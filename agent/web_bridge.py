#!/usr/bin/env python3
"""
Watar — website "Talk in browser" entrance for the SAME agent as the Twilio line
=================================================================================
Put this file next to pt_live_bridge.py. It reuses that file's voice, model, tools and
booking adapter, and the SAME prompt files (prompts/system_prompt.txt, prompts/greeting.txt),
so editing a prompt file changes the phone line and the website together. It adds:

  /ws/web   ← the website's live demo connects here (browser audio)
  /         ← serves the website (folder ./website)

Twilio keeps working exactly as before (/twiml/pt and /ws/pt/... are the same app).

Run (instead of pt_live_bridge):
  uvicorn web_bridge:app --host 0.0.0.0 --port 8080
Then open http://localhost:8080

Optional env vars:
  WEB_MAX_SECONDS   max length of one website call (default 240)
  WEB_MAX_CALLS     max website calls at the same time (default 5)
  ALLOWED_ORIGINS   only accept website calls from these sites, e.g.
                    "https://watar.sa,https://www.watar.sa" (set before going live)
  WEB_ADAPTER_URL / WEB_ADAPTER_KEY
                    send website-demo bookings to a different (demo) booking system.
                    Default: same as the phone line (CLINIC_ADAPTER_URL / CLINIC_ADAPTER_KEY).
  WEBSITE_DIR       folder with the website files (default ./website)
"""
import asyncio
import json
import os
from pathlib import Path

import httpx
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from google.genai import types

import pt_live_bridge as agent          # the phone agent — single source of truth
from pt_live_bridge import app          # same FastAPI app → Twilio routes stay live

WEBSITE_DIR = os.environ.get("WEBSITE_DIR", str(Path(__file__).parent / "website"))
MAX_SECONDS = int(os.environ.get("WEB_MAX_SECONDS", "240"))
MAX_CALLS = int(os.environ.get("WEB_MAX_CALLS", "5"))
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
WEB_ADAPTER_URL = os.environ.get("WEB_ADAPTER_URL", agent.ADAPTER_URL)
WEB_ADAPTER_KEY = os.environ.get("WEB_ADAPTER_KEY", agent.ADAPTER_KEY)

def _greeting():
    """Shared greeting from prompts/greeting.txt (same as the phone line)."""
    if hasattr(agent, "load_greeting"):
        return agent.load_greeting()
    # Older pt_live_bridge.py without shared prompt files:
    return ("المتصل بدأ المكالمة الآن. رحّبي فيه فورًا بترحيب سعودي قصير ودافئ، "
            "وعرّفي عن نفسك باسمك سارا من مجمع واتر الطبي، واسأليه كيف تقدرين تساعدينه.")


class WebPTClient(agent.PTClient):
    """Same booking client, but can point website calls at a separate adapter."""
    async def _req(self, method, path, **kw):
        headers = {"X-Watar-Key": WEB_ADAPTER_KEY}
        async with httpx.AsyncClient(timeout=8.0) as c:
            r = await c.request(method, f"{WEB_ADAPTER_URL}{path}", headers=headers, **kw)
            r.raise_for_status()
            return r.json()


_active = {"n": 0}


@app.websocket("/ws/web")
async def web_call(ws: WebSocket):
    origin = ws.headers.get("origin", "")
    if ALLOWED_ORIGINS and origin not in ALLOWED_ORIGINS:
        await ws.close(code=1008)
        return
    await ws.accept()

    async def send(obj):
        await ws.send_text(json.dumps(obj, ensure_ascii=False))

    if agent._client is None:
        await send({"type": "error", "reason": "no_api_key"})
        await ws.close()
        return
    if _active["n"] >= MAX_CALLS:
        await send({"type": "error", "reason": "busy"})
        await ws.close()
        return

    _active["n"] += 1
    print(f"🌐 web call connected (active={_active['n']})")
    pt = WebPTClient()
    caller = {"phone": "", "name": ""}

    try:
        async with agent._client.aio.live.connect(model=agent.MODEL, config=(agent.agent_config() if hasattr(agent, "agent_config") else agent.LIVE_CONFIG)) as session:
            await send({"type": "ready"})
            await session.send_client_content(
                turns=types.Content(role="user", parts=[types.Part(text=_greeting())]),
                turn_complete=True)

            async def browser_to_gemini():
                # Binary frames = PCM16 mono 16 kHz from the browser mic.
                while True:
                    msg = await ws.receive()
                    if msg["type"] == "websocket.disconnect":
                        return
                    if msg.get("bytes"):
                        await session.send_realtime_input(
                            audio=types.Blob(data=msg["bytes"], mime_type="audio/pcm;rate=16000"))
                    elif msg.get("text"):
                        try:
                            if json.loads(msg["text"]).get("type") == "stop":
                                return
                        except ValueError:
                            pass

            async def gemini_to_browser():
                while True:
                    async for m in session.receive():
                        sc = getattr(m, "server_content", None)
                        if sc:
                            it = getattr(sc, "input_transcription", None)
                            if it and getattr(it, "text", None):
                                print(f"🎤 [web] caller: {it.text}")
                                await send({"type": "transcript", "role": "user", "text": it.text})
                            ot = getattr(sc, "output_transcription", None)
                            if ot and getattr(ot, "text", None):
                                print(f"🤖 [web] AI: {ot.text}")
                                await send({"type": "transcript", "role": "agent", "text": ot.text})
                            if getattr(sc, "interrupted", False):
                                await send({"type": "interrupted"})
                            if getattr(sc, "turn_complete", False):
                                await send({"type": "turn_end"})

                        # PCM16 mono 24 kHz → browser plays it directly (no resampling needed).
                        if getattr(m, "data", None):
                            await ws.send_bytes(m.data)

                        tc = getattr(m, "tool_call", None)
                        if tc:
                            responses = []
                            for fc in tc.function_calls:
                                impl = agent.TOOL_IMPLS.get(fc.name)
                                args = dict(fc.args or {})
                                print(f"🔧 [web] {fc.name}({args})")
                                await send({"type": "tool", "name": fc.name})
                                try:
                                    result = await impl(pt, caller, **args) if impl else {"error": "unknown"}
                                except Exception as e:
                                    result = {"error": str(e)}
                                responses.append(types.FunctionResponse(id=fc.id, name=fc.name, response=result))
                            await session.send_tool_response(function_responses=responses)

            tasks = [asyncio.create_task(browser_to_gemini()), asyncio.create_task(gemini_to_browser())]
            done, _ = await asyncio.wait(tasks, timeout=MAX_SECONDS, return_when=asyncio.FIRST_COMPLETED)
            if not done:
                print("⏱  web call hit time limit")
                try:
                    await send({"type": "end", "reason": "time_limit"})
                except Exception:
                    pass
            for t in tasks:
                t.cancel()
            for t in tasks:
                try:
                    await t
                except BaseException:
                    pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"web bridge error: {e}")
        try:
            await send({"type": "error", "reason": "server"})
        except Exception:
            pass
    finally:
        _active["n"] -= 1
        try:
            await ws.close()
        except Exception:
            pass
        print("🌐 web call ended")


# Serve the website last, so all API / Twilio routes above take priority.
if Path(WEBSITE_DIR).is_dir():
    app.mount("/", StaticFiles(directory=WEBSITE_DIR, html=True), name="website")
    print(f"🌐 website served from {WEBSITE_DIR}")
else:
    print(f"⚠️  website folder not found: {WEBSITE_DIR} (only /ws/web is available)")
