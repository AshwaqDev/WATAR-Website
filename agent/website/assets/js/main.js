// Watar — page behaviour: language, menu, sections, live demo.
const CFG = window.WATAR_CONFIG;
const I18N = window.WATAR_I18N;
const FAQ = window.WATAR_FAQ;
const CONVOS = window.WATAR_CONVOS;

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

/* ------------------------------------------------------------------ */
/* Language                                                            */
/* ------------------------------------------------------------------ */
let lang = (() => {
  try { return localStorage.getItem("watar-lang") || CFG.defaultLang; } catch { return CFG.defaultLang; }
})();
const t = (key) => I18N[lang][key] ?? I18N.en[key] ?? key;

function applyLang() {
  const html = document.documentElement;
  html.lang = lang;
  html.dir = lang === "ar" ? "rtl" : "ltr";
  document.title = lang === "ar" ? "وتر | موظف صوتي ذكي" : "Watar | AI voice agent";
  $$("[data-i18n]").forEach((el) => (el.textContent = t(el.dataset.i18n)));
  $$("[data-i18n-placeholder]").forEach((el) => (el.placeholder = t(el.dataset.i18nPlaceholder)));
  $("#langToggle").textContent = lang === "ar" ? "EN" : "ع";
  renderFaq();
  renderChannel(currentChannel);
  demo.refreshText();
}

$("#langToggle").addEventListener("click", () => {
  lang = lang === "ar" ? "en" : "ar";
  try { localStorage.setItem("watar-lang", lang); } catch {}
  applyLang();
});

/* ------------------------------------------------------------------ */
/* Header + mobile menu                                                */
/* ------------------------------------------------------------------ */
const header = $(".header");
const menuBtn = $("#menuToggle");
menuBtn.addEventListener("click", () => {
  const open = header.classList.toggle("is-open");
  menuBtn.setAttribute("aria-expanded", open);
});
$$("#nav a").forEach((a) => a.addEventListener("click", () => {
  header.classList.remove("is-open");
  menuBtn.setAttribute("aria-expanded", "false");
}));
addEventListener("scroll", () => header.classList.toggle("is-scrolled", scrollY > 10), { passive: true });

/* ------------------------------------------------------------------ */
/* Contact details from config                                         */
/* ------------------------------------------------------------------ */
$("#waDirect").href = `https://wa.me/${CFG.whatsapp}`;
$("#mailDirect").href = `mailto:${CFG.email}`;
$("#mailText").textContent = CFG.email;
$("#year").textContent = new Date().getFullYear();

/* ------------------------------------------------------------------ */
/* FAQ                                                                 */
/* ------------------------------------------------------------------ */
function renderFaq() {
  const list = $("#faqList");
  list.innerHTML = "";
  FAQ[lang].forEach(([q, a], i) => {
    const d = document.createElement("details");
    if (i === 0) d.open = true;
    const s = document.createElement("summary");
    s.textContent = q;
    const p = document.createElement("p");
    p.textContent = a;
    d.append(s, p);
    list.append(d);
  });
}

/* ------------------------------------------------------------------ */
/* Channels                                                            */
/* ------------------------------------------------------------------ */
let currentChannel = "inbound";
let convoTimers = [];
function renderChannel(key) {
  currentChannel = key;
  $$(".ch-tab").forEach((b) => b.classList.toggle("is-active", b.dataset.ch === key));
  $("#chTitle").textContent = t(`ch.${key}.t`);
  $("#chDesc").textContent = t(`ch.${key}.d`);
  const box = $("#chConvo");
  convoTimers.forEach(clearTimeout);
  convoTimers = [];
  box.innerHTML = "";
  CONVOS[lang][key].forEach(([who, text], i) => {
    convoTimers.push(setTimeout(() => {
      const b = document.createElement("div");
      b.className = `bubble bubble--${who}`;
      if (who !== "s") {
        const sm = document.createElement("small");
        sm.textContent = who === "c" ? (lang === "ar" ? "العميل" : "Caller") : t("demo.agent");
        b.append(sm);
      }
      b.append(document.createTextNode(text));
      box.append(b);
    }, i * 650));
  });
}
$$(".ch-tab").forEach((b) => b.addEventListener("click", () => renderChannel(b.dataset.ch)));

