// popup.js — Settings popup logic

// Birth date → zodiac sign (matches birth_chart.py)
const BIRTHDATE_RANGES = [
  [[3,21],[4,19],  'Aries'],
  [[4,20],[5,20],  'Taurus'],
  [[5,21],[6,20],  'Gemini'],
  [[6,21],[7,22],  'Cancer'],
  [[7,23],[8,22],  'Leo'],
  [[8,23],[9,22],  'Virgo'],
  [[9,23],[10,22], 'Libra'],
  [[10,23],[11,21],'Scorpio'],
  [[11,22],[12,21],'Sagittarius'],
  [[12,22],[12,31],'Capricorn'],
  [[1,1],[1,19],   'Capricorn'],
  [[1,20],[2,18],  'Aquarius'],
  [[2,19],[3,20],  'Pisces'],
];

function birthdateToSign(month, day) {
  for (const [[sm, sd], [em, ed], sign] of BIRTHDATE_RANGES) {
    const inRange =
      (month === sm && day >= sd) ||
      (month === em && day <= ed) ||
      (sm < month && month < em);
    if (inRange) return sign;
  }
  return 'Libra';
}

// ── DOM refs ─────────────────────────────────────────────────────────────────

const $ = id => document.getElementById(id);

const els = {
  moon:          $('popup-moon'),
  mercury:       $('popup-mercury'),
  retrogradeRow: $('popup-retrograde-row'),
  days:          $('popup-days'),

  tokenSection:  $('token-section'),
  tokenInput:    $('token-input'),
  saveTokenBtn:  $('save-token-btn'),

  userSection:   $('user-section'),
  userLogin:     $('user-login'),
  userSign:      $('user-sign'),
  changeSignBtn: $('change-sign-btn'),
  logoutBtn:     $('logout-btn'),

  signSection:   $('sign-section'),
  signSelect:    $('sign-select'),
  birthMonth:    $('birth-month'),
  birthDay:      $('birth-day'),
  saveSignBtn:   $('save-sign-btn'),

  feedback:      $('feedback'),
};

// ── Feedback helper ───────────────────────────────────────────────────────────

function setFeedback(msg, type = 'ok') {
  els.feedback.textContent = msg;
  els.feedback.className = type;
}

function clearFeedback() {
  els.feedback.textContent = '';
  els.feedback.className = '';
}

// ── Cosmic status (runs on open) ──────────────────────────────────────────────

function renderCosmicStatus() {
  // cosmic.js is not available in the popup context — re-implement inline
  const MOON_PHASES = [
    { threshold: 0.0625, emoji: '🌑', label: 'New Moon' },
    { threshold: 0.1875, emoji: '🌒', label: 'Waxing Crescent' },
    { threshold: 0.3125, emoji: '🌓', label: 'First Quarter' },
    { threshold: 0.4375, emoji: '🌔', label: 'Waxing Gibbous' },
    { threshold: 0.5625, emoji: '🌕', label: 'Full Moon' },
    { threshold: 0.6875, emoji: '🌖', label: 'Waning Gibbous' },
    { threshold: 0.8125, emoji: '🌗', label: 'Last Quarter' },
    { threshold: 0.9375, emoji: '🌘', label: 'Waning Crescent' },
    { threshold: 1.0,    emoji: '🌑', label: 'New Moon' },
  ];

  const RETROGRADE = [
    ['2025-03-15','2025-04-07'], ['2025-07-18','2025-08-11'],
    ['2025-11-09','2025-11-29'], ['2026-01-10','2026-01-31'],
    ['2026-05-05','2026-05-28'], ['2026-09-04','2026-09-26'],
  ];

  const now = new Date();
  const knownNew = new Date('2000-01-06');
  const daysSince = (now - knownNew) / 86400000;
  const pos = ((daysSince % 29.53) + 29.53) % 29.53 / 29.53;
  const moon = MOON_PHASES.find(p => pos < p.threshold) || MOON_PHASES[0];
  els.moon.textContent = `${moon.emoji} ${moon.label}`;

  const today = now.toISOString().slice(0, 10);
  const period = RETROGRADE.find(([s, e]) => today >= s && today <= e);

  if (period) {
    const end = new Date(period[1]);
    const days = Math.ceil((end - now) / 86400000);
    els.mercury.innerHTML = '<span class="retrograde-badge">Retrograde</span>';
    els.retrogradeRow.style.display = 'flex';
    els.days.textContent = `${days} day${days !== 1 ? 's' : ''}`;
  } else {
    els.mercury.innerHTML = '<span class="ok-badge">Direct ✓</span>';
  }
}

