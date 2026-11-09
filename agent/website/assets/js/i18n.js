// All site text in Arabic and English. Edit freely.
//
// Copy notes
// - Positioning: sector-neutral. Healthcare is the first sector and appears only as an example.
// - Scope today: phone/voice calls only. No integration with customers' systems, and no setup
//   timeframe is promised. Don't add either until it's true.
// - Differentiators vs. Sawt, Hams, Sarj, Nabrah: done-for-you setup and a live demo with no sign-up (Nabrah also has one; the others
//   require a sales call).
// - Each section does one job; promises are not repeated across sections.
// - Language: the agent speaks Saudi dialect. Say only that, everywhere, until more are supported.
// - Arabic marketing copy uses light Saudi colloquial; UI messages stay neutral.
// - Agent persona is "Sara"; "Watar" is the product name only.
// - Do not claim PDPL compliance, certifications or hosting details until they are confirmed in writing.
// - Don't mention the pilot stage on the site.
// - Search for "TODO" for items to fill in later.

window.WATAR_I18N = {
  ar: {
    "nav.how": "كيف يعمل",
    "nav.features": "المزايا",
    "nav.channels": "القنوات",
    "nav.faq": "الأسئلة الشائعة",
    "nav.contact": "تواصل معنا",
    "nav.try": "جرّب مكالمة",

    "hero.badge": "جرّبه بصوتك الحين، بدون تسجيل",
    "hero.title": "موظف استقبال صوتي يرد على كل مكالمة، بلهجة عملائك.",
    "hero.sub": "وتر يجاوب على استفسارات عملائك، ويحجز المواعيد، ويستقبل أكثر من مكالمة في نفس الوقت، ليل ونهار.",
    "hero.ctaTry": "جرّب مكالمة تجريبية",
    "hero.ctaContact": "اطلب وتر لنشاطك",
    "hero.stat1v": "٢٤/٧", "hero.stat1": "بدون مكالمات فائتة",
    "hero.stat2v": "سعودي", "hero.stat2": "بلهجة طبيعية، ويفهم المقاطعة",

    "pain.eyebrow": "المشكلة",
    "pain.title": "كل مكالمة ما تنرد، عميل يروح لغيرك.",
    "pain.p1t": "مكالمات ما تنرد",
    "pain.p1d": "بعد الدوام أو وقت الذروة، العميل ما يلقى أحد يرد، ويتصل على غيرك.",
    "pain.p2t": "مواعيد ما يحضرها أحد",
    "pain.p2d": "العميل ينسى موعده، والوقت يضيع، وعميل ثاني كان ممكن ياخذه.",
    "pain.p3t": "نفس الأسئلة كل يوم",
    "pain.p3d": "الأسعار، أوقات العمل، الخدمات، الموقع. وقت فريقك يروح في التكرار.",
    "demo.hint": "أنت تتصل بعيادة علاج طبيعي تجريبية. اضغط للبدء واسمح بالمايكروفون، وجرّب تحجز جلسة أو تسأل عن الأوقات المتاحة. مدة المكالمة حتى ٤ دقائق.",
    "demo.checking": "تتحقق من المواعيد…",
    "demo.busy": "الخطوط مشغولة حالياً، جرّب مرة ثانية بعد دقيقة.",
    "demo.idle": "جاهز",
    "demo.connecting": "جارٍ الاتصال…",
    "demo.live": "مباشر",
    "demo.ended": "انتهت المكالمة",
    "demo.preview": "محادثة نموذجية، ليست مكالمة مباشرة",
    "demo.micError": "تعذّر الوصول للمايكروفون. فعّل الإذن من إعدادات المتصفح.",
    "demo.connError": "تعذّر الاتصال حالياً، جرّب مرة ثانية بعد قليل.",
    "demo.you": "أنت",
    "demo.agent": "سارا",

    "how.eyebrow": "كيف يعمل",
    "how.title": "احنا نجهّزه عنك.",
    "how.s1t": "عرّفنا على نشاطك",
    "how.s1d": "أرسل لنا خدماتك وأسعارك وأوقات العمل، والموظف يرجع لها في كل مكالمة.",
    "how.s2t": "نضبطه على أسلوبك",
    "how.s2d": "نختار الصوت وطريقة الترحيب، ونحدد معك متى يحجز ومتى يحوّل لفريقك.",
    "how.s3t": "يبدأ يرد على رقمك",
    "how.s3d": "حوّل مكالماتك إلى وتر، وتابع ملخص ونتيجة كل مكالمة أول بأول.",
    "how.doc1": "الخدمات والأسعار",
    "how.doc2": "أوقات العمل",
    "how.doc3": "الأسئلة المتكررة",
    "how.ready": "جاهز",
    "how.chip1": "لهجة سعودية", "how.chip2": "صوت رسمي", "how.chip3": "صوت ودود", "how.chip4": "صوت هادئ",
    "how.line": "الخط الرئيسي",
    "how.live": "يعمل",
    "how.sumT": "ملخص المكالمة",
    "how.sumD": "حجز موعد الثلاثاء ١٠ص، وتم إرسال تأكيد للعميل.",

    "feat.eyebrow": "المزايا",
    "feat.title": "وش يسوي في كل مكالمة",
    "feat.f1t": "لهجة سعودية طبيعية",
    "feat.f1d": "يتكلم باللهجة السعودية بشكل طبيعي، ويتابع مع العميل حتى لو قاطعه أو غيّر رأيه.",
    "feat.f2t": "يحجز ويعدّل المواعيد",
    "feat.f2d": "يشوف الأوقات المتاحة، يحجز أو يغيّر أو يلغي، ويرسل للعميل تأكيد.",
    "feat.f3t": "يجاوب من معلوماتك",
    "feat.f3d": "يرد من خدماتك وأسعارك وسياساتك. وإذا ما لقى الإجابة، يقول للعميل ويسجّل طلبه.",
    "feat.f4t": "يحوّل لموظف من فريقك",
    "feat.f4d": "في الشكاوى والحالات الحساسة، يحوّل المكالمة ومعها ملخص كامل، فما يحتاج العميل يعيد كلامه.",
    "feat.f5t": "ملخص لكل مكالمة",
    "feat.f5d": "نص المكالمة وملخصها ونوع الطلب، ويبيّن لك العملاء غير الراضين.",
    "feat.f6t": "أكثر من مكالمة في نفس الوقت",
    "feat.f6d": "لا انتظار ولا خط مشغول، في وقت الذروة وبعد الدوام وفي الإجازات.",

    "ch.eyebrow": "القنوات",
    "ch.title": "وين يرد",
    "ch.t1": "المكالمات الواردة",
    "ch.t2": "المكالمات الصادرة",
    "ch.inbound.t": "يرد على رقمك الحالي",
    "ch.inbound.d": "حوّل كل مكالماتك إلى وتر، أو بس اللي خارج الدوام، أو لما يكون الخط مشغول.",
    "ch.outbound.t": "يذكّر عملاءك بمواعيدهم",
    "ch.outbound.d": "يتصل قبل الموعد، يأكد الحضور أو يغيّر الموعد، ويتابع مع العميل بعد الخدمة.",

    "faq.title": "الأسئلة الشائعة",

    "contact.eyebrow": "تواصل معنا",
    "contact.title": "خلّ وتر يرد على مكالمات نشاطك",
    // TODO: add a response time you can keep, e.g. "ونتواصل معك خلال يوم عمل".
    "contact.sub": "اترك بياناتك، ونتواصل معك نفهم طبيعة مكالماتك، ونجهّز وتر على خدماتك وأسعارك.",
    "contact.wa": "راسلنا على واتساب",
    "form.name": "الاسم",
    "form.company": "اسم النشاط",
    "form.phone": "رقم الجوال",
    "form.email": "البريد الإلكتروني",
    "form.message": "عرّفنا على نشاطك",
    "form.messagePh": "مثال: عيادة أسنان، نستقبل تقريباً ٢٠٠ مكالمة يومياً…",
    "form.error": "فضلاً اكتب اسمك وطريقة للتواصل معك (جوال أو بريد).",
    "form.emailInvalid": "البريد الإلكتروني غير صحيح، تأكد منه.",
    "form.send": "إرسال",
    "form.sending": "جارٍ الإرسال…",
    "form.success": "وصلتنا رسالتك، وبنتواصل معك قريباً.",
    "form.fail": "ما قدرنا نرسل رسالتك الحين. جرّب مرة ثانية، أو راسلنا على واتساب.",
    "form.subject": "طلب تواصل - وتر",

    "footer.tag": "موظف استقبال صوتي لنشاطك.",
    "footer.rights": "وتر. جميع الحقوق محفوظة."
  },

  en: {
    "nav.how": "How it works",
    "nav.features": "Features",
    "nav.channels": "Channels",
    "nav.faq": "FAQ",
    "nav.contact": "Contact",
    "nav.try": "Try a call",

    "hero.badge": "Try it with your voice now. No sign-up.",
    "hero.title": "A voice receptionist that answers every call, in your customers' dialect.",
    "hero.sub": "Watar answers your customers' questions, books appointments, and takes several calls at once, day or night.",
    "hero.ctaTry": "Try a demo call",
    "hero.ctaContact": "Get Watar for your business",
    "hero.stat1v": "24/7", "hero.stat1": "No missed calls",
    "hero.stat2v": "Saudi", "hero.stat2": "natural dialect, handles interruptions",

    "pain.eyebrow": "The problem",
    "pain.title": "Every unanswered call is a customer who goes elsewhere.",
    "pain.p1t": "Calls nobody answers",
    "pain.p1d": "After hours or at peak times, the customer can't get through and calls someone else.",
    "pain.p2t": "Appointments nobody shows up for",
    "pain.p2d": "The customer forgets, the time is wasted, and someone else could have had that slot.",
    "pain.p3t": "The same questions every day",
    "pain.p3d": "Prices, opening hours, services, location. Your team's time goes on repetition.",
    "demo.hint": "You're calling a sample physiotherapy clinic. Tap to start, allow the microphone, and try booking a session or asking what times are free. Calls last up to 4 minutes.",
    "demo.checking": "Checking the schedule…",
    "demo.busy": "All demo lines are busy. Try again in a minute.",
    "demo.idle": "Ready",
    "demo.connecting": "Connecting…",
    "demo.live": "Live",
    "demo.ended": "Call ended",
    "demo.preview": "Sample conversation, not a live call",
    "demo.micError": "Microphone access was blocked. Enable it in your browser settings.",
    "demo.connError": "Couldn't connect right now. Please try again shortly.",
    "demo.you": "You",
    "demo.agent": "Sara",

    "how.eyebrow": "How it works",
    "how.title": "We set it up for you.",
    "how.s1t": "Tell us about your business",
    "how.s1d": "Send us your services, prices and hours. The agent uses them on every call.",
    "how.s2t": "We tune it to your style",
    "how.s2d": "We pick the voice and greeting, and agree with you when it books and when it transfers to your team.",
    "how.s3t": "It starts answering your number",
    "how.s3d": "Forward your calls to Watar, and see each call's summary and outcome as it happens.",
    "how.doc1": "Services & prices",
    "how.doc2": "Opening hours",
    "how.doc3": "Common questions",
    "how.ready": "Ready",
    "how.chip1": "Saudi dialect", "how.chip2": "Formal voice", "how.chip3": "Friendly voice", "how.chip4": "Calm voice",
    "how.line": "Main line",
    "how.live": "Live",
    "how.sumT": "Call summary",
    "how.sumD": "Booked Tuesday 10am. Confirmation sent to the customer.",

    "feat.eyebrow": "Features",
    "feat.title": "What it does on every call",
    "feat.f1t": "Natural Saudi dialect",
    "feat.f1d": "Speaks natural Saudi Arabic, and keeps up when callers interrupt or change their mind.",
    "feat.f2t": "Books & reschedules",
    "feat.f2d": "Checks availability, books, moves or cancels appointments, and sends the customer a confirmation.",
    "feat.f3t": "Answers from your info",
    "feat.f3d": "Replies from your services, prices and policies. If the answer isn't there, it says so and takes a message.",
    "feat.f4t": "Transfers to your team",
    "feat.f4d": "For complaints and sensitive cases, it transfers the call with a full summary, so the caller doesn't repeat themselves.",
    "feat.f5t": "A summary of every call",
    "feat.f5d": "Transcript, summary and request type for each call, with unhappy callers flagged.",
    "feat.f6t": "Many calls at once",
    "feat.f6d": "No hold music and no busy tone, at peak hours, after hours and on holidays.",

    "ch.eyebrow": "Channels",
    "ch.title": "Where it answers",
    "ch.t1": "Inbound calls",
    "ch.t2": "Outbound calls",
    "ch.inbound.t": "Answers your current number",
    "ch.inbound.d": "Forward all your calls to Watar, only after-hours calls, or only when your line is busy.",
    "ch.outbound.t": "Reminds customers of their appointments",
    "ch.outbound.d": "Calls before the appointment, confirms attendance or moves the slot, and follows up afterwards.",

    "faq.title": "Common questions",

    "contact.eyebrow": "Contact us",
    "contact.title": "Let Watar answer your business calls",
    // TODO: add a response time you can keep, e.g. "We'll reply within one business day."
    "contact.sub": "Leave your details. We'll get in touch to learn how your calls work, then set Watar up with your services and prices.",
    "contact.wa": "Message us on WhatsApp",
    "form.name": "Name",
    "form.company": "Business name",
    "form.phone": "Mobile number",
    "form.email": "Email",
    "form.message": "Tell us about your business",
    "form.messagePh": "e.g. Dental clinic, we receive around 200 calls a day…",
    "form.error": "Please add your name and a way to reach you (mobile or email).",
    "form.emailInvalid": "That email address doesn't look right. Please check it.",
    "form.send": "Send",
    "form.sending": "Sending…",
    "form.success": "Thanks, we got your message and will be in touch soon.",
    "form.fail": "We couldn't send your message right now. Please try again, or message us on WhatsApp.",
    "form.subject": "Watar inquiry",

    "footer.tag": "Voice receptionist for your business.",
    "footer.rights": "Watar. All rights reserved."
  }
};

