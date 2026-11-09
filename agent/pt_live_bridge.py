#!/usr/bin/env python3
"""
General clinic — Real-time Gemini Live ↔ Twilio bridge, wired to the DEMO adapter
=================================================================================
(File name kept as pt_live_bridge.py so web_bridge.py and existing commands keep working.
 The previous physical-therapy version is saved as pt_live_bridge.pt-clinic.py.)

Real-time Saudi voice receptionist for a multi-specialty clinic (الطب العام، الأطفال،
الأسنان، العظام، النساء والولادة، الجلدية، أنف وأذن وحنجرة، ...). Function calls hit the
clinic adapter's Watar contract — real doctors and slots from its database.

Prereqs (two terminals):
  1) clinic adapter: cd clinic-demo-adapter && python main.py      # port 3003
  2) this bridge:    cd gemini-live-test && source venv/bin/activate
     export GEMINI_API_KEY=your_key
     uvicorn web_bridge:app --host 0.0.0.0 --port 8080
  3) ngrok http 8080  → set Twilio Voice webhook to  https://<ngrok>/twiml/pt

When the clinic integrates for real, only CLINIC_ADAPTER_URL/KEY change — the tools,
prompt, and audio bridge stay the same.
"""
import asyncio
import audioop
import base64
import json
import os
import time

from datetime import datetime, timedelta
import re

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import PlainTextResponse
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
# native-audio can't do tools; 3.1-flash-live supports audio + function calling.
MODEL = os.environ.get("GEMINI_LIVE_MODEL", "gemini-3.1-flash-live-preview")

ADAPTER_URL = os.environ.get("CLINIC_ADAPTER_URL") or os.environ.get("PT_ADAPTER_URL", "http://localhost:3003")
ADAPTER_KEY = os.environ.get("CLINIC_ADAPTER_KEY") or os.environ.get("PT_ADAPTER_KEY", "clinic-demo-key-2026")

# Gemini Live built-in voice. Female: Kore, Aoede, Leda. Male: Charon, Puck, Fenrir, Orus.
# Default = a FEMALE voice. The Saudi DIALECT comes from the prompt, not the voice.
VOICE = os.environ.get("GEMINI_VOICE", "Kore")

GEMINI_IN_SR, GEMINI_OUT_SR, TWILIO_SR, TWILIO_FRAME = 16000, 24000, 8000, 160

# ------------------------------------------------------------
#  Agent prompt + greeting live in ./prompts/ and are shared by the
#  phone line (this file) and the website demo (web_bridge.py).
#  They are re-read at the start of EVERY call, so edits apply on the
#  next call without restarting the server.
# ------------------------------------------------------------
from pathlib import Path as _Path

PROMPTS_DIR = _Path(os.environ.get("PROMPTS_DIR", _Path(__file__).parent / "prompts"))
_prompt_cache = {}


def _read_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    try:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError("file is empty")
        _prompt_cache[name] = text
        return text
    except Exception as e:
        if name in _prompt_cache:  # keep calls working if the file is mid-edit
            print(f"⚠️  could not read {path} ({e}); using the last good version")
            return _prompt_cache[name]
        raise RuntimeError(f"Missing prompt file: {path} ({e})")


def load_prompt() -> str:
    return _read_prompt("system_prompt.txt")


def load_greeting() -> str:
    return _read_prompt("greeting.txt")


SYSTEM_PROMPT = load_prompt()  # fails fast at startup if the file is missing
load_greeting()


_AR_MONTHS = ["", "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
              "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
_AR_DAYS = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]


def _date_ar(iso: str) -> str:
    """'2026-08-15' → 'السبت 15 أغسطس' so the model never invents 'آوت'."""
    try:
        d = datetime.strptime(iso, "%Y-%m-%d")
        return f"{_AR_DAYS[d.weekday()]} {d.day} {_AR_MONTHS[d.month]}"
    except Exception:
        return iso


# ============================================================
#  Clinic adapter client (wraps the Watar contract)
#  Class name kept as PTClient because web_bridge.py subclasses it.
# ============================================================
_DIACRITICS = re.compile(r"[ؗ-ًؚ-ْـ]")


