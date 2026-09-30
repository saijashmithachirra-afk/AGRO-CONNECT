// AgroConnect Multilingual Chatbot
const FAQS = {
  en: [
    { keys: ['order', 'buy', 'purchase', 'how to order'], answer: "To order: 1) Browse products in Marketplace 2) Add items to cart 3) Set delivery location 4) Choose payment method 5) Confirm order! 🛒", chips: ['Track order', 'Payment methods', 'Coupons'] },
    { keys: ['track', 'tracking', 'where is my order', 'delivery status'], answer: "Go to Marketplace → My Account → Your Orders → Click 'Track' button. You'll see a live map with 5 delivery steps! 📍", chips: ['My orders', 'Delivery time', 'Contact support'] },
    { keys: ['coupon', 'discount', 'promo', 'offer', 'FIRST25'], answer: "Use code FIRST25 for 25% off your first order! Enter it in cart before checkout. More offers coming soon! 🎉", chips: ['How to order', 'Payment methods'] },
    { keys: ['payment', 'pay', 'upi', 'card', 'cash', 'net banking'], answer: "We accept: 📱 UPI/GPay/PhonePe, 💳 Credit/Debit Card, 🏦 Net Banking, 💵 Cash on Delivery (COD). All payments are secure!", chips: ['Order now', 'Coupons', 'Delivery'] },
    { keys: ['register', 'signup', 'create account', 'join'], answer: "Click 'Login / Register' in navbar → Register tab → Fill details → Get OTP on screen → Verify → Done! 🎊", chips: ['Login help', 'Farmer registration'] },
    { keys: ['farmer', 'sell', 'list product', 'selling'], answer: "Farmers: 1) Register with role = Farmer 2) Add bank account in Profile 3) Go to Farmer Dashboard 4) Add products with AI price suggestion! 🌾", chips: ['Bank account', 'AI pricing', 'How to register'] },
    { keys: ['bank', 'account', 'payment receive', 'ifsc', 'upi id'], answer: "Go to Farmer Dashboard → Profile tab → Add Bank Account details. This is required before listing products. ✅", chips: ['Add product', 'Dashboard help'] },
    { keys: ['language', 'hindi', 'tamil', 'telugu', 'translate'], answer: "Click EN | हि | த | తె buttons in the navbar to switch language. All content will translate automatically! 🌐", chips: ['How to order', 'Contact support'] },
    { keys: ['support', 'help', 'contact', 'problem', 'issue'], answer: "Use the Support section at the bottom of Marketplace page to send a message to our team. We reply within 24 hours! 💬", chips: ['Send message', 'Track order'] },
    { keys: ['pre-harvest', 'advance booking', 'future crop'], answer: "Pre-harvest products let you book crops before they're harvested. Look for the orange 'Pre-Harvest' badge on products! 🌱", chips: ['Browse products', 'How to order'] },
    { keys: ['ai price', 'ai', 'suggested price', 'pricing'], answer: "Our AI analyzes Indian mandi rates, location, season & demand to suggest optimal prices for farmers. It's free! 🤖", chips: ['Farmer features', 'How to sell'] },
    { keys: ['delivery', 'shipping', 'when', 'days'], answer: "Estimated delivery is 3-5 days after order confirmation. You can track your order in real-time on the map! 🚚", chips: ['Track order', 'Payment methods'] },
    { keys: ['cancel', 'return', 'refund'], answer: "To cancel an order, contact our support team immediately. Refunds are processed within 3-5 business days for online payments.", chips: ['Contact support', 'Track order'] },
    { keys: ['fresh', 'quality', 'organic'], answer: "All products are directly sourced from verified farmers! Look for 'Organic' in product descriptions for certified produce. 🌿", chips: ['Browse products', 'How to order'] },
    { keys: ['hello', 'hi', 'hey', 'namaste', 'help me'], answer: "Hello! 👋 Welcome to AgroConnect! I can help you with ordering, tracking, payments, farmer features, and more. What do you need?", chips: ['How to order', 'Track order', 'Payment methods', 'Farmer features'] },
  ],
  hi: [
    { keys: ['ऑर्डर', 'खरीदें', 'कैसे खरीदें', 'order kaise'], answer: "ऑर्डर करने के लिए: 1) मार्केटप्लेस में उत्पाद देखें 2) कार्ट में जोड़ें 3) डिलीवरी स्थान सेट करें 4) भुगतान विधि चुनें! 🛒", chips: ['ट्रैकिंग', 'भुगतान', 'कूपन'] },
    { keys: ['ट्रैक', 'कहाँ है', 'डिलीवरी'], answer: "मार्केटप्लेस → मेरा खाता → मेरे ऑर्डर → ट्रैक बटन दबाएं। लाइव मैप में देखें! 📍", chips: ['ऑर्डर करें', 'सहायता'] },
    { keys: ['कूपन', 'छूट', 'FIRST25', 'ऑफर'], answer: "FIRST25 कोड से पहले ऑर्डर पर 25% छूट! कार्ट में दर्ज करें। 🎉", chips: ['ऑर्डर करें', 'भुगतान'] },
    { keys: ['भुगतान', 'UPI', 'कार्ड', 'नकद'], answer: "हम स्वीकार करते हैं: 📱 UPI/GPay, 💳 कार्ड, 🏦 नेट बैंकिंग, 💵 COD। सभी भुगतान सुरक्षित! ✅", chips: ['ऑर्डर करें', 'कूपन'] },
    { keys: ['रजिस्टर', 'अकाउंट बनाएं', 'ज्वाइन'], answer: "नेवबार में 'लॉगिन / रजिस्टर' → रजिस्टर टैब → विवरण भरें → OTP से सत्यापित करें! 🎊", chips: ['किसान पंजीकरण', 'लॉगिन'] },
    { keys: ['किसान', 'बेचें', 'फसल'], answer: "किसान: 1) किसान रोल से रजिस्टर करें 2) बैंक खाता जोड़ें 3) डैशबोर्ड में उत्पाद जोड़ें! 🌾", chips: ['बैंक खाता', 'AI मूल्य'] },
    { keys: ['नमस्ते', 'हेलो', 'मदद'], answer: "नमस्ते! 👋 AgroConnect में आपका स्वागत है। मैं आपकी मदद कर सकता हूँ!", chips: ['ऑर्डर करें', 'ट्रैकिंग', 'भुगतान'] },
  ],
  ta: [
    { keys: ['ஆர்டர்', 'வாங்க', 'எப்படி வாங்குவது'], answer: "ஆர்டர் செய்ய: 1) மார்க்கெட்டில் பொருட்கள் பாருங்கள் 2) கார்ட்டில் சேர்க்கவும் 3) டெலிவரி இடம் தேர்வு செய்யுங்கள்! 🛒", chips: ['தொடர்', 'கட்டணம்', 'கூப்பன்'] },
    { keys: ['கூப்பன்', 'தள்ளுபடி', 'FIRST25'], answer: "FIRST25 குறியீட்டைப் பயன்படுத்தி முதல் ஆர்டரில் 25% தள்ளுபடி பெறுங்கள்! 🎉", chips: ['ஆர்டர்', 'கட்டணம்'] },
    { keys: ['வணக்கம்', 'ஹலோ', 'உதவி'], answer: "வணக்கம்! 👋 AgroConnect-க்கு வரவேற்கிறோம். நான் உங்களுக்கு உதவ தயாராக இருக்கிறேன்!", chips: ['ஆர்டர்', 'கட்டணம்', 'விவசாயி'] },
    { keys: ['விவசாயி', 'விற்க', 'பயிர்'], answer: "விவசாயி: 1) விவசாயி பாத்திரத்தில் பதிவு செய்யுங்கள் 2) வங்கி கணக்கு சேர்க்கவும் 3) டாஷ்போர்டில் பொருட்கள் சேர்க்கவும்! 🌾", chips: ['வங்கி', 'AI விலை'] },
  ],
  te: [
    { keys: ['ఆర్డర్', 'కొనుగోలు', 'ఎలా కొనాలి'], answer: "ఆర్డర్ చేయడానికి: 1) మార్కెట్‌లో పొందు 2) కార్ట్‌కు జోడించు 3) డెలివరీ స్థానం సెట్ చేయి! 🛒", chips: ['ట్రాక్', 'చెల్లింపు', 'కూపన్'] },
    { keys: ['కూపన్', 'తగ్గింపు', 'FIRST25'], answer: "FIRST25 కోడ్ తో మొదటి ఆర్డర్‌లో 25% తగ్గింపు పొందండి! 🎉", chips: ['ఆర్డర్', 'చెల్లింపు'] },
    { keys: ['నమస్కారం', 'హలో', 'సహాయం'], answer: "నమస్కారం! 👋 AgroConnect కి స్వాగతం. నేను మీకు సహాయం చేయడానికి సిద్ధంగా ఉన్నాను!", chips: ['ఆర్డర్', 'చెల్లింపు', 'రైతు'] },
    { keys: ['రైతు', 'అమ్ముట', 'పంట'], answer: "రైతు: 1) రైతు పాత్రతో నమోదు చేయండి 2) బ్యాంక్ ఖాతా జోడించండి 3) డాష్‌బోర్డ్‌లో ఉత్పత్తులు జోడించండి! 🌾", chips: ['బ్యాంక్', 'AI ధర'] },
  ]
};