// FAQ items: objections only. Anything already explained above was removed.
window.WATAR_FAQ = {
  ar: [
    ["وش الأنشطة اللي يناسبها وتر؟", "أي نشاط يستقبل مكالمات كثيرة أو يحجز مواعيد. بدأنا بالقطاع الصحي، وإذا نشاطك في قطاع ثاني تواصل معنا ونشوف إذا يناسبك."],
    ["وش يصير إذا ما عرف يجاوب؟", "يقول للعميل بوضوح، ثم يحوّله لأحد من فريقك، أو يسجّل الطلب ويرسل لكم تذكرة متابعة مع ملخص المكالمة."],
    ["هل اللهجة السعودية طبيعية فعلاً؟", "نعم، يتكلم ويفهم اللهجة السعودية، ويتعامل مع المقاطعة وتغيير الكلام بشكل طبيعي. جرّبه بنفسك في المكالمة التجريبية أعلى الصفحة."],
    // TODO: confirm your disclosure policy, e.g.
    // ["هل يعرف العميل إنه يكلم ذكاء اصطناعي؟", "…"],
    // TODO: for healthcare clients, confirm the agent's behavior, e.g.
    // ["هل يعطي استشارات طبية؟", "لا. وتر يحجز ويجاوب على الأسئلة الإدارية، وأي سؤال طبي يحوّله لفريقك."],
    ["هل بيانات عملائي آمنة؟", "البيانات مشفّرة، ولا نستخدمها إلا لخدمة نشاطك."]
  ],
  en: [
    ["What kind of business is Watar for?", "Any business that gets a lot of calls or books appointments. We started with healthcare; if you're in another sector, get in touch and we'll see whether Watar fits."],
    ["What if it can't answer something?", "It tells the caller plainly, then transfers them to someone on your team, or logs the request and sends you a follow-up ticket with the call summary."],
    ["Does the Saudi dialect actually sound natural?", "Yes. It speaks and understands Saudi Arabic, and handles interruptions and changes of mind naturally. Try it yourself in the demo call at the top of the page."],
    // TODO: confirm your disclosure policy, e.g.
    // ["Will callers know they're talking to an AI?", "…"],
    // TODO: for healthcare clients, confirm the agent's behavior, e.g.
    // ["Does it give medical advice?", "No. Watar books appointments and answers administrative questions, and transfers any medical question to your team."],
    ["Is my customers' data safe?", "Data is encrypted, and used only to serve your business."]
  ]
};