def _norm(text: str) -> str:
    """Loose Arabic match: 'اسنان' == 'الأسنان', 'جلديه' == 'الجلدية'."""
    t = _DIACRITICS.sub("", (text or "").strip().lower())
    t = re.sub("[أإآٱ]", "ا", t).replace("ة", "ه").replace("ى", "ي").replace("ؤ", "و").replace("ئ", "ي")
    t = re.sub(r"^(د|دكتور|دكتوره|الدكتور|الدكتوره|دكتورة|الدكتورة)\.?\s+", "", t)
    words = []
    for w in t.split():
        if w.startswith("وال") and len(w) > 4:
            w = w[3:]
        elif w.startswith("ال") and len(w) > 3:
            w = w[2:]
        words.append(w)
    return " ".join(words)


def _contains(a: str, b: str) -> bool:
    a, b = _norm(a), _norm(b)
    return bool(a and b) and (a in b or b in a)


class PTClient:
    def __init__(self):
        self._clinics = None
        self._doctors = None  # list of all doctors

    async def _req(self, method, path, **kw):
        headers = {"X-Watar-Key": ADAPTER_KEY}
        async with httpx.AsyncClient(timeout=8.0) as c:
            r = await c.request(method, f"{ADAPTER_URL}{path}", headers=headers, **kw)
            r.raise_for_status()
            return r.json()

    async def clinics(self):
        if self._clinics is None:
            self._clinics = (await self._req("GET", "/watar/v1/clinics")).get("data", [])
        return self._clinics

    async def doctors(self, clinic_id=None):
        if self._doctors is None:
            self._doctors = (await self._req("GET", "/watar/v1/doctors")).get("data", [])
        if clinic_id:
            return [d for d in self._doctors if d["clinic_id"] == clinic_id]
        return self._doctors

    async def slots(self, clinic_id, doctor_id=None, date=None, from_date=None, limit=10):
        params = {"clinic_id": clinic_id, "limit": limit}
        if doctor_id:
            params["doctor_id"] = doctor_id
        if date:
            params["date"] = date
        elif from_date:
            params["from_date"] = from_date
        r = await self._req("GET", "/watar/v1/slots/available", params=params)
        return r.get("data", [])

    async def patient_by_phone(self, phone):
        r = await self._req("GET", "/watar/v1/patients", params={"phone": phone})
        return r.get("patient") if r.get("found") else None

    async def register(self, name, phone, gender="unknown", age=None, guardian_name=None):
        r = await self._req("POST", "/watar/v1/patients/register", json={
            "name": name, "phone": phone, "national_id": "",
            "gender": gender, "age": age, "guardian_name": guardian_name})
        return r.get("patient")

    async def book(self, patient_id, clinic_id, doctor_id, slot_id):
        return await self._req("POST", "/watar/v1/appointments", json={
            "patient_id": patient_id, "clinic_id": clinic_id,
            "doctor_id": doctor_id, "slot_id": slot_id})

    # ---- name resolution helpers ----
    async def find_clinic(self, text):
        cs = await self.clinics()
        for c in cs:                      # exact / name match first
            if _contains(text, c["name"]):
                return c
        for c in cs:                      # then aliases ("اسنان", "حمل", "لوز", ...)
            if any(_contains(text, a) for a in c.get("aliases", [])):
                return c
        return None

    async def find_doctor(self, name, clinic_id=None):
        for d in await self.doctors(clinic_id):
            if _contains(name, d["name"]):
                return d
        # first name only ("دكتور أحمد")
        first = _norm(name).split()[:1]
        if first:
            hits = [d for d in await self.doctors(clinic_id) if _norm(d["name"]).split()[:1] == first]
            if len(hits) == 1:
                return hits[0]
        return None


def _doctor_info(d):
    return {"name": d["name"], "gender": d.get("gender", "unknown"),
            "title": "دكتورة" if d.get("gender") == "female" else "دكتور"}


