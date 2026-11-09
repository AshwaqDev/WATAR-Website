"""
General multi-specialty clinic — database + monthly schedule logic
==================================================================
Shared by main.py (the adapter API) and manage.py (the staff command line).

Where the data comes from (staff edit these, e.g. in Excel → Save as CSV UTF-8):
  data/clinics.csv   one row per specialty      : name, aliases
  data/doctors.csv   one row per doctor shift   : doctor, gender, clinic, days, start, end, slot_minutes
  data/leaves.csv    doctor holidays / leave    : doctor, from, to, note

How slots stay up to date every month:
  • `sync()` reloads the three CSV files into the DB and rebuilds all FUTURE,
    UNBOOKED slots for the current month + next month. Booked slots are never touched.
  • `ensure_months()` only ADDS missing slots for the current + next month. The adapter
    runs it automatically every few hours, so when a new month starts the month after it
    is generated on its own — nobody has to remember.
"""
import csv
import logging
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo(os.getenv("CLINIC_TZ", "Asia/Riyadh"))
except Exception:  # pragma: no cover
    TZ = None

logger = logging.getLogger("clinic-adapter")

BASE_DIR = Path(__file__).parent
DB_PATH = Path(os.getenv("CLINIC_DB", BASE_DIR / "clinic_demo.db"))
DATA_DIR = Path(os.getenv("CLINIC_DATA_DIR", BASE_DIR / "data"))
MONTHS_AHEAD = int(os.getenv("CLINIC_MONTHS_AHEAD", "1"))  # current month + N more


def now_local() -> datetime:
    return datetime.now(TZ) if TZ else datetime.now()


def today_local() -> date:
    return now_local().date()


# ============================================================
#  Arabic text normalisation (so "اسنان" == "الأسنان", "جلديه" == "الجلدية")
# ============================================================
_DIACRITICS = re.compile(r"[ؗ-ًؚ-ْـ]")


def norm(text: str) -> str:
    t = _DIACRITICS.sub("", (text or "").strip().lower())
    t = re.sub("[أإآٱ]", "ا", t).replace("ة", "ه").replace("ى", "ي").replace("ؤ", "و").replace("ئ", "ي")
    words = []
    for w in t.split():
        if w.startswith("وال") and len(w) > 4:
            w = w[3:]
        elif w.startswith("ال") and len(w) > 3:
            w = w[2:]
        words.append(w)
    return " ".join(words)


# Weekday numbers follow Python: Monday=0 … Sunday=6
_DAY_NAMES = {
    "اثنين": 0, "ثنين": 0, "mon": 0, "monday": 0,
    "ثلاثا": 1, "ثلاثاء": 1, "tue": 1, "tuesday": 1,
    "اربعا": 2, "اربعاء": 2, "wed": 2, "wednesday": 2,
    "خميس": 3, "thu": 3, "thursday": 3,
    "جمعه": 4, "fri": 4, "friday": 4,
    "سبت": 5, "sat": 5, "saturday": 5,
    "احد": 6, "sun": 6, "sunday": 6,
}
# Saudi week order, used to expand ranges like "الأحد-الخميس"
_WEEK_ORDER = [6, 0, 1, 2, 3, 4, 5]


def _day_num(word: str) -> int:
    w = norm(word)
    if w.startswith("يوم "):
        w = w[4:]
    if w not in _DAY_NAMES:
        raise ValueError(f"unknown day name: {word!r}")
    return _DAY_NAMES[w]


def parse_days(text: str) -> list:
    """'الأحد-الخميس' / 'الأحد|الثلاثاء' / 'sun,tue' → sorted weekday numbers."""
    days = set()
    for part in re.split(r"[|،,;/+]+", text or ""):
        part = part.strip()
        if not part:
            continue
        if "-" in part or "–" in part or " الى " in f" {norm(part)} ":
            a, b = re.split(r"\s*(?:-|–|إلى|الى)\s*", part, maxsplit=1)
            i, j = _WEEK_ORDER.index(_day_num(a)), _WEEK_ORDER.index(_day_num(b))
            rng = _WEEK_ORDER[i:j + 1] if i <= j else _WEEK_ORDER[i:] + _WEEK_ORDER[:j + 1]
            days.update(rng)
        else:
            days.add(_day_num(part))
    if not days:
        raise ValueError("no days given")
    return sorted(days)


def _hhmm(text: str) -> str:
    h, m = (text or "").strip().split(":")[:2]
    return f"{int(h):02d}:{int(m):02d}"