function initChatbot() {
  const btn = document.getElementById('chatbot-btn');
  const panel = document.getElementById('chatbot-panel');
  const messages = document.getElementById('chatbot-messages');
  const input = document.getElementById('chatbot-input');
  const sendBtn = document.getElementById('chatbot-send');

  if (!btn || !panel) return;

  btn.addEventListener('click', () => {
    panel.style.display = panel.style.display === 'flex' ? 'none' : 'flex';
    if (panel.style.display === 'flex' && messages.children.length === 0) {
      addBotMessage(getGreeting(), ['How to order', 'Track order', 'Payment methods', 'Farmer features']);
    }
  });

  sendBtn?.addEventListener('click', () => sendMessage());
  input?.addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });

  function getGreeting() {
    const lang = currentLang || 'en';
    const greetings = {
      en: "Hello! 👋 I'm AgriBot, your AgroConnect assistant! How can I help you today?",
      hi: "नमस्ते! 👋 मैं AgriBot हूँ। आपकी क्या मदद कर सकता हूँ?",
      ta: "வணக்கம்! 👋 நான் AgriBot. உங்களுக்கு எப்படி உதவலாம்?",
      te: "నమస్కారం! 👋 నేను AgriBot. మీకు ఎలా సహాయం చేయగలను?"
    };
    return greetings[lang] || greetings.en;
  }

  function sendMessage(text) {
    const msg = text || input.value.trim();
    if (!msg) return;
    if (input) input.value = '';
    addUserMessage(msg);
    setTimeout(() => {
      const response = findAnswer(msg);
      addBotMessage(response.answer, response.chips);
    }, 600);
  }

  function findAnswer(query) {
    const q = query.toLowerCase();
    const lang = currentLang || 'en';
    const faqs = FAQS[lang] || FAQS.en;

    for (const faq of faqs) {
      if (faq.keys.some(k => q.includes(k.toLowerCase()))) {
        return { answer: faq.answer, chips: faq.chips || [] };
      }
    }
    // Try English as fallback
    if (lang !== 'en') {
      for (const faq of FAQS.en) {
        if (faq.keys.some(k => q.includes(k.toLowerCase()))) {
          return { answer: faq.answer, chips: faq.chips || [] };
        }
      }
    }

    const defaults = {
      en: "I'm not sure about that. Try asking about ordering, payments, tracking, or farmer features! 🤔",
      hi: "मुझे यह नहीं पता। ऑर्डर, भुगतान, या किसान सुविधाओं के बारे में पूछें!",
      ta: "அது தெரியவில்லை. ஆர்டர், கட்டணம் பற்றி கேளுங்கள்!",
      te: "తెలియదు. ఆర్డర్, చెల్లింపు గురించి అడగండి!"
    };
    return { answer: defaults[lang] || defaults.en, chips: ['How to order', 'Contact support'] };
  }

  function addBotMessage(text, chips = []) {
    const div = document.createElement('div');
    div.className = 'chat-msg bot';
    let chipHtml = '';
    if (chips.length) {
      chipHtml = `<div class="chat-chips">${chips.map(c => `<span class="chat-chip" onclick="chatSendChip('${c}')">${c}</span>`).join('')}</div>`;
    }
    div.innerHTML = `<div class="bubble">${text}</div>${chipHtml}`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'chat-msg user';
    div.innerHTML = `<div class="bubble">${text}</div>`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  window.chatSendChip = (text) => {
    if (input) input.value = text;
    const div = document.querySelector('#chatbot-panel .chat-msg.user:last-child');
    sendMessage(text);
  };
}

setTimeout(initChatbot, 2000);