def _clean_date(text):
    try:
        return datetime.strptime((text or "").strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return ""


# ============================================================
#  Tool implementations (called when Gemini invokes a function)
# ============================================================
async def t_list_clinics(pt: PTClient, caller, **_):
    return {"clinics": [c["name"] for c in await pt.clinics()]}


async def t_list_doctors(pt: PTClient, caller, clinic="", **_):
    c = await pt.find_clinic(clinic)
    if not c:
        return {"error": "clinic not found", "clinics": [x["name"] for x in await pt.clinics()]}
    return {"clinic": c["name"], "doctors": [_doctor_info(d) for d in await pt.doctors(c["id"])]}


async def t_available_slots(pt: PTClient, caller, clinic="", doctor="", date="", from_date="", **_):
    c = await pt.find_clinic(clinic)
    if not c:
        return {"error": "clinic not found", "clinics": [x["name"] for x in await pt.clinics()]}
    d = None
    if doctor:
        d = await pt.find_doctor(doctor, c["id"])
        if not d:
            return {"error": "doctor not found in this clinic",
                    "doctors": [_doctor_info(x) for x in await pt.doctors(c["id"])]}
    date, from_date = _clean_date(date), _clean_date(from_date)
    slots = await pt.slots(c["id"], d["id"] if d else None, date=date, from_date=from_date, limit=8)
    result = {"clinic": c["name"], "doctor": d["name"] if d else "أي طبيب",
              "slots": [{"date": s["date"], "date_ar": _date_ar(s["date"]), "time": s["time"],
                         "doctor": s.get("doctor_name", d["name"] if d else ""),
                         "doctor_gender": s.get("doctor_gender", "")} for s in slots]}
    if not slots and date:
        # nothing that day → offer the nearest days after it
        nxt = await pt.slots(c["id"], d["id"] if d else None, from_date=date, limit=6)
        result["note"] = "no free slots on the requested day; these are the nearest ones"
        result["slots"] = [{"date": s["date"], "date_ar": _date_ar(s["date"]), "time": s["time"],
                            "doctor": s.get("doctor_name", ""), "doctor_gender": s.get("doctor_gender", "")}
                           for s in nxt]
    return result


async def t_book_appointment(pt: PTClient, caller, clinic="", doctor="", date="", time="",
                             patient_name="", phone="", is_child=False, child_name="",
                             child_age=None, **_):
    c = await pt.find_clinic(clinic)
    d = await pt.find_doctor(doctor, c["id"]) if c else None
    if not c or not d:
        return {"error": "clinic or doctor not found"}
    date = _clean_date(date)
    if not date:
        return {"error": "date is required as YYYY-MM-DD (use the date field from available_slots)"}
    want = (time or "").strip()[:5].zfill(5)
    slots = await pt.slots(c["id"], d["id"], date=date, limit=100)
    slot = next((s for s in slots if s["time"] == want), None)
    if not slot:
        return {"error": "time not available",
                "slots": [{"date": s["date"], "date_ar": _date_ar(s["date"]), "time": s["time"]}
                          for s in slots[:6]]}

    use_phone = phone or caller.get("phone") or ""
    if is_child and child_name:
        pat = await pt.register(child_name, use_phone or "unknown",
                                age=child_age, guardian_name=patient_name or caller.get("name"))
    else:
        pat = await pt.patient_by_phone(use_phone) if use_phone else None
        if not pat or (patient_name and _norm(pat["name"]) != _norm(patient_name)):
            # same phone can belong to several family members → new record per name
            pat = await pt.register(patient_name or "متصل", use_phone or "unknown")
    if not pat:
        return {"error": "could not create patient"}

    try:
        res = await pt.book(pat["id"], c["id"], d["id"], slot["id"])
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            return {"error": "this time was just taken, offer another time"}
        raise
    conf = (res or {}).get("data", {}).get("confirmation_number", "")
    print(f"🔧 BOOKED: {c['name']} / {d['name']} / {slot['date']} {slot['time']} "
          f"/ patient={pat['name']} / conf={conf}")
    return {"status": "confirmed", "clinic": c["name"], "doctor": d["name"],
            "doctor_title": _doctor_info(d)["title"], "date": slot["date"],
            "date_ar": _date_ar(slot["date"]), "time": slot["time"], "confirmation_number": conf}


TOOL_IMPLS = {
    "list_clinics": t_list_clinics,
    "list_doctors": t_list_doctors,
    "available_slots": t_available_slots,
    "book_appointment": t_book_appointment,
}

_S = types.Schema
_T = types.Type
TOOLS = [types.Tool(function_declarations=[
    types.FunctionDeclaration(name="list_clinics",
        description="ارجع العيادات/التخصصات المتاحة في المجمع"),
    types.FunctionDeclaration(name="list_doctors",
        description="ارجع الأطباء في عيادة معينة",
        parameters=_S(type=_T.OBJECT, properties={
            "clinic": _S(type=_T.STRING, description="اسم العيادة، مثل: الأسنان، طب الأطفال، الجلدية")},
            required=["clinic"])),
    types.FunctionDeclaration(name="available_slots",
        description="ارجع أقرب المواعيد المتاحة في عيادة. الطبيب اختياري (بدونه = أي طبيب). "
                    "مرّر date لليوم المطلوب بالضبط، أو from_date لمواعيد من يوم معين وبعده.",
        parameters=_S(type=_T.OBJECT, properties={
            "clinic": _S(type=_T.STRING),
            "doctor": _S(type=_T.STRING, description="اسم الطبيب إن طلب المتصل طبيب معين"),
            "date": _S(type=_T.STRING, description="يوم محدد YYYY-MM-DD"),
            "from_date": _S(type=_T.STRING, description="من هذا اليوم وبعده YYYY-MM-DD")},
            required=["clinic"])),
    types.FunctionDeclaration(name="book_appointment",
        description="احجز موعد بعد تأكيد المتصل الصريح. للطفل مرّر is_child و child_name و child_age.",
        parameters=_S(type=_T.OBJECT, properties={
            "clinic": _S(type=_T.STRING),
            "doctor": _S(type=_T.STRING),
            "date": _S(type=_T.STRING, description="التاريخ YYYY-MM-DD كما رجع من available_slots"),
            "time": _S(type=_T.STRING, description="الوقت مثل 09:20"),
            "patient_name": _S(type=_T.STRING, description="اسم المريض البالغ / ولي الأمر"),
            "phone": _S(type=_T.STRING, description="رقم الجوال ١٠ أرقام يبدأ بـ 05"),
            "is_child": _S(type=_T.BOOLEAN, description="هل الموعد لطفل"),
            "child_name": _S(type=_T.STRING),
            "child_age": _S(type=_T.INTEGER)},
            required=["clinic", "doctor", "date", "time", "patient_name", "phone"])),
])]


def _dates_block() -> str:
    """Today's date + the next 14 days, so the model can turn 'الأحد الجاي' into YYYY-MM-DD."""
    try:
        from zoneinfo import ZoneInfo
        today = datetime.now(ZoneInfo(os.environ.get("CLINIC_TZ", "Asia/Riyadh"))).date()
    except Exception:
        today = datetime.now().date()
    lines = [f"اليوم: {_date_ar(today.isoformat())} ({today.isoformat()})", "الأيام القادمة:"]
    for i in range(1, 15):
        d = (today + timedelta(days=i)).isoformat()
        lines.append(f"- {_date_ar(d)} = {d}")
    return "\n".join(lines)

LIVE_CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    system_instruction=types.Content(parts=[types.Part(text=SYSTEM_PROMPT)]),
    tools=TOOLS,
)
# Force Arabic (Saudi) so it stops mishearing/replying in other languages,
# and optionally pick a specific built-in voice. Guarded — SDK shapes vary.
LANG = os.environ.get("GEMINI_LANG", "ar-SA")
try:
    _sc = types.SpeechConfig(language_code=LANG)
    if VOICE:
        _sc.voice_config = types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE))
    LIVE_CONFIG.speech_config = _sc