# ============================================================
#  DB
# ============================================================
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS patients (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                phone         TEXT NOT NULL,
                national_id   TEXT,
                gender        TEXT DEFAULT 'unknown',
                age           INTEGER,
                guardian_name TEXT
            );

            -- specialties (الطب العام، الأطفال، الأسنان، ...)
            CREATE TABLE IF NOT EXISTS clinics (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL UNIQUE,
                aliases TEXT DEFAULT '',
                active  INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS doctors (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT NOT NULL UNIQUE,
                clinic_id INTEGER REFERENCES clinics(id),
                gender    TEXT DEFAULT 'unknown',
                active    INTEGER DEFAULT 1
            );

            -- weekly template: a doctor can have several shifts
            CREATE TABLE IF NOT EXISTS doctor_schedules (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id    INTEGER NOT NULL REFERENCES doctors(id),
                weekday      INTEGER NOT NULL,          -- Monday=0 … Sunday=6
                start_time   TEXT NOT NULL,             -- 'HH:MM'
                end_time     TEXT NOT NULL,             -- 'HH:MM' (last slot ends here)
                slot_minutes INTEGER NOT NULL DEFAULT 20
            );

            CREATE TABLE IF NOT EXISTS doctor_leaves (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER NOT NULL REFERENCES doctors(id),
                from_date TEXT NOT NULL,
                to_date   TEXT NOT NULL,
                note      TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS slots (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER REFERENCES doctors(id),
                clinic_id INTEGER REFERENCES clinics(id),
                date      TEXT NOT NULL,
                time      TEXT NOT NULL,
                booked    INTEGER DEFAULT 0,
                UNIQUE (doctor_id, date, time)
            );
            CREATE INDEX IF NOT EXISTS idx_slots_lookup ON slots (clinic_id, booked, date, time);

            CREATE TABLE IF NOT EXISTS appointments (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id          INTEGER REFERENCES patients(id),
                clinic_id           INTEGER REFERENCES clinics(id),
                doctor_id           INTEGER REFERENCES doctors(id),
                slot_id             INTEGER REFERENCES slots(id),
                appointment_date    TEXT,
                appointment_time    TEXT,
                status              TEXT DEFAULT 'confirmed',
                confirmation_number TEXT
            );

            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
        """)


# ============================================================
#  CSV import
# ============================================================
def _read_csv(name: str) -> list:
    path = DATA_DIR / name
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig", newline="") as f:  # utf-8-sig: Excel adds a BOM
        rows = []
        for i, row in enumerate(csv.DictReader(f), start=2):
            row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            if any(row.values()) and not next(iter(row.values()), "").startswith("#"):
                row["_line"] = i
                rows.append(row)
        return rows


def data_files_mtime() -> float:
    return max((p.stat().st_mtime for p in DATA_DIR.glob("*.csv")), default=0.0)


def _gender(text: str) -> str:
    t = norm(text)
    if t in ("m", "male", "ذكر", "رجل", "دكتور"):
        return "male"
    if t in ("f", "female", "انثي", "امراه", "دكتوره"):
        return "female"
    return "unknown"


def import_csv(db) -> dict:
    """Load data/*.csv into clinics / doctors / schedules / leaves. Raises on bad rows."""
    errors = []

    # ── clinics ─────────────────────────────────────────────
    clinic_rows = _read_csv("clinics.csv")
    clinic_names = []
    for r in clinic_rows:
        name = r.get("name", "")
        if not name:
            continue
        clinic_names.append(name)
        db.execute("""INSERT INTO clinics (name, aliases, active) VALUES (?,?,1)
                      ON CONFLICT(name) DO UPDATE SET aliases=excluded.aliases, active=1""",
                   (name, r.get("aliases", "")))

    # ── doctors + weekly shifts ─────────────────────────────
    doctor_rows = _read_csv("doctors.csv")
    clinic_by_norm = {norm(r["name"]): r["id"] for r in db.execute("SELECT id, name FROM clinics")}
    shifts = []          # (doctor_name, weekday, start, end, minutes)
    doctors = {}         # name → (clinic_id, gender)
    for r in doctor_rows:
        line = r["_line"]
        name = r.get("doctor", "")
        clinic_id = clinic_by_norm.get(norm(r.get("clinic", "")))
        if not name:
            errors.append(f"doctors.csv line {line}: missing doctor name"); continue
        if not clinic_id:
            errors.append(f"doctors.csv line {line}: clinic {r.get('clinic')!r} is not in clinics.csv"); continue
        try:
            days = parse_days(r.get("days", ""))
            start, end = _hhmm(r.get("start", "")), _hhmm(r.get("end", ""))
            minutes = int(r.get("slot_minutes") or 20)
            if start >= end or minutes < 5:
                raise ValueError("start must be before end, slot_minutes ≥ 5")
        except Exception as e:
            errors.append(f"doctors.csv line {line} ({name}): {e}"); continue
        if name in doctors and doctors[name][0] != clinic_id:
            errors.append(f"doctors.csv line {line}: {name} is listed under two clinics"); continue
        doctors[name] = (clinic_id, _gender(r.get("gender", "")))
        shifts += [(name, d, start, end, minutes) for d in days]

    # ── leaves ──────────────────────────────────────────────
    leaves = []
    for r in _read_csv("leaves.csv"):
        line, name = r["_line"], r.get("doctor", "")
        if name not in doctors:
            errors.append(f"leaves.csv line {line}: doctor {name!r} is not in doctors.csv"); continue
        try:
            f = datetime.strptime(r.get("from", ""), "%Y-%m-%d").date()
            t = datetime.strptime(r.get("to") or r.get("from", ""), "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"leaves.csv line {line}: dates must look like 2026-12-01"); continue
        leaves.append((name, f.isoformat(), t.isoformat(), r.get("note", "")))

    if errors:
        raise ValueError("Fix these rows in the CSV files, then sync again:\n  - " + "\n  - ".join(errors))

    # ── write (only after everything validated) ─────────────
    if clinic_names:
        q = ",".join("?" * len(clinic_names))
        db.execute(f"UPDATE clinics SET active=0 WHERE name NOT IN ({q})", clinic_names)
    db.execute("UPDATE doctors SET active=0")
    for name, (clinic_id, gender) in doctors.items():
        db.execute("""INSERT INTO doctors (name, clinic_id, gender, active) VALUES (?,?,?,1)
                      ON CONFLICT(name) DO UPDATE SET clinic_id=excluded.clinic_id,
                                                      gender=excluded.gender, active=1""",
                   (name, clinic_id, gender))
    doc_id = {r["name"]: r["id"] for r in db.execute("SELECT id, name FROM doctors")}
    db.execute("DELETE FROM doctor_schedules")
    db.executemany("INSERT INTO doctor_schedules (doctor_id, weekday, start_time, end_time, slot_minutes) "
                   "VALUES (?,?,?,?,?)", [(doc_id[n], d, s, e, m) for n, d, s, e, m in shifts])
    db.execute("DELETE FROM doctor_leaves")
    db.executemany("INSERT INTO doctor_leaves (doctor_id, from_date, to_date, note) VALUES (?,?,?,?)",
                   [(doc_id[n], f, t, note) for n, f, t, note in leaves])
    return {"clinics": len(clinic_names), "doctors": len(doctors), "shifts": len(shifts), "leaves": len(leaves)}


# ============================================================
#  Slot generation
# ============================================================
def _month_range(year: int, month: int):
    first = date(year, month, 1)
    nxt = date(year + (month == 12), month % 12 + 1, 1)
    return first, nxt - timedelta(days=1)


def _months_to_cover() -> list:
    t = today_local()
    out, y, m = [], t.year, t.month
    for _ in range(MONTHS_AHEAD + 1):
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def _times(start: str, end: str, minutes: int) -> list:
    cur = datetime.strptime(start, "%H:%M")
    stop = datetime.strptime(end, "%H:%M")
    out = []
    while cur + timedelta(minutes=minutes) <= stop:
        out.append(cur.strftime("%H:%M"))
        cur += timedelta(minutes=minutes)
    return out


def generate_month(db, year: int, month: int, rebuild: bool = False) -> int:
    """Create slots for one month from the weekly schedules. Returns slots added.

    rebuild=True first deletes the month's FUTURE, UNBOOKED slots (so schedule
    changes and new leaves take effect). Booked slots are always kept."""
    first, last = _month_range(year, month)
    start_day = max(first, today_local() + timedelta(days=1))  # never create slots for today/past
    if start_day > last:
        return 0
    if rebuild:
        db.execute("DELETE FROM slots WHERE booked=0 AND date BETWEEN ? AND ?",
                   (start_day.isoformat(), last.isoformat()))

    schedules = db.execute("""
        SELECT s.doctor_id, d.clinic_id, s.weekday, s.start_time, s.end_time, s.slot_minutes
        FROM doctor_schedules s JOIN doctors d ON d.id = s.doctor_id
        JOIN clinics c ON c.id = d.clinic_id
        WHERE d.active = 1 AND c.active = 1""").fetchall()
    leaves = {}
    for r in db.execute("SELECT doctor_id, from_date, to_date FROM doctor_leaves"):
        leaves.setdefault(r["doctor_id"], []).append((r["from_date"], r["to_date"]))

    rows = []
    day = start_day
    while day <= last:
        iso, wd = day.isoformat(), day.weekday()
        for s in schedules:
            if s["weekday"] != wd:
                continue
            if any(f <= iso <= t for f, t in leaves.get(s["doctor_id"], [])):
                continue
            rows += [(s["doctor_id"], s["clinic_id"], iso, tm)
                     for tm in _times(s["start_time"], s["end_time"], s["slot_minutes"])]
        day += timedelta(days=1)

    before = db.total_changes
    db.executemany("INSERT OR IGNORE INTO slots (doctor_id, clinic_id, date, time) VALUES (?,?,?,?)", rows)
    return db.total_changes - before


def ensure_months() -> int:
    """Add any missing slots for the current + next month(s). Safe to run any time."""
    with get_db() as db:
        added = sum(generate_month(db, y, m) for y, m in _months_to_cover())
        db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('last_generate', ?)",
                   (now_local().isoformat(timespec="seconds"),))
    if added:
        logger.info(f"Monthly schedule: added {added} new slots")
    return added


def conflicts(db) -> list:
    """Booked future appointments that no longer fit the schedule (doctor removed, on leave, …)."""
    t = today_local().isoformat()
    rows = db.execute("""
        SELECT a.confirmation_number, a.appointment_date, a.appointment_time, d.name AS doctor,
               d.active, d.id AS doctor_id, p.name AS patient, p.phone
        FROM appointments a JOIN doctors d ON d.id=a.doctor_id JOIN patients p ON p.id=a.patient_id
        WHERE a.status='confirmed' AND a.appointment_date > ?""", (t,)).fetchall()
    out = []
    for r in rows:
        on_leave = db.execute("SELECT 1 FROM doctor_leaves WHERE doctor_id=? AND ? BETWEEN from_date AND to_date",
                              (r["doctor_id"], r["appointment_date"])).fetchone()
        if not r["active"] or on_leave:
            out.append({"confirmation_number": r["confirmation_number"], "date": r["appointment_date"],
                        "time": r["appointment_time"], "doctor": r["doctor"], "patient": r["patient"],
                        "phone": r["phone"], "reason": "doctor removed" if not r["active"] else "doctor on leave"})
    return out


def sync() -> dict:
    """Reload CSV files and rebuild future unbooked slots. Returns a summary."""
    init_db()
    with get_db() as db:
        counts = import_csv(db)
        counts["slots_added"] = sum(generate_month(db, y, m, rebuild=True) for y, m in _months_to_cover())
        counts["conflicts"] = conflicts(db)
        db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('last_sync', ?)",
                   (now_local().isoformat(timespec="seconds"),))
        db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('data_mtime', ?)",
                   (str(data_files_mtime()),))
    logger.info(f"Sync done: {counts['clinics']} clinics, {counts['doctors']} doctors, "
                f"{counts['slots_added']} slots (re)built, {len(counts['conflicts'])} conflicts")
    for c in counts["conflicts"]:
        logger.warning(f"⚠️  Appointment {c['confirmation_number']} on {c['date']} {c['time']} with "
                       f"{c['doctor']} — {c['reason']}. Call {c['patient']} to rebook.")
    return counts


def meta(key: str):
    with get_db() as db:
        r = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return r["value"] if r else None


def summary() -> dict:
    with get_db() as db:
        clinics = db.execute("""
            SELECT c.name,
                   (SELECT COUNT(*) FROM doctors d WHERE d.clinic_id=c.id AND d.active=1) AS doctors,
                   (SELECT COUNT(*) FROM slots s WHERE s.clinic_id=c.id AND s.booked=0 AND s.date > ?) AS free_slots,
                   (SELECT MAX(date) FROM slots s WHERE s.clinic_id=c.id) AS last_day
            FROM clinics c WHERE c.active=1 ORDER BY c.id""", (today_local().isoformat(),)).fetchall()
    return {"today": today_local().isoformat(), "last_sync": meta("last_sync"),
            "last_generate": meta("last_generate"), "clinics": [dict(r) for r in clinics]}