// Sample conversations shown in the Channels section.
// Inbound and outbound calls only (the website call button channel was removed).
window.WATAR_CONVOS = {
  ar: {
    inbound: [["c", "السلام عليكم، حاب أحجز موعد بكرة الصباح"], ["a", "وعليكم السلام، حيّاك الله. عندنا موعد الساعة ١٠ الصباح، يناسبك؟"], ["c", "تمام، احجزه لي"], ["a", "تم الحجز. بيوصلك تأكيد برسالة الحين."]],
    outbound: [["a", "مساء الخير أستاذ خالد، معك سارا من عيادة النخبة. أذكّرك بموعدك بكرة الساعة ٤ العصر."], ["c", "أهلاً، أقدر أأجله لبعد بكرة؟"], ["a", "أكيد، متاح بعد بكرة الساعة ٤ أو ٦. أيهم يناسبك؟"], ["c", "الساعة ٦"]]
  },
  en: {
    inbound: [["c", "Hi, I'd like to book an appointment tomorrow morning."], ["a", "Hello, happy to help. We have 10am available. Does that work?"], ["c", "Perfect, book it."], ["a", "Done. You'll get a confirmation text right away."]],
    outbound: [["a", "Good evening Khalid, this is Sara from Elite Clinic. Just a reminder of your appointment tomorrow at 4pm."], ["c", "Hi, can I move it to the day after?"], ["a", "Of course. 4pm or 6pm are open. Which suits you?"], ["c", "6pm, please."]]
  }
};
