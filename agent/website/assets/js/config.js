// ============================================================
//  Watar site settings — edit these values.
// ============================================================
window.WATAR_CONFIG = {
  // Demo phone number (placeholder — replace with the real Twilio number later)
  phoneDisplay: "+966 11 000 0000",
  phoneTel: "+966110000000",

  // Where the contact form sends messages
  whatsapp: "966500000000",          // international format, digits only
  email: "hello@watar.example",

  // Live demo: the agent server's browser entrance (web_bridge.py → /ws/web).
  // Relative path = same server that serves this page.
  // If the website is hosted elsewhere, use the full address, e.g. "wss://agent.watar.sa/ws/web".
  voiceSocket: "/ws/web",

  // If the agent server can't be reached, play a scripted preview instead.
  // Set to false when going live, so visitors see "try calling the number" instead.
  previewFallback: true,

  // Name shown on the agent's lines in the live transcript
  agentName: { ar: "سارا", en: "Sara" },

  // Max length of a browser demo call, in seconds (the server also enforces WEB_MAX_SECONDS)
  maxCallSeconds: 240,

  // Default language: "ar" or "en"
  defaultLang: "ar",
};