except Exception as e:
    print(f"speech config skipped: {e}")
try:
    LIVE_CONFIG.input_audio_transcription = types.AudioTranscriptionConfig()
    LIVE_CONFIG.output_audio_transcription = types.AudioTranscriptionConfig()
except Exception:
    pass

def agent_config():
    """LIVE_CONFIG with the latest prompt from prompts/system_prompt.txt + today's dates."""
    cfg = LIVE_CONFIG.model_copy()
    text = load_prompt() + "\n\n" + _dates_block()
    cfg.system_instruction = types.Content(parts=[types.Part(text=text)])
    return cfg


app = FastAPI()
_client = genai.Client(api_key=API_KEY) if API_KEY else None


@app.get("/health")
async def health():
    return {"ok": True, "model": MODEL, "adapter": ADAPTER_URL, "key_set": bool(API_KEY)}


@app.api_route("/twiml/{tenant_id}", methods=["GET", "POST"])
async def twiml(tenant_id: str, request: Request):
    host = request.url.hostname
    # pass the caller's number into the stream so patient lookup works
    caller = ""
    try:
        form = await request.form()
        caller = form.get("From", "")
    except Exception:
        pass
    ws_url = f"wss://{host}/ws/pt/{tenant_id}"
    return PlainTextResponse(
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Connect><Stream url="{ws_url}">'
        f'<Parameter name="caller" value="{caller}"/>'
        f'</Stream></Connect></Response>',
        media_type="application/xml",
    )


