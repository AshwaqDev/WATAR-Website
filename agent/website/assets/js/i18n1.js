// All site text in Arabic and English. Edit freely.
//
// Copy revision notes
// - Each section now does one job; repeated promises were cut.
// - Arabic marketing copy uses light Saudi colloquial; UI messages stay neutral.
// - The agent persona is "Sara" everywhere; "Watar" is the product name only.
// - Search for "TODO" to find facts only you can confirm (price, data, integrations).

window.WATAR_I18N = {
  ar: {
    "nav.how": "كيف يعمل",
    "nav.features": "المزايا",
    "nav.channels": "القنوات",
    "nav.faq": "الأسئلة الشائعة",
    "nav.contact": "تواصل معنا",
    "nav.try": "جرّب مكالمة",

    "hero.badge": "تجربة مباشرة، بدون تسجيل",
    "hero.title": "موظف صوتي ذكي يرد على كل مكالمة، بلهجة عملائك.",
    // TODO: if your main market is clinics, add it here, e.g. "…لعيادتك".
    "hero.sub": "وتر يجاوب على الاستفسارات، يحجز المواعيد، ويستقبل أكثر من مكالمة في نفس الوقت، ليل ونهار. وإذا احتاج العميل موظف، يحوّله لفريقك.",
    "hero.ctaTry": "جرّب مكالمة تجريبية",
    "hero.ctaContact": "اطلب تجربة على نشاطك",
    "hero.stat1v": "٢٤/٧", "hero.stat1": "بدون مكالمات فائتة",
    "hero.stat2v": "عدة", "hero.stat2": "مكالمات في نفس الوقت",
    "hero.stat3v": "٤", "hero.stat3": "سعودي، خليجي، فصحى، إنجليزي",

    "demo.tabWeb": "تحدّث من المتصفح",
    "demo.tabPhone": "اتصل على الرقم",
    "demo.hint": "أنت تتصل بعيادة علاج طبيعي تجريبية، والموظفة تتكلم باللهجة السعودية. اضغط للبدء واسمح بالمايكروفون، وجرّب تحجز جلسة أو تسأل عن الأوقات المتاحة. مدة المكالمة حتى ٤ دقائق.",
    "demo.checking": "تتحقق من المواعيد…",
    "demo.busy": "الخطوط مشغولة حالياً، جرّب بعد دقيقة أو اتصل على الرقم.",
    "demo.idle": "جاهز",
    "demo.connecting": "جارٍ الاتصال…",
    "demo.live": "مباشر",
    "demo.ended": "انتهت المكالمة",
    "demo.preview": "محادثة نموذجية، ليست مكالمة مباشرة",
    "demo.micError": "تعذّر الوصول للمايكروفون. فعّل الإذن من إعدادات المتصفح.",
    "demo.connError": "تعذّر الاتصال حالياً. جرّب الاتصال على الرقم.",
    "demo.you": "أنت",
    "demo.agent": "سارا",
    "demo.phoneEyebrow": "اتصل وجرّب بنفسك",
    "demo.phoneSub": "نفس الموظفة، على خط هاتف حقيقي. جرّب:",
    "demo.phoneCta": "اتصل الآن",
    "demo.tip1": "احجز جلسة علاج طبيعي",
    "demo.tip2": "اسأل عن الأخصائيين والأوقات المتاحة",
    "demo.tip3": "احجز جلسة لطفلك",

    "how.eyebrow": "كيف يعمل",
    "how.title": "جاهز خلال أيام.",
    "how.s1t": "عرّفنا على نشاطك",
    "how.s1d": "أرسل لنا خدماتك وأسعارك وأوقات العمل وسياسات الحجز، والموظف يرجع لها أثناء كل مكالمة.",
    "how.s2t": "نضبطه على أسلوبك",
    "how.s2d": "نختار الصوت واللهجة وطريقة الترحيب، ونحدد معك متى يحجز ومتى يحوّل لفريقك.",
    "how.s3t": "يبدأ يرد على رقمك",
    "how.s3d": "حوّل مكالماتك إلى وتر، وتابع ملخص ونتيجة كل مكالمة أول بأول.",
    "how.doc1": "الخدمات والأسعار",
    "how.doc2": "أوقات العمل",
    "how.doc3": "الأسئلة المتكررة",
    "how.ready": "جاهز",
    "how.chip1": "لهجة سعودية", "how.chip2": "فصحى", "how.chip3": "English", "how.chip4": "صوت هادئ",
    "how.line": "الخط الرئيسي",
    "how.live": "يعمل",
    "how.sumT": "ملخص المكالمة",
    "how.sumD": "حجز موعد الثلاثاء ١٠ص، وتم إرسال تأكيد للعميل.",

    "feat.eyebrow": "المزايا",
    "feat.title": "وش يسوي في كل مكالمة",
    "feat.f1t": "يتكلم بلهجة عميلك",
    "feat.f1d": "سعودي وخليجي وفصحى وإنجليزي، ويتابع مع العميل حتى لو قاطعه أو غيّر رأيه.",
    "feat.f2t": "يحجز ويعدّل المواعيد",
    "feat.f2d": "يشوف الأوقات المتاحة، يحجز أو يغيّر أو يلغي، ويرسل للعميل رسالة تأكيد.",
    "feat.f3t": "يجاوب من معلوماتك",
    "feat.f3d": "يرد من ملفاتك وأسعارك وسياساتك. وإذا ما لقى الإجابة، يقول للعميل ويسجّل طلبه.",
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
    "ch.t3": "زر الاتصال في موقعك",
    "ch.inbound.t": "يرد على رقمك الحالي",
    "ch.inbound.d": "حوّل كل مكالماتك إلى وتر، أو بس اللي خارج الدوام، أو لما يكون الخط مشغول.",
    "ch.outbound.t": "يتصل بعملائك عنك",
    "ch.outbound.d": "تذكير بالمواعيد، تأكيد الطلبات، والمتابعة بعد الخدمة.",
    "ch.web.t": "مكالمة بضغطة من موقعك",
    "ch.web.d": "زر في موقعك يخلّي الزائر يتكلم مباشرة من المتصفح، بدون رقم وبدون انتظار.",

    "faq.title": "الأسئلة الشائعة",

    "contact.eyebrow": "تواصل معنا",
    "contact.title": "جرّب وتر على بيانات نشاطك",
    // TODO: add a response time you can keep, e.g. "ونتواصل معك خلال يوم عمل".
    "contact.sub": "اترك بياناتك، ونتواصل معك نفهم طبيعة مكالماتك، ونجهّز لك نسخة تجريبية بخدماتك وأسعارك.",
    "contact.wa": "راسلنا على واتساب",
    "form.name": "الاسم",
    "form.company": "اسم النشاط",
    "form.phone": "رقم الجوال",
    "form.email": "البريد الإلكتروني",
    "form.message": "عرّفنا على نشاطك",
    "form.messagePh": "مثال: عيادة أسنان، نستقبل تقريباً ٢٠٠ مكالمة يومياً…",
    "form.sendWa": "إرسال عبر واتساب",
    "form.sendMail": "إرسال عبر البريد",
    "form.error": "فضلاً اكتب اسمك وطريقة للتواصل معك (جوال أو بريد).",
    "form.subject": "طلب تجربة وتر",

    "footer.tag": "موظف صوتي ذكي لنشاطك التجاري.",
    "footer.rights": "وتر. جميع الحقوق محفوظة."
  },

  en: {
    "nav.how": "How it works",
    "nav.features": "Features",
    "nav.channels": "Channels",
    "nav.faq": "FAQ",
    "nav.contact": "Contact",
    "nav.try": "Try a call",

    "hero.badge": "Live demo, no sign-up",
    "hero.title": "A voice agent that answers every call, in your customers' dialect.",
    // TODO: if your main market is clinics, say so here.
    "hero.sub": "Watar answers questions, books appointments, and takes several calls at once, day or night. When a caller needs a person, it transfers them to your team.",
    "hero.ctaTry": "Try a demo call",
    "hero.ctaContact": "Request a custom demo",
    "hero.stat1v": "24/7", "hero.stat1": "No missed calls",
    "hero.stat2v": "Many", "hero.stat2": "calls at the same time",
    "hero.stat3v": "4", "hero.stat3": "Saudi, Gulf, formal Arabic, English",

    "demo.tabWeb": "Talk in browser",
    "demo.tabPhone": "Call the number",
    "demo.hint": "You're calling a sample physiotherapy clinic; the agent speaks Saudi Arabic. Tap to start, allow the microphone, and try booking a session or asking what times are free. Calls last up to 4 minutes.",
    "demo.checking": "Checking the schedule…",
    "demo.busy": "All demo lines are busy. Try again in a minute, or call the number.",
    "demo.idle": "Ready",
    "demo.connecting": "Connecting…",
    "demo.live": "Live",
    "demo.ended": "Call ended",
    "demo.preview": "Sample conversation, not a live call",
    "demo.micError": "Microphone access was blocked. Enable it in your browser settings.",
    "demo.connError": "Couldn't connect right now. Try calling the number instead.",
    "demo.you": "You",
    "demo.agent": "Sara",
    "demo.phoneEyebrow": "Call and try it yourself",
    "demo.phoneSub": "The same agent, on a real phone line. Try:",
    "demo.phoneCta": "Call now",
    "demo.tip1": "Book a physiotherapy session",
    "demo.tip2": "Ask which therapists and times are available",
    "demo.tip3": "Book a session for your child",

    "how.eyebrow": "How it works",
    "how.title": "Live in a few days.",
    "how.s1t": "Tell us about your business",
    "how.s1d": "Send us your services, prices, hours and booking rules. The agent uses them on every call.",
    "how.s2t": "We tune it to your style",
    "how.s2d": "We pick the voice, dialect and greeting, and agree with you when it books and when it transfers to your team.",
    "how.s3t": "It starts answering your number",
    "how.s3d": "Forward your calls to Watar, and see each call's summary and outcome as it happens.",
    "how.doc1": "Services & prices",
    "how.doc2": "Opening hours",
    "how.doc3": "Common questions",
    "how.ready": "Ready",
    "how.chip1": "Saudi dialect", "how.chip2": "Formal Arabic", "how.chip3": "English", "how.chip4": "Calm voice",
    "how.line": "Main line",
    "how.live": "Live",
    "how.sumT": "Call summary",
    "how.sumD": "Booked Tuesday 10am. Confirmation sent to the customer.",

    "feat.eyebrow": "Features",
    "feat.title": "What it does on every call",
    "feat.f1t": "Speaks your caller's dialect",
    "feat.f1d": "Saudi, Gulf, formal Arabic and English, and it keeps up when callers interrupt or change their mind.",
    "feat.f2t": "Books & reschedules",
    "feat.f2d": "Checks availability, books, moves or cancels appointments, and texts the customer a confirmation.",
    "feat.f3t": "Answers from your info",
    "feat.f3d": "Replies from your documents, prices and policies. If the answer isn't there, it says so and takes a message.",
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
    "ch.t3": "Website call button",
    "ch.inbound.t": "Answers your current number",
    "ch.inbound.d": "Forward all your calls to Watar, only after-hours calls, or only when your line is busy.",
    "ch.outbound.t": "Calls your customers for you",
    "ch.outbound.d": "Appointment reminders, order confirmations and after-service follow-ups.",
    "ch.web.t": "One tap to call from your site",
    "ch.web.d": "A button on your website lets visitors talk straight from the browser, with no number to dial and no wait.",

    "faq.title": "Common questions",

    "contact.eyebrow": "Contact us",
    "contact.title": "Get a demo built on your business",
    // TODO: add a response time you can keep, e.g. "We'll reply within one business day."
    "contact.sub": "Leave your details. We'll get in touch to learn how your calls work, then build a demo with your own services and prices.",
    "contact.wa": "Message us on WhatsApp",
    "form.name": "Name",
    "form.company": "Business name",
    "form.phone": "Mobile number",
    "form.email": "Email",
    "form.message": "Tell us about your business",
    "form.messagePh": "e.g. Dental clinic, we receive around 200 calls a day…",
    "form.sendWa": "Send via WhatsApp",
    "form.sendMail": "Send via email",
    "form.error": "Please add your name and a way to reach you (mobile or email).",
    "form.subject": "Watar demo request",

    "footer.tag": "AI voice agent for your business.",
    "footer.rights": "Watar. All rights reserved."
  }
};

