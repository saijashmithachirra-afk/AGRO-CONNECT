// ─── Auth ─────────────────────────────────────────────────────────────────────
const Auth = {
  getToken: () => localStorage.getItem('agro_token'),
  getUser: () => { try { return JSON.parse(localStorage.getItem('agro_user')); } catch { return null; } },
  setAuth: (token, user) => { localStorage.setItem('agro_token', token); localStorage.setItem('agro_user', JSON.stringify(user)); },
  clear: () => { localStorage.removeItem('agro_token'); localStorage.removeItem('agro_user'); },
  headers: () => { const t = Auth.getToken(); return t ? { 'Authorization': `Bearer ${t}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }; }
};

// ─── API Helper ───────────────────────────────────────────────────────────────
const API = {
  get: async (url) => {
    const r = await fetch(url, { headers: Auth.headers() });
    if (!r.ok) { const e = await r.json().catch(() => ({ detail: 'Request failed' })); throw new Error(e.detail || 'Request failed'); }
    return r.json();
  },
  post: async (url, data) => {
    const r = await fetch(url, { method: 'POST', headers: Auth.headers(), body: JSON.stringify(data) });
    if (!r.ok) { const e = await r.json().catch(() => ({ detail: 'Request failed' })); throw new Error(e.detail || 'Request failed'); }
    return r.json();
  },
  put: async (url, data) => {
    const r = await fetch(url, { method: 'PUT', headers: Auth.headers(), body: JSON.stringify(data) });
    if (!r.ok) { const e = await r.json().catch(() => ({ detail: 'Request failed' })); throw new Error(e.detail || 'Request failed'); }
    return r.json();
  },
  delete: async (url) => {
    const r = await fetch(url, { method: 'DELETE', headers: Auth.headers() });
    if (!r.ok) { const e = await r.json().catch(() => ({ detail: 'Request failed' })); throw new Error(e.detail || 'Request failed'); }
    return r.json();
  }
};

// ─── Toast ────────────────────────────────────────────────────────────────────
function showToast(msg, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible shadow`;
  toast.style.cssText = 'min-width:260px;animation:fadeIn 0.3s;';
  toast.innerHTML = `${msg}<button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// ─── Modal Helper ─────────────────────────────────────────────────────────────
function showModal(id) {
  const el = document.getElementById(id);
  if (!el) return;
  const m = bootstrap.Modal.getInstance(el) || new bootstrap.Modal(el);
  m.show();
}
function hideModal(id) {
  const el = document.getElementById(id);
  if (!el) return;
  const m = bootstrap.Modal.getInstance(el);
  if (m) m.hide();
}

// ─── Navbar Auth ──────────────────────────────────────────────────────────────
function updateNavAuth() {
  const user = Auth.getUser();
  document.querySelectorAll('.nav-login').forEach(el => {
    el.style.display = user ? 'none' : 'inline-flex';
  });
  document.querySelectorAll('.nav-logout').forEach(el => {
    el.classList.toggle('d-none', !user);
    el.style.display = user ? 'flex' : 'none';
  });
  document.querySelectorAll('.nav-user-name').forEach(el => {
    if (user) el.textContent = user.name;
  });
  document.querySelectorAll('.nav-role-badge').forEach(el => {
    if (user) el.textContent = user.role;
  });
  document.querySelectorAll('.nav-dashboard').forEach(el => {
    if (user) {
      const url = user.role === 'farmer' ? '/farmer-dashboard'
                : user.role === 'admin'  ? '/admin-dashboard'
                : '/marketplace';
      el.href = url;
      el.onclick = null;
    } else {
      el.href = '#';
      el.onclick = (e) => { e.preventDefault(); showModal('loginModal'); };
    }
  });
}

// ─── Logout ───────────────────────────────────────────────────────────────────
function doLogout() {
  Auth.clear();
  updateNavAuth();
  showToast('Logged out successfully');
  setTimeout(() => window.location.href = '/', 500);
}

// ─── Cart Count ───────────────────────────────────────────────────────────────
async function updateCartCount() {
  const user = Auth.getUser();
  if (!user) { document.querySelectorAll('.cart-badge').forEach(b => b.textContent = '0'); return; }
  try {
    const items = await API.get('/api/cart');
    document.querySelectorAll('.cart-badge').forEach(b => b.textContent = items.length);
  } catch { }
}

// ─── Login Panel ──────────────────────────────────────────────────────────────
async function doLogin(e) {
  if (e) e.preventDefault();
  const email = document.getElementById('loginEmail')?.value;
  const password = document.getElementById('loginPassword')?.value;
  const btn = document.getElementById('loginBtn');
  if (!email || !password) return showToast('Enter email and password', 'error');
  if (btn) { btn.disabled = true; btn.textContent = 'Logging in...'; }
  try {
    const res = await API.post('/api/auth/login', { email, password });
    Auth.setAuth(res.token, res.user);
    updateNavAuth();
    updateCartCount();
    hideModal('loginModal');
    showToast(`Welcome back, ${res.user.name}! 🌾`);
    if (res.user.role === 'farmer') setTimeout(() => window.location.href = '/farmer-dashboard', 600);
    else if (res.user.role === 'admin') setTimeout(() => window.location.href = '/admin-dashboard', 600);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Login'; }
  }
}

// ─── Register / OTP ──────────────────────────────────────────────────────────
let otpEmail = '';
async function sendOTP() {
  const name = document.getElementById('regName')?.value?.trim();
  const email = document.getElementById('regEmail')?.value?.trim();
  const phone = document.getElementById('regPhone')?.value?.trim();
  const password = document.getElementById('regPassword')?.value;
  const role = document.getElementById('regRole')?.value;
  const location = document.getElementById('regLocation')?.value?.trim();
  if (!name || !email || !password) return showToast('Fill all required fields', 'error');
  if (password.length < 6) return showToast('Password must be 6+ characters', 'error');
  const btn = document.getElementById('sendOtpBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }
  try {
    const res = await API.post('/api/auth/send-otp', { name, email, phone, password, role, location });
    otpEmail = email;
    document.getElementById('demoOtp').textContent = res.otp_demo;
    document.getElementById('regPanel').style.display = 'none';
    document.getElementById('otpPanel').style.display = 'block';
    showToast('OTP sent! (Demo: shown on screen)');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Send OTP'; }
  }
}

async function verifyOTP() {
  const otp = document.getElementById('otpInput')?.value?.trim();
  if (!otp) return showToast('Enter OTP', 'error');
  const btn = document.getElementById('verifyOtpBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'Verifying...'; }
  try {
    const res = await API.post('/api/auth/verify-otp', { email: otpEmail, otp });
    Auth.setAuth(res.token, res.user);
    updateNavAuth();
    updateCartCount();
    hideModal('loginModal');
    showToast(`Welcome to AgroConnect, ${res.user.name}! 🌾`);
    if (res.user.role === 'farmer') setTimeout(() => window.location.href = '/farmer-dashboard', 600);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Verify OTP'; }
  }
}

function switchAuthTab(tab) {
  document.getElementById('loginPanel').style.display = tab === 'login' ? 'block' : 'none';
  document.getElementById('regPanel').style.display = tab === 'register' ? 'block' : 'none';
  if (document.getElementById('otpPanel')) document.getElementById('otpPanel').style.display = 'none';
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active', 'btn-success'));
  const activeTab = document.getElementById('tab' + tab.charAt(0).toUpperCase() + tab.slice(1));
  if (activeTab) { activeTab.classList.add('active', 'btn-success'); }
}

// ─── Add to Cart ──────────────────────────────────────────────────────────────
async function addToCart(productId) {
  const user = Auth.getUser();
  if (!user) { showModal('loginModal'); showToast('Login to add items to cart', 'warning'); return; }
  try {
    await API.post('/api/cart', { product_id: productId, quantity: 1 });
    updateCartCount();
    showToast('Added to cart! 🛒');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ─── Wishlist ──────────────────────────────────────────────────────────────────
async function toggleWishlist(productId, btn) {
  const user = Auth.getUser();
  if (!user) { showModal('loginModal'); return; }
  try {
    const res = await API.post('/api/wishlist', { product_id: productId });
    if (btn) btn.textContent = res.action === 'added' ? '❤️' : '🤍';
    showToast(res.action === 'added' ? 'Added to wishlist!' : 'Removed from wishlist');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ─── Stars ────────────────────────────────────────────────────────────────────
function renderStars(rating) {
  let s = '';
  for (let i = 1; i <= 5; i++) s += i <= Math.round(rating) ? '★' : '☆';
  return `<span class="star-rating">${s}</span>`;
}

// ─── Translations ─────────────────────────────────────────────────────────────
const TRANSLATIONS = {
  en: {
    'nav.home': 'Home', 'nav.marketplace': 'Marketplace', 'nav.dashboard': '📊 Dashboard',
    'nav.login': '🔐 Login / Register', 'nav.logout': 'Logout',
    'hero.title': 'Farm Fresh, Direct to Your Door',
    'hero.subtitle': 'Connect directly with farmers. Get the freshest produce at the best prices.',
    'hero.shop': '🛒 Shop Now', 'hero.sell': '🌾 Sell Harvest',
    'feat.ai': 'AI Pricing', 'feat.pre': 'Pre-Harvest', 'feat.pay': 'Secure Pay',
    'feat.otp': 'OTP Verify', 'feat.multi': 'Multilingual', 'feat.direct': 'Direct Trade',
    'cart.title': '🛒 Shopping Cart', 'cart.empty': 'Your cart is empty',
    'cart.checkout': 'Proceed to Pay', 'cart.location': 'Delivery Location',
    'search.placeholder': 'Search fruits, vegetables, grains...',
    'filter.category': 'Category', 'filter.price': 'Price Range',
    'filter.preharvest': 'Pre-Harvest Only', 'filter.sort': 'Sort By',
    'product.addcart': 'Add to Cart', 'product.viewall': 'View All Products',
    'login.title': '🌾 Welcome Back', 'register.title': '🌱 Join AgroConnect',
    'otp.title': '📱 Verify OTP',
    'stat.farmers': '500+ Farmers', 'stat.customers': '2K+ Customers', 'stat.products': '50+ Products',
  },
  hi: {
    'nav.home': 'होम', 'nav.marketplace': 'मार्केटप्लेस', 'nav.dashboard': '📊 डैशबोर्ड',
    'nav.login': '🔐 लॉगिन / रजिस्टर', 'nav.logout': 'लॉगआउट',
    'hero.title': 'खेत से ताज़ा, सीधे आपके दरवाजे',
    'hero.subtitle': 'किसानों से सीधे जुड़ें। सबसे ताज़े उत्पाद, सबसे अच्छे दाम पर।',
    'hero.shop': '🛒 खरीदें', 'hero.sell': '🌾 फसल बेचें',
    'feat.ai': 'AI मूल्य', 'feat.pre': 'प्री-हार्वेस्ट', 'feat.pay': 'सुरक्षित भुगतान',
    'feat.otp': 'OTP सत्यापन', 'feat.multi': 'बहुभाषी', 'feat.direct': 'सीधा व्यापार',
    'cart.title': '🛒 शॉपिंग कार्ट', 'cart.empty': 'कार्ट खाली है',
    'cart.checkout': 'भुगतान करें', 'cart.location': 'डिलीवरी स्थान',
    'search.placeholder': 'फल, सब्जियां, अनाज खोजें...',
    'filter.category': 'श्रेणी', 'filter.price': 'मूल्य सीमा',
    'filter.preharvest': 'केवल प्री-हार्वेस्ट', 'filter.sort': 'क्रमबद्ध करें',
    'product.addcart': 'कार्ट में जोड़ें', 'product.viewall': 'सभी उत्पाद देखें',
    'login.title': '🌾 वापस स्वागत है', 'register.title': '🌱 AgroConnect से जुड़ें',
    'otp.title': '📱 OTP सत्यापित करें',
    'stat.farmers': '500+ किसान', 'stat.customers': '2K+ ग्राहक', 'stat.products': '50+ उत्पाद',
  },
  ta: {
    'nav.home': 'முகப்பு', 'nav.marketplace': 'சந்தை', 'nav.dashboard': '📊 டாஷ்போர்டு',
    'nav.login': '🔐 உள்நுழை / பதிவு', 'nav.logout': 'வெளியேறு',
    'hero.title': 'விவசாயி நேரடியாக உங்கள் வீட்டிற்கு',
    'hero.subtitle': 'விவசாயிகளுடன் நேரடியாக இணைந்து சிறந்த விலையில் பெறுங்கள்.',
    'hero.shop': '🛒 வாங்கு', 'hero.sell': '🌾 விற்கவும்',
    'feat.ai': 'AI விலை', 'feat.pre': 'முன் அறுவடை', 'feat.pay': 'பாதுகாப்பான கட்டணம்',
    'feat.otp': 'OTP சரிபார்ப்பு', 'feat.multi': 'பன்மொழி', 'feat.direct': 'நேரடி வர்த்தகம்',
    'cart.title': '🛒 கார்ட்', 'cart.empty': 'கார்ட் காலியாக உள்ளது',
    'cart.checkout': 'கட்டணம் செலுத்து', 'cart.location': 'டெலிவரி இடம்',
    'search.placeholder': 'பழங்கள், காய்கறிகள் தேடுங்கள்...',
    'filter.category': 'வகை', 'filter.price': 'விலை வரம்பு',
    'filter.preharvest': 'முன் அறுவடை மட்டும்', 'filter.sort': 'வரிசைப்படுத்து',
    'product.addcart': 'கார்ட்டில் சேர்', 'product.viewall': 'அனைத்தும் காண',
    'login.title': '🌾 வரவேற்கிறோம்', 'register.title': '🌱 AgroConnect சேரு',
    'otp.title': '📱 OTP சரிபார்',
    'stat.farmers': '500+ விவசாயிகள்', 'stat.customers': '2K+ வாடிக்கையாளர்கள்', 'stat.products': '50+ தயாரிப்புகள்',
  },
  te: {
    'nav.home': 'హోమ్', 'nav.marketplace': 'మార్కెట్', 'nav.dashboard': '📊 డాష్‌బోర్డ్',
    'nav.login': '🔐 లాగిన్ / నమోదు', 'nav.logout': 'లాగ్ అవుట్',
    'hero.title': 'రైతు నేరుగా మీ తలుపు వద్దకు',
    'hero.subtitle': 'రైతులతో నేరుగా అనుసంధానించి అత్యుత్తమ ధరలకు పొందండి.',
    'hero.shop': '🛒 కొనుగోలు', 'hero.sell': '🌾 పంట అమ్ముము',
    'feat.ai': 'AI ధర', 'feat.pre': 'ముందస్తు పంట', 'feat.pay': 'సురక్షిత చెల్లింపు',
    'feat.otp': 'OTP ధృవీకరణ', 'feat.multi': 'బహుభాష', 'feat.direct': 'నేరుగా వ్యాపారం',
    'cart.title': '🛒 కార్ట్', 'cart.empty': 'కార్ట్ ఖాళీగా ఉంది',
    'cart.checkout': 'చెల్లింపు చేయండి', 'cart.location': 'డెలివరీ స్థానం',
    'search.placeholder': 'పండ్లు, కూరగాయలు వెతకండి...',
    'filter.category': 'వర్గం', 'filter.price': 'ధర పరిధి',
    'filter.preharvest': 'ముందస్తు పంట మాత్రమే', 'filter.sort': 'క్రమపరచు',
    'product.addcart': 'కార్ట్‌కు జోడించు', 'product.viewall': 'అన్నీ చూడండి',
    'login.title': '🌾 తిరిగి స్వాగతం', 'register.title': '🌱 AgroConnect చేరండి',
    'otp.title': '📱 OTP ధృవీకరించు',
    'stat.farmers': '500+ రైతులు', 'stat.customers': '2K+ వినియోగదారులు', 'stat.products': '50+ ఉత్పత్తులు',
  }
};

let currentLang = localStorage.getItem('agro_lang') || 'en';
const _txCache = {};

function t(key) {
  return TRANSLATIONS[currentLang]?.[key] || TRANSLATIONS['en']?.[key] || key;
}

function applyLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('agro_lang', lang);
  document.documentElement.lang = lang;

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const attr = el.getAttribute('data-i18n-attr');
    const val = t(key);
    if (attr) el.setAttribute(attr, val);
    else el.textContent = val;
  });

  document.querySelectorAll('.lang-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-lang') === lang);
  });

  if (lang !== 'en') {
    setTimeout(() => translateDynamic(), 400);
  }
}

async function translateDynamic() {
  if (currentLang === 'en') return;
  const langMap = { hi: 'hi', ta: 'ta', te: 'te' };
  const targetLang = langMap[currentLang];
  if (!targetLang) return;

  const textNodes = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const parent = node.parentElement;
      if (!parent) return NodeFilter.FILTER_REJECT;
      const tag = parent.tagName?.toLowerCase();
      if (['script', 'style', 'input', 'textarea', 'select'].includes(tag)) return NodeFilter.FILTER_REJECT;
      if (parent.classList.contains('lang-btn') || parent.closest('.lang-btn')) return NodeFilter.FILTER_REJECT;
      if (parent.closest('[data-no-translate]')) return NodeFilter.FILTER_REJECT;
      const text = node.textContent.trim();
      if (!text || text.length < 3 || /^[\d₹%+.,\-\/\s]+$/.test(text)) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    }
  });

  const batch = [];
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const text = node.textContent.trim();
    if (!_txCache[`${targetLang}:${text}`]) batch.push({ node, text });
    if (batch.length >= 5) break; // limit per run
  }

  const promises = batch.map(async ({ node, text }) => {
    const cacheKey = `${targetLang}:${text}`;
    try {
      const res = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=en|${targetLang}`);
      const data = await res.json();
      const translated = data.responseData?.translatedText;
      if (translated && translated !== text) {
        _txCache[cacheKey] = translated;
        node.textContent = translated;
      }
    } catch { }
  });
  await Promise.all(promises);
}

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateNavAuth();
  updateCartCount();
  applyLanguage(currentLang);

  // Language buttons
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => applyLanguage(btn.getAttribute('data-lang')));
  });

  // Nav logout
  document.querySelectorAll('.btn-logout').forEach(btn => {
    btn.addEventListener('click', doLogout);
  });

  // Login enter key
  document.getElementById('loginPassword')?.addEventListener('keypress', e => {
    if (e.key === 'Enter') doLogin(e);
  });
  document.getElementById('loginEmail')?.addEventListener('keypress', e => {
    if (e.key === 'Enter') doLogin(e);
  });

  // OTP enter key
  document.getElementById('otpInput')?.addEventListener('keypress', e => {
    if (e.key === 'Enter') verifyOTP();
  });

  // Login form submit
  document.getElementById('loginForm')?.addEventListener('submit', doLogin);
});