// ── Token flow ────────────────────────────────────────────────────────────────

async function verifyAndSaveToken(token) {
  setFeedback('Verifying token…');
  try {
    const res = await fetch('https://api.github.com/user', {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/vnd.github+json',
      },
    });
    if (!res.ok) throw new Error('Token rejected by GitHub.');
    const user = await res.json();
    await chrome.storage.local.set({ mercuryci_token: token, mercuryci_login: user.login });
    return user.login;
  } catch (err) {
    throw new Error(err.message || 'Could not verify token.');
  }
}

async function loadTokenState() {
  const { mercuryci_token: token, mercuryci_login: login, mercuryci_sign: sign } =
    await chrome.storage.local.get(['mercuryci_token', 'mercuryci_login', 'mercuryci_sign']);

  if (token && login) {
    showUserSection(login, sign);
    // Show sign picker if no sign saved yet
    if (!sign) showSignSection();
  } else {
    showTokenSection();
  }
}

function showTokenSection() {
  els.tokenSection.style.display = 'block';
  els.userSection.style.display  = 'none';
  els.signSection.style.display  = 'none';
}

function showUserSection(login, sign) {
  els.tokenSection.style.display = 'none';
  els.userSection.style.display  = 'block';
  els.userLogin.textContent = `@${login}`;
  els.userSign.textContent  = sign ? `☀️ ${sign}` : 'No sign saved';
}

function showSignSection() {
  els.signSection.style.display = 'block';
}

// ── Sign flow ─────────────────────────────────────────────────────────────────

async function saveSign(sign) {
  await chrome.storage.local.set({ mercuryci_sign: sign });
  const { mercuryci_login: login } = await chrome.storage.local.get('mercuryci_login');
  showUserSection(login, sign);
  els.signSection.style.display = 'none';
  setFeedback(`Saved. You are a ${sign}.`);
}

// ── Event listeners ───────────────────────────────────────────────────────────

els.saveTokenBtn.addEventListener('click', async () => {
  const token = els.tokenInput.value.trim();
  if (!token) { setFeedback('Paste your token first.', 'error'); return; }
  els.saveTokenBtn.disabled = true;
  try {
    const login = await verifyAndSaveToken(token);
    const { mercuryci_sign: sign } = await chrome.storage.local.get('mercuryci_sign');
    showUserSection(login, sign);
    if (!sign) showSignSection();
    setFeedback(`Signed in as @${login}.`);
  } catch (err) {
    setFeedback(err.message, 'error');
  } finally {
    els.saveTokenBtn.disabled = false;
  }
});

els.changeSignBtn.addEventListener('click', () => {
  showSignSection();
  clearFeedback();
});

els.logoutBtn.addEventListener('click', async () => {
  await chrome.storage.local.remove(['mercuryci_token', 'mercuryci_login']);
  showTokenSection();
  setFeedback('Signed out.');
});

els.saveSignBtn.addEventListener('click', async () => {
  // Prefer dropdown selection
  const selected = els.signSelect.value;
  if (selected) { await saveSign(selected); return; }

  // Fall back to birth date
  const month = parseInt(els.birthMonth.value);
  const day   = parseInt(els.birthDay.value);
  if (!isNaN(month) && !isNaN(day) && month >= 1 && month <= 12 && day >= 1 && day <= 31) {
    const sign = birthdateToSign(month, day);
    await saveSign(sign);
    return;
  }

  setFeedback('Select a sign or enter a valid birth date.', 'error');
});

// Clear birth date fields when dropdown is used, and vice versa
els.signSelect.addEventListener('change', () => {
  if (els.signSelect.value) {
    els.birthMonth.value = '';
    els.birthDay.value   = '';
  }
});

els.birthMonth.addEventListener('input', () => { els.signSelect.value = ''; });
els.birthDay.addEventListener('input',   () => { els.signSelect.value = ''; });

// ── Init ──────────────────────────────────────────────────────────────────────

renderCosmicStatus();
loadTokenState();