@app.websocket("/ws/pt/{tenant_id}")
async def pt_bridge(ws: WebSocket, tenant_id: str):
    await ws.accept()
    print(f"📞 call connected (tenant={tenant_id})")
    if _client is None:
        await ws.close(); return

    pt = PTClient()
    caller = {"phone": "", "name": ""}
    stream_sid = {"v": None}
    in_state = {"v": None}
    out_state = {"v": None}
    playback_end = {"v": 0.0}
    MUTE_TAIL = 0.8

    async with _client.aio.live.connect(model=MODEL, config=agent_config()) as session:

        async def twilio_to_gemini():
            try:
                while True:
                    msg = json.loads(await ws.receive_text())
                    ev = msg.get("event")
                    if ev == "start":
                        stream_sid["v"] = msg["start"]["streamSid"]
                        params = msg["start"].get("customParameters", {}) or {}
                        caller["phone"] = params.get("caller", "") or ""
                        print(f"▶️  stream started (caller={caller['phone'] or 'unknown'})")
                        # Greet FIRST — the AI speaks before the caller says anything.
                        try:
                            await session.send_client_content(
                                turns=types.Content(role="user", parts=[types.Part(
                                    text=load_greeting())]),
                                turn_complete=True)
                        except Exception as e:
                            print(f"greeting kickoff skipped: {e}")
                    elif ev == "media":
                        if time.time() < playback_end["v"] + MUTE_TAIL:
                            continue
                        ulaw = base64.b64decode(msg["media"]["payload"])
                        pcm8 = audioop.ulaw2lin(ulaw, 2)
                        pcm16, in_state["v"] = audioop.ratecv(pcm8, 2, 1, TWILIO_SR, GEMINI_IN_SR, in_state["v"])
                        await session.send_realtime_input(
                            audio=types.Blob(data=pcm16, mime_type="audio/pcm;rate=16000"))
                    elif ev == "stop":
                        print("⏹  stream stopped"); break
            except WebSocketDisconnect:
                print("📴 caller hung up")

        async def gemini_to_twilio():
            leftover = b""
            while True:
              async for m in session.receive():
                sc = getattr(m, "server_content", None)
                if sc:
                    it = getattr(sc, "input_transcription", None)
                    if it and getattr(it, "text", None):
                        print(f"🎤 caller: {it.text}")
                    ot = getattr(sc, "output_transcription", None)
                    if ot and getattr(ot, "text", None):
                        print(f"🤖 AI: {ot.text}")
                    if getattr(sc, "interrupted", False) and stream_sid["v"]:
                        await ws.send_text(json.dumps({"event": "clear", "streamSid": stream_sid["v"]}))
                        leftover = b""; playback_end["v"] = time.time()

                if getattr(m, "data", None) and stream_sid["v"]:
                    secs = (len(m.data) / 2) / GEMINI_OUT_SR
                    playback_end["v"] = max(time.time(), playback_end["v"]) + secs
                    pcm8, out_state["v"] = audioop.ratecv(m.data, 2, 1, GEMINI_OUT_SR, TWILIO_SR, out_state["v"])
                    buf = leftover + audioop.lin2ulaw(pcm8, 2)
                    while len(buf) >= TWILIO_FRAME:
                        frame, buf = buf[:TWILIO_FRAME], buf[TWILIO_FRAME:]
                        await ws.send_text(json.dumps({
                            "event": "media", "streamSid": stream_sid["v"],
                            "media": {"payload": base64.b64encode(frame).decode()}}))
                    leftover = buf

                tc = getattr(m, "tool_call", None)
                if tc:
                    responses = []
                    for fc in tc.function_calls:
                        impl = TOOL_IMPLS.get(fc.name)
                        args = dict(fc.args or {})
                        print(f"🔧 {fc.name}({args})")
                        try:
                            result = await impl(pt, caller, **args) if impl else {"error": "unknown"}
                        except Exception as e:
                            result = {"error": str(e)}
                        responses.append(types.FunctionResponse(id=fc.id, name=fc.name, response=result))
                    await session.send_tool_response(function_responses=responses)

        recv_task = asyncio.create_task(gemini_to_twilio())
        try:
            await twilio_to_gemini()
        except Exception as e:
            print(f"bridge error: {e}")
        finally:
            recv_task.cancel()
            try:
                await recv_task
            except BaseException:
                pass
            print("call ended")
