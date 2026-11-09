# Watar — website + Saudi voice receptionist (سارا)

One server that hosts:

- **The website** with the live "talk in browser" demo (`/`, `/ws/web`)
- **The phone line** for Twilio (`/twiml/pt` → `/ws/pt/...`)
- **The clinic booking system** — specialties, doctors and monthly slots (private, inside the server)

Phone calls and website calls share the same prompt (`agent/prompts/`) and the same booking tools.

```
agent/            Gemini Live voice agent + website
  prompts/        system_prompt.txt, greeting.txt  ← what سارا says
  website/        the site
clinic-adapter/   doctors + slots database (see clinic-adapter/README.md)
  data/           clinics.csv, doctors.csv, leaves.csv  ← edit doctors here
```

## Deploy on Render

1. In Render: **New → Blueprint**, pick this repo. It reads `render.yaml`.
2. Paste your **GEMINI_API_KEY** when Render asks (it is never stored in GitHub).
3. Deploy. The site will be at `https://watar-website.onrender.com` (or similar).

Every `git push` to `main` redeploys automatically.

**Twilio:** set the number's Voice webhook to `https://<your-render-address>/twiml/pt` (POST).

**Before sharing publicly:** in Render → Environment add
`ALLOWED_ORIGINS=https://<your-render-address>`, and set `previewFallback: false` in
`agent/website/assets/js/config.js`.

### Free plan notes

- The server sleeps after 15 minutes without visitors; the first visit after that takes about a minute.
- The disk is reset on every deploy/restart: doctors and slots are rebuilt from the CSV files,
  but **demo bookings are lost**. For real bookings use a paid plan with a persistent disk
  (set `CLINIC_DB=/var/data/clinic.db`) or connect the clinic's real system.

## Run locally

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key
./start.sh            # open http://localhost:8080
```