// FAQ items: objections only. Anything already explained above was removed.
window.WATAR_FAQ = {
  ar: [
    ["وش يصير إذا ما عرف يجاوب؟", "يقول للعميل بوضوح، ثم يحوّله لأحد من فريقك، أو يسجّل الطلب ويرسل لكم تذكرة متابعة مع ملخص المكالمة."],
    ["هل اللهجة السعودية طبيعية فعلاً؟", "هي اللهجة الأساسية للموظف. جرّبها بنفسك في المكالمة التجريبية أعلى الصفحة."],
    ["كم يأخذ التجهيز؟", "غالباً أيام قليلة: نجمع معلومات نشاطك، نضبط الموظف، ونجرّبه معك قبل ما يبدأ يرد على عملائك."],
    // TODO: confirm and add which booking systems you connect to, e.g.
    // ["هل يرتبط بنظام الحجز عندي؟", "نعم، يرتبط مع …، وإذا نظامك غير مدعوم نجهّز لك …"],
    // TODO: confirm your disclosure policy, e.g.
    // ["هل يعرف العميل إنه يكلم ذكاء اصطناعي؟", "…"],
    // TODO: replace with specifics you can stand behind: where data is stored, PDPL compliance, retention.
    ["هل بيانات عملائي آمنة؟", "المكالمات والبيانات مشفّرة، ولا نستخدمها إلا لخدمة نشاطك."],
    // TODO: add a starting price if you can, e.g. "تبدأ الباقات من … ريال شهرياً".
    ["كم التكلفة؟", "باقات شهرية حسب عدد المكالمات. أرسل لنا عدد مكالماتك اليومية تقريباً، ونرسل لك السعر."]
  ],
  en: [
    ["What if it can't answer something?", "It tells the caller plainly, then transfers them to someone on your team, or logs the request and sends you a follow-up ticket with the call summary."],
    ["Does the Saudi dialect actually sound natural?", "It's the agent's main dialect. Try it yourself in the demo call at the top of the page."],
    ["How long does setup take?", "Usually a few days: we collect your business info, tune the agent and test it with you before it answers your customers."],
    // TODO: confirm and add which booking systems you connect to, e.g.
    // ["Does it connect to my booking system?", "Yes, it works with … If yours isn't supported, we …"],
    // TODO: confirm your disclosure policy, e.g.
    // ["Will callers know they're talking to an AI?", "…"],
    // TODO: replace with specifics you can stand behind: where data is stored, PDPL compliance, retention.
    ["Is my customers' data safe?", "Calls and data are encrypted, and used only to serve your business."],
    // TODO: add a starting price if you can, e.g. "Plans start from … SAR a month."
    ["How much does it cost?", "Monthly plans based on call volume. Send us roughly how many calls you get a day, and we'll send you a price."]
  ]
};

