#!/usr/bin/env python3
"""
General Multi-Specialty Clinic — DEMO Adapter (Watar Adapter Contract v1)
=========================================================================
Specialties (الطب العام، الأطفال، الأسنان، العظام، النساء والولادة، الجلدية،
أنف وأذن وحنجرة، ...), their doctors and bookable slots live in SQLite.

Doctors + weekly schedules are kept in data/*.csv (see README.md). Slots are generated
from those schedules for the current month + next month, and topped up automatically
every few hours — so a new month always has slots without anyone touching the system.

Run:
    pip install -r requirements.txt
    python main.py                 # default port 3003
Auth:
    Header  X-Watar-Key: clinic-demo-key-2026   (override with WATAR_KEY)
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request

import clinic_db as cdb
from clinic_db import get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [CLINIC-ADAPTER] %(message)s")
logger = logging.getLogger("clinic-adapter")

WATAR_KEY = os.getenv("WATAR_KEY", "clinic-demo-key-2026")
ADMIN_KEY = os.getenv("ADMIN_KEY", WATAR_KEY)
REFRESH_SECONDS = int(os.getenv("REFRESH_SECONDS", "21600"))   # 6 h: top up next month's slots
WATCH_SECONDS = int(os.getenv("WATCH_SECONDS", "60"))          # re-sync when a CSV file is saved


def _sync_if_csv_changed():
    if str(cdb.data_files_mtime()) != (cdb.meta("data_mtime") or ""):
        logger.info("CSV files changed → syncing doctors and schedules")
        try:
            cdb.sync()
        except ValueError as e:
            logger.error(str(e))


async def _background_refresh():
    last_generate = 0.0
    while True:
        try:
            _sync_if_csv_changed()
            if asyncio.get_running_loop().time() - last_generate >= REFRESH_SECONDS:
                cdb.ensure_months()
                last_generate = asyncio.get_running_loop().time()
        except Exception as e:  # never let the loop die
            logger.error(f"background refresh failed: {e}")
        await asyncio.sleep(WATCH_SECONDS)


@asynccontextmanager
async def lifespan(_app):
    cdb.init_db()
    try:
        cdb.sync()
    except ValueError as e:
        logger.error(str(e))
        logger.error("Starting with the data already in the database.")
    task = asyncio.create_task(_background_refresh())
    yield
    task.cancel()


app = FastAPI(title="General Clinic Demo Adapter", lifespan=lifespan)


def _check_auth(key: str, admin: bool = False):
    if key != (ADMIN_KEY if admin else WATAR_KEY):
        raise HTTPException(status_code=401, detail="Invalid X-Watar-Key")


@app.get("/health")
def health():
    return {"status": "ok", "mode": "clinic-demo-adapter", "db": str(cdb.DB_PATH),
            "last_sync": cdb.meta("last_sync")}


# ── Patient ───────────────────────────────────────────────────
@app.get("/watar/v1/patients")
def get_patient(phone: str, x_watar_key: str = Header("")):
    _check_auth(x_watar_key)
    with get_db() as db:
        row = db.execute("SELECT * FROM patients WHERE phone=? ORDER BY id LIMIT 1", (phone,)).fetchone()
    if row:
        return {"found": True, "patient": {"id": row["id"], "name": row["name"], "gender": row["gender"]}}
    return {"found": False}


@app.post("/watar/v1/patients/register")
async def register_patient(req: Request, x_watar_key: str = Header("")):
    _check_auth(x_watar_key)
    b = await req.json()
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO patients (name, phone, national_id, gender, age, guardian_name) VALUES (?,?,?,?,?,?)",
            (b.get("name", ""), b.get("phone", ""), b.get("national_id", ""),
             b.get("gender", "unknown") or "unknown", b.get("age"), b.get("guardian_name")))
        new_id = cur.lastrowid
    logger.info(f"Patient registered id={new_id}")
    return {"patient": {"id": new_id, "name": b.get("name", ""), "gender": b.get("gender", "unknown")}}


@app.put("/watar/v1/patients/{patient_id}")
async def update_patient(patient_id: int, req: Request, x_watar_key: str = Header("")):
    _check_auth(x_watar_key)
    b = await req.json()
    with get_db() as db:
        if "name" in b:
            db.execute("UPDATE patients SET name=? WHERE id=?", (b["name"], patient_id))
        if "national_id" in b:
            db.execute("UPDATE patients SET national_id=? WHERE id=?", (b["national_id"], patient_id))
    return {"success": True}


# ── Clinics (specialties) & Doctors ───────────────────────────
@app.get("/watar/v1/clinics")
def get_clinics(x_watar_key: str = Header("")):
    _check_auth(x_watar_key)
    with get_db() as db:
        rows = db.execute("SELECT id, name, aliases FROM clinics WHERE active=1 ORDER BY id").fetchall()
    return {"data": [{"id": r["id"], "name": r["name"],
                      "aliases": [a.strip() for a in (r["aliases"] or "").split("|") if a.strip()]}
                     for r in rows]}


@app.get("/watar/v1/doctors")
def get_doctors(clinic_id: int = None, x_watar_key: str = Header("")):
    _check_auth(x_watar_key)
    sql = "SELECT id, name, clinic_id, gender FROM doctors WHERE active=1"
    args = ()
    if clinic_id:
        sql += " AND clinic_id=?"
        args = (clinic_id,)
    with get_db() as db:
        rows = db.execute(sql + " ORDER BY id", args).fetchall()
    return {"data": [dict(r) for r in rows]}


# ── Slots ─────────────────────────────────────────────────────
@app.get("/watar/v1/slots/available")
def get_slots(clinic_id: int, doctor_id: int = None, date: str = None, from_date: str = None,
              limit: int = 10, x_watar_key: str = Header("")):
    """Contract v1 + optional extensions:
       doctor_id omitted → any doctor in the clinic (earliest first)
       date=YYYY-MM-DD   → only that day;  from_date=YYYY-MM-DD → that day onwards"""
    _check_auth(x_watar_key)
    now = cdb.now_local()
    today, now_hm = now.date().isoformat(), now.strftime("%H:%M")
    sql = """SELECT s.id, s.date, s.time, s.doctor_id, d.name AS doctor_name, d.gender AS doctor_gender
             FROM slots s JOIN doctors d ON d.id = s.doctor_id
             WHERE s.clinic_id=? AND s.booked=0 AND d.active=1
               AND (s.date > ? OR (s.date = ? AND s.time > ?))"""
    args = [clinic_id, today, today, now_hm]
    if doctor_id:
        sql += " AND s.doctor_id=?"; args.append(doctor_id)
    if date:
        sql += " AND s.date=?"; args.append(date)
    elif from_date:
        sql += " AND s.date>=?"; args.append(from_date)
    sql += " ORDER BY s.date, s.time, s.doctor_id LIMIT ?"
    args.append(max(1, min(limit, 100)))
    with get_db() as db:
        rows = db.execute(sql, args).fetchall()
    logger.info(f"Slots clinic={clinic_id} doctor={doctor_id} date={date or from_date} → {len(rows)}")
    return {"data": [dict(r) for r in rows]}


# ── Appointments ──────────────────────────────────────────────
@app.post("/watar/v1/appointments")
async def create_appointment(req: Request, x_watar_key: str = Header("")):
    _check_auth(x_watar_key)
    b = await req.json()
    slot_id = b.get("slot_id")
    with get_db() as db:
        slot = db.execute("SELECT date, time, doctor_id, clinic_id FROM slots WHERE id=?", (slot_id,)).fetchone()
        if not slot:
            raise HTTPException(404, "Slot not found")
        # atomic claim — two callers can't take the same slot
        if db.execute("UPDATE slots SET booked=1 WHERE id=? AND booked=0", (slot_id,)).rowcount == 0:
            raise HTTPException(409, "Slot already booked")
        conf = f"CL-{int(datetime.utcnow().timestamp())}{slot_id % 100:02d}"
        cur = db.execute("""
            INSERT INTO appointments (patient_id, clinic_id, doctor_id, slot_id,
                                      appointment_date, appointment_time, status, confirmation_number)
            VALUES (?,?,?,?,?,?,'confirmed',?)""",
            (b.get("patient_id"), slot["clinic_id"], slot["doctor_id"], slot_id,
             slot["date"], slot["time"], conf))
        apt_id = cur.lastrowid
    logger.info(f"Appointment CREATED id={apt_id} conf={conf}")
    return {"data": {"id": apt_id, "confirmation_number": conf}}


def _patient_appointments(patient_id: int):
    with get_db() as db:
        rows = db.execute("""
            SELECT a.id, a.appointment_date, a.appointment_time, a.doctor_id, a.clinic_id,
                   a.confirmation_number, d.name AS doctor_name, c.name AS clinic_name
            FROM appointments a JOIN doctors d ON a.doctor_id=d.id JOIN clinics c ON a.clinic_id=c.id
            WHERE a.patient_id=? AND a.status='confirmed' AND a.appointment_date >= ?
            ORDER BY a.appointment_date, a.appointment_time""",
            (patient_id, cdb.today_local().isoformat())).fetchall()
    return [{"id": r["id"], "appointment_date": r["appointment_date"],
             "appointment_time": r["appointment_time"], "doctor_id": r["doctor_id"],
             "clinic_id": r["clinic_id"], "confirmation_number": r["confirmation_number"],
             "doctor": {"name": r["doctor_name"]}, "clinic": {"name": r["clinic_name"]}} for r in rows]


@app.get("/watar/v1/appointments/patient")
def get_patient_appointments(patient_id: int, x_watar_key: str = Header("")):
    _check_auth(x_watar_key)
    data = _patient_appointments(patient_id)
    return {"count": len(data), "data": data}


@app.get("/watar/v1/appointments/cancellable")
def get_cancellable(patient_id: int, x_watar_key: str = Header("")):
    _check_auth(x_watar_key)
    return {"data": _patient_appointments(patient_id)}


@app.put("/watar/v1/appointments/{apt_id}/cancel")
def cancel_appointment(apt_id: int, x_watar_key: str = Header("")):
    _check_auth(x_watar_key)
    with get_db() as db:
        row = db.execute("SELECT slot_id FROM appointments WHERE id=? AND status='confirmed'", (apt_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Appointment not found")
        db.execute("UPDATE appointments SET status='cancelled' WHERE id=?", (apt_id,))
        db.execute("UPDATE slots SET booked=0 WHERE id=?", (row["slot_id"],))
    logger.info(f"Appointment CANCELLED id={apt_id}")
    return {"success": True}


@app.put("/watar/v1/appointments/{apt_id}/reschedule")
async def reschedule_appointment(apt_id: int, req: Request, x_watar_key: str = Header("")):
    _check_auth(x_watar_key)
    new_slot_id = (await req.json()).get("new_slot_id")
    with get_db() as db:
        old = db.execute("SELECT slot_id FROM appointments WHERE id=? AND status='confirmed'", (apt_id,)).fetchone()
        new = db.execute("SELECT date, time, doctor_id, clinic_id FROM slots WHERE id=?", (new_slot_id,)).fetchone()
        if not old or not new:
            raise HTTPException(404, "Not found")
        if db.execute("UPDATE slots SET booked=1 WHERE id=? AND booked=0", (new_slot_id,)).rowcount == 0:
            raise HTTPException(409, "New slot already booked")
        db.execute("UPDATE slots SET booked=0 WHERE id=?", (old["slot_id"],))
        db.execute("""UPDATE appointments SET slot_id=?, appointment_date=?, appointment_time=?,
                      doctor_id=?, clinic_id=? WHERE id=?""",
                   (new_slot_id, new["date"], new["time"], new["doctor_id"], new["clinic_id"], apt_id))
    logger.info(f"Appointment RESCHEDULED id={apt_id} new_slot={new_slot_id}")
    return {"success": True}


# ── Admin (staff / scheduler) ─────────────────────────────────
@app.post("/admin/sync")
def admin_sync(x_watar_key: str = Header("")):
    """Re-read data/*.csv and rebuild future unbooked slots (same as `python manage.py sync`)."""
    _check_auth(x_watar_key, admin=True)
    try:
        return cdb.sync()
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/admin/summary")
def admin_summary(x_watar_key: str = Header("")):
    _check_auth(x_watar_key, admin=True)
    return cdb.summary()


@app.get("/debug/appointments")
def debug_appointments(x_watar_key: str = Header("")):
    _check_auth(x_watar_key, admin=True)
    with get_db() as db:
        rows = db.execute("""
            SELECT a.id, a.patient_id, p.name AS patient, a.appointment_date, a.appointment_time, a.status,
                   d.name AS doctor, c.name AS clinic, a.confirmation_number
            FROM appointments a JOIN doctors d ON a.doctor_id=d.id JOIN clinics c ON a.clinic_id=c.id
            LEFT JOIN patients p ON p.id=a.patient_id ORDER BY a.id DESC LIMIT 30""").fetchall()
    return {"appointments": [dict(r) for r in rows]}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3003"))
    logger.info(f"General clinic demo adapter on port {port} | DB: {cdb.DB_PATH}")
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=port)
