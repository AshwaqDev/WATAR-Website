// Real-time voice call from the browser to the Watar agent server (/ws/web).
// Mic → 16 kHz PCM16 (binary frames) → server.  Server → 24 kHz PCM16 (binary) → speakers.
// Text frames are small JSON events: ready, transcript, turn_end, interrupted, tool, end, error.

function rms(analyser, buf) {
  analyser.getFloatTimeDomainData(buf);
  let s = 0;
  for (let i = 0; i < buf.length; i++) s += buf[i] * buf[i];
  return Math.sqrt(s / buf.length);
}

function fail(code, message) {
  const e = new Error(message || code);
  e.code = code;
  return e;
}

export async function startLiveCall({ url, onText, onTurnEnd, onTool, onClose, onError }) {
  // Browsers only allow the microphone on https:// or http://localhost.
  // Check first, so we don't open an agent session we can't use.
  if (!navigator.mediaDevices?.getUserMedia) throw fail("insecure");

  // Create audio contexts right away (still inside the user's click).
  const outCtx = new AudioContext({ sampleRate: 24000 });
  const inCtx = new AudioContext();
  outCtx.resume().catch(() => {});
  inCtx.resume().catch(() => {});

  const outGain = outCtx.createGain();
  const outAnalyser = outCtx.createAnalyser();
  outAnalyser.fftSize = 512;
  outGain.connect(outAnalyser).connect(outCtx.destination);
  let playHead = 0;
  const playing = new Set();

  function play(arrayBuffer) {
    const pcm = new Int16Array(arrayBuffer, 0, arrayBuffer.byteLength >> 1);
    if (!pcm.length) return;
    const f = new Float32Array(pcm.length);
    for (let i = 0; i < pcm.length; i++) f[i] = pcm[i] / 32768;
    const buf = outCtx.createBuffer(1, f.length, 24000);
    buf.copyToChannel(f, 0);
    const src = outCtx.createBufferSource();
    src.buffer = buf;
    src.connect(outGain);
    playHead = Math.max(playHead, outCtx.currentTime + 0.03);
    src.start(playHead);
    playHead += buf.duration;
    playing.add(src);
    src.onended = () => playing.delete(src);
  }
  function flush() {
    playing.forEach((s) => { try { s.stop(); } catch {} });
    playing.clear();
    playHead = 0;
  }

  let mic = null, closed = false, ready = false;
  const ws = new WebSocket(url);
  ws.binaryType = "arraybuffer";

  function cleanup() {
    if (closed) return;
    closed = true;
    flush();
    mic?.getTracks().forEach((t) => t.stop());
    inCtx.close().catch(() => {});
    outCtx.close().catch(() => {});
    try { ws.close(); } catch {}
  }
  function stop() {
    if (closed) return;
    try { if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: "stop" })); } catch {}
    cleanup();
    onClose?.();
  }

  // 1) Wait until the server has connected to the agent.
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => { cleanup(); reject(fail("unreachable", "timeout")); }, 10000);

    ws.onmessage = (ev) => {
      if (typeof ev.data !== "string") { play(ev.data); return; }
      let msg;
      try { msg = JSON.parse(ev.data); } catch { return; }
      switch (msg.type) {
        case "ready":
          ready = true; clearTimeout(timer); resolve(); break;
        case "transcript":
          onText?.(msg.role === "user" ? "user" : "agent", msg.text); break;
        case "turn_end":
          onTurnEnd?.(); break;
        case "interrupted":
          flush(); break;
        case "tool":
          onTool?.(msg.name); break;
        case "end":
          stop(); break;
        case "error":
          clearTimeout(timer);
          if (!ready) { cleanup(); reject(fail(msg.reason || "server")); }
          else { cleanup(); onError?.(msg.reason); }
          break;
      }
    };
    ws.onerror = () => {
      if (!ready) { clearTimeout(timer); cleanup(); reject(fail("unreachable")); }
    };
    ws.onclose = () => {
      if (!ready) { clearTimeout(timer); cleanup(); reject(fail("unreachable")); }
      else if (!closed) { cleanup(); onClose?.(); }
    };
  });

  // 2) Microphone (throws NotAllowedError if blocked).
  try {
    mic = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true, autoGainControl: true },
    });
  } catch (err) {
    cleanup();
    throw err;
  }
  if (closed) throw fail("server");

  await inCtx.audioWorklet.addModule(new URL("./mic-worklet.js", import.meta.url));
  const micSrc = inCtx.createMediaStreamSource(mic);
  const micAnalyser = inCtx.createAnalyser();
  micAnalyser.fftSize = 512;
  const capture = new AudioWorkletNode(inCtx, "mic-capture", { processorOptions: { targetRate: 16000 } });
  const mute = inCtx.createGain();
  mute.gain.value = 0;
  micSrc.connect(micAnalyser);
  micSrc.connect(capture).connect(mute).connect(inCtx.destination);
  capture.port.onmessage = (e) => {
    if (!closed && ws.readyState === WebSocket.OPEN) ws.send(e.data);
  };

  const lv = new Float32Array(512);
  return {
    stop,
    getLevel: () => (closed ? 0 : Math.min(1, Math.max(rms(micAnalyser, lv) * 4, rms(outAnalyser, lv) * 5))),
  };
}