// Sample conversations shown in the Channels section
window.WATAR_CONVOS = {
  ar: {
    inbound: [["c", "السلام عليكم، حاب أحجز موعد بكرة الصباح"], ["a", "وعليكم السلام، حيّاك الله. عندنا موعد الساعة ١٠ الصباح، يناسبك؟"], ["c", "تمام، احجزه لي"], ["a", "تم الحجز. بيوصلك تأكيد برسالة الحين."]],
    outbound: [["a", "مساء الخير أستاذ خالد، معك سارا من عيادة النخبة. أذكّرك بموعدك بكرة الساعة ٤ العصر."], ["c", "أهلاً، أقدر أأجله لبعد بكرة؟"], ["a", "أكيد، متاح بعد بكرة الساعة ٤ أو ٦. أيهم يناسبك؟"], ["c", "الساعة ٦"]],
    web: [["c", "كم سعر تنظيف الأسنان؟"], ["a", "سعر التنظيف ٢٥٠ ريال، ويشمل الفحص. تحب أحجز لك موعد؟"], ["c", "إيه، يوم الخميس"], ["a", "متاح الخميس ١١ الصباح أو ٣ العصر."]]
  },
  en: {
    inbound: [["c", "Hi, I'd like to book an appointment tomorrow morning."], ["a", "Hello, happy to help. We have 10am available. Does that work?"], ["c", "Perfect, book it."], ["a", "Done. You'll get a confirmation text right away."]],
    outbound: [["a", "Good evening Khalid, this is Sara from Elite Clinic. Just a reminder of your appointment tomorrow at 4pm."], ["c", "Hi, can I move it to the day after?"], ["a", "Of course. 4pm or 6pm are open. Which suits you?"], ["c", "6pm, please."]],
    web: [["c", "How much is a teeth cleaning?"], ["a", "Cleaning is 250 SAR, including a check-up. Shall I book you in?"], ["c", "Yes, on Thursday."], ["a", "Thursday has 11am or 3pm available."]]
  }
};