/* ------------------------------------------------------------------ */
/* Contact form → email (FormSubmit sends it to CFG.email)            */
/* ------------------------------------------------------------------ */
const form = $("#contactForm");
const formErr = $("#formError");
const formStatus = $("#formStatus");
const formBtn = $("#formSubmit");
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function showFormError(key) {
  formStatus.hidden = true;
  formErr.textContent = t(key);
  formErr.hidden = false;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const d = Object.fromEntries(new FormData(form));
  formErr.hidden = true;
  formStatus.hidden = true;
  if (d._honey) return;                       // bot filled the hidden field
  const name = d.name.trim(), phone = d.phone.trim(), email = d.email.trim();
  if (!name || (!phone && !email)) return showFormError("form.error");
  if (email && !EMAIL_RE.test(email)) return showFormError("form.emailInvalid");

  formBtn.disabled = true;
  formBtn.textContent = t("form.sending");
  try {
    const res = await fetch(`https://formsubmit.co/ajax/${CFG.email}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        _subject: t("form.subject"),
        _template: "table",
        _replyto: email || undefined,
        [t("form.name")]: name,
        [t("form.company")]: d.company.trim() || "-",
        [t("form.phone")]: phone || "-",
        [t("form.email")]: email || "-",
        [t("form.message")]: d.message.trim() || "-",
        [lang === "ar" ? "لغة الصفحة" : "Page language"]: lang,
      }),
    });
    const out = await res.json().catch(() => ({}));
    if (!res.ok || String(out.success) !== "true") throw new Error(out.message || res.status);
    form.reset();
    formStatus.textContent = t("form.success");
    formStatus.hidden = false;
  } catch (err) {
    console.error("Contact form failed:", err);
    showFormError("form.fail");
  } finally {
    formBtn.disabled = false;
    formBtn.textContent = t("form.send");
  }
});

/* ------------------------------------------------------------------ */
/* Scroll reveal                                                       */
/* ------------------------------------------------------------------ */
const io = new IntersectionObserver((entries) => entries.forEach((en) => {
  if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
}), { threshold: 0.12 });
$$(".reveal").forEach((el) => io.observe(el));

/* ------------------------------------------------------------------ */
/* Vibrating strings (the demo visual)                                 */
/* ------------------------------------------------------------------ */
const strings = (() => {
  const svg = $("#stringsSvg");
  const NS = "http://www.w3.org/2000/svg";
  const W = 400, rows = [34, 62, 90, 118, 146];
  const paths = rows.map((y, i) => {
    const p = document.createElementNS(NS, "path");
    const mid = i === 2;
    p.setAttribute("stroke", mid ? "#4FBFB5" : "rgba(246,244,239,0.55)");
    p.setAttribute("stroke-width", mid ? "2.4" : "1.4");
    svg.append(p);
    return { p, y, k: 1 + (i % 3), speed: 5 + i * 1.7, phase: i * 1.3, weight: mid ? 1 : 0.55 + (i % 2) * 0.2 };
  });
  let level = 0, target = 0;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  function frame(ts) {
    const time = ts / 1000;
    level += (target - level) * 0.18;
    const amp = 1.5 + level * 26;
    for (const s of paths) {
      let d = `M0 ${s.y}`;
      for (let x = 0; x <= W; x += 8) {
        const env = Math.sin((Math.PI * x) / W);
        const v = env * Math.sin(time * s.speed + s.phase) * Math.sin((s.k * Math.PI * x) / W + time * 0.6);
        d += ` L${x} ${(s.y + v * amp * s.weight).toFixed(2)}`;
      }
      s.p.setAttribute("d", d);
    }
    if (!reduce) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  return { set: (v) => (target = Math.max(0, Math.min(1, v))) };
})();

/* ------------------------------------------------------------------ */
/* Live demo controller                                                */
/* ------------------------------------------------------------------ */
const demo = (() => {
  const btn = $("#callBtn");
  const statusEl = $("#demoStatus");
  const statusText = $("#demoStatusText");
  const timerEl = $("#demoTimer");
  const hint = $("#demoHint");
  const box = $("#demoTranscript");

  let state = "idle";          // idle | connecting | live | ended
  let session = null;          // live session or mock
  let startedAt = 0, tick = null, levelLoop = null;
  let lastLine = null, lastRole = null;

  function setState(s) {
    state = s;
    statusEl.className = `demo__status is-${s}`;
    statusText.textContent = t(`demo.${s}`);
    btn.classList.toggle("is-active", s === "live" || s === "connecting");
    btn.disabled = s === "connecting";
    btn.setAttribute("aria-label", s === "live" ? "End call" : "Start call");
  }

  function setHint(key, isError = false) {
    hint.textContent = t(key);
    hint.dataset.i18n = key;
    hint.classList.toggle("is-error", isError);
  }

  function addText(role, text, append = true) {
    if (role === "note") {
      const n = document.createElement("div");
      n.className = "demo__line demo__line--note";
      n.textContent = text;
      box.append(n);
      lastLine = null; lastRole = null;
    } else if (append && lastRole === role && lastLine) {
      lastLine.lastChild.textContent += text;
    } else {
      const line = document.createElement("div");
      line.className = `demo__line demo__line--${role}`;
      const sm = document.createElement("small");
      sm.textContent = role === "user" ? t("demo.you") : (CFG.agentName?.[lang] || t("demo.agent"));
      line.append(sm, document.createTextNode(text));
      box.append(line);
      lastLine = line; lastRole = role;
    }
    box.scrollTop = box.scrollHeight;
  }
  const endTurn = () => { lastRole = null; lastLine = null; };

  function startTimer() {
    startedAt = Date.now();
    tick = setInterval(() => {
      const sec = Math.floor((Date.now() - startedAt) / 1000);
      timerEl.textContent = `${String(Math.floor(sec / 60)).padStart(2, "0")}:${String(sec % 60).padStart(2, "0")}`;
      if (sec >= CFG.maxCallSeconds) stop();
    }, 250);
  }

  async function start() {
    box.innerHTML = ""; endTurn();
    timerEl.textContent = "00:00";
    setState("connecting");
    setHint("demo.hint");

    // Opened as a plain file (no server) → scripted preview.
    if (location.protocol === "file:" || !CFG.voiceSocket) return startMock();

    const url = new URL(CFG.voiceSocket, location.href);
    url.protocol = url.protocol === "https:" ? "wss:" : url.protocol === "http:" ? "ws:" : url.protocol;

    try {
      const { startLiveCall } = await import("./voice-live.js");
      session = await startLiveCall({
        url: url.href,
        onText: (role, text) => addText(role, text),
        onTurnEnd: endTurn,
        onTool: () => addText("note", t("demo.checking")),
        onClose: () => finish(),
        onError: (reason) => { finish(); setHint(reason === "busy" ? "demo.busy" : "demo.connError", true); },
      });
      setState("live");
      startTimer();
      levelLoop = setInterval(() => strings.set(session?.getLevel() ?? 0), 50);
    } catch (err) {
      console.error(err);
      if (err?.code === "unreachable" && CFG.previewFallback) return startMock();
      finish();
      setHint(err?.name === "NotAllowedError" ? "demo.micError" : err?.code === "busy" ? "demo.busy" : "demo.connError", true);
    }
  }

  // Scripted preview (used when no voice server is configured)
  function startMock() {
    setState("live");
    startTimer();
    addText("note", t("demo.preview"));
    const script = CONVOS[lang].inbound.filter(([w]) => w !== "s");
    let i = 0, timers = [];
    const next = () => {
      if (i >= script.length) { timers.push(setTimeout(stop, 1500)); return; }
      const [who, text] = script[i++];
      const role = who === "c" ? "user" : "agent";
      let pos = 0;
      addText(role, "", false);
      strings.set(role === "agent" ? 0.7 : 0.35);
      const typer = setInterval(() => {
        pos += 2;
        lastLine.lastChild.textContent = text.slice(0, pos);
        strings.set((role === "agent" ? 0.45 : 0.2) + Math.random() * 0.4);
        if (pos >= text.length) { clearInterval(typer); strings.set(0.05); endTurn(); timers.push(setTimeout(next, 700)); }
      }, 45);
      timers.push(typer);
    };
    timers.push(setTimeout(next, 600));
    session = { stop: () => timers.forEach((x) => { clearTimeout(x); clearInterval(x); }) };
  }

  function finish() {
    clearInterval(tick); clearInterval(levelLoop);
    strings.set(0);
    if (state !== "idle") setState("ended");
    session = null;
  }

  function stop() {
    const s = session;
    session = null;
    try { s?.stop(); } catch {}
    finish();
  }

  btn.addEventListener("click", () => (state === "live" || state === "connecting" ? stop() : start()));


  return {
    refreshText() {
      statusText.textContent = t(`demo.${state}`);
      hint.textContent = t(hint.dataset.i18n || "demo.hint");
    },
  };
})();

applyLang();
