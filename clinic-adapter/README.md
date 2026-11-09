# General Clinic Demo Adapter

Booking backend for the multi-specialty clinic voice agent (سارا). It holds the
specialties, the doctors and their free slots, and speaks the Watar Adapter Contract v1.

```bash
cd ~/Downloads/watar-ai-main/clinic-demo-adapter
python main.py            # port 3003, key: clinic-demo-key-2026
```

## Adding or changing doctors

Edit the files in `data/` (Excel works — save as **CSV UTF-8**):

| File | One row per | Columns |
|---|---|---|
| `clinics.csv` | specialty | `name`, `aliases` (other words callers use, separated by `\|`) |
| `doctors.csv` | doctor **shift** | `doctor`, `gender` (ذكر/أنثى), `clinic`, `days`, `start`, `end`, `slot_minutes` |
| `leaves.csv` | leave / holiday | `doctor`, `from`, `to` (YYYY-MM-DD), `note` |

- `days`: `الأحد-الخميس` (a range), or `الأحد|الثلاثاء|الخميس`, or `sun|tue`.
- A doctor with a morning and an evening shift gets two rows.
- `clinic` must match a `name` in `clinics.csv`.
- Removing a doctor's row deactivates them (their history stays).

While the adapter is running it notices a saved CSV within a minute and re-syncs by itself.
Or run it yourself:

```bash
python manage.py sync
```

If the sync finds a mistake (unknown clinic, bad time, …) it lists the CSV line and changes nothing.

## Monthly slots — automatic

Slots are built from the weekly shifts for **this month + next month**. Every 6 hours the adapter
adds any missing ones, so when December starts, January is created on its own.

- Booked slots are never deleted or moved.
- Changing a shift or adding a leave rebuilds only *future, free* slots.
- If a doctor is removed or put on leave while patients are booked, the sync prints those
  appointments (patient name + phone) so reception can call them to rebook.

Without the adapter running (e.g. a monthly cron job): `python manage.py generate`.

## Checking

```bash
python manage.py summary          # doctors and free slots per specialty, last day covered
python manage.py slots الأسنان     # next free slots in one specialty
```

API extras: `POST /admin/sync`, `GET /admin/summary`, `GET /debug/appointments` (header `X-Watar-Key`).
`GET /watar/v1/slots/available` also accepts optional `date`, `from_date`, `limit`, and works without
`doctor_id` (= any doctor in that clinic).
