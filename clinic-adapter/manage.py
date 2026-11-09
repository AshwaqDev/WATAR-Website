#!/usr/bin/env python3
"""
Staff command line for the clinic schedule.

  python manage.py sync              reload data/*.csv → doctors, schedules, leaves; rebuild future free slots
  python manage.py generate          add any missing slots for this month + next month
  python manage.py generate 2027-01  add slots for a specific month
  python manage.py summary           specialties, number of doctors, free slots, last day covered
  python manage.py slots الأسنان      next free slots for one specialty

The adapter (python main.py) already re-syncs by itself when a CSV file is saved and
tops up next month every few hours, so these are only needed for checking or for
running without the adapter (e.g. a monthly cron job).
"""
import sys

import clinic_db as cdb


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "summary"
    cdb.init_db()

    if cmd == "sync":
        try:
            r = cdb.sync()
        except ValueError as e:
            print(f"❌ {e}")
            return 1
        print(f"✓ {r['clinics']} specialties, {r['doctors']} doctors, {r['shifts']} weekly shifts, "
              f"{r['leaves']} leaves → {r['slots_added']} free slots built")
        for c in r["conflicts"]:
            print(f"⚠️  {c['confirmation_number']} {c['date']} {c['time']} — {c['doctor']} ({c['reason']}): "
                  f"call {c['patient']} {c['phone']} to rebook")
        return 0

    if cmd == "generate":
        if len(argv) > 2:
            y, m = map(int, argv[2].split("-"))
            with cdb.get_db() as db:
                n = cdb.generate_month(db, y, m)
        else:
            n = cdb.ensure_months()
        print(f"✓ {n} new slots added")
        return 0

    if cmd == "summary":
        s = cdb.summary()
        print(f"Today {s['today']} | last sync {s['last_sync']} | last top-up {s['last_generate']}")
        for c in s["clinics"]:
            print(f"  {c['name']:<28} doctors={c['doctors']:<3} free={c['free_slots']:<5} until {c['last_day']}")
        return 0

    if cmd == "slots" and len(argv) > 2:
        want = cdb.norm(" ".join(argv[2:]))
        with cdb.get_db() as db:
            rows = db.execute("""
                SELECT c.name AS clinic, d.name AS doctor, s.date, s.time FROM slots s
                JOIN doctors d ON d.id=s.doctor_id JOIN clinics c ON c.id=s.clinic_id
                WHERE s.booked=0 AND s.date > ? AND d.active=1 ORDER BY s.date, s.time""",
                (cdb.today_local().isoformat(),)).fetchall()
        rows = [r for r in rows if want in cdb.norm(r["clinic"])][:15]
        for r in rows:
            print(f"  {r['date']} {r['time']}  {r['doctor']}  ({r['clinic']})")
        if not rows:
            print("no free slots found")
        return 0

    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
