// content.js — Injects the MercuryCI review panel into GitHub PR pages

const PANEL_ID = 'mercuryci-panel';

// ── Helpers ─────────────────────────────────────────────────────────────────

function isPRPage() {
  return /\/pull\/\d+(\/|$)/.test(window.location.pathname)
    && !window.location.pathname.endsWith('/files')
    && !window.location.pathname.endsWith('/commits');
}

function getPRInfo() {
  const parts = window.location.pathname.split('/');
  return { owner: parts[1], repo: parts[2], pullNumber: parseInt(parts[4]) };
}

function getSidebarTarget() {
  return (
    document.querySelector('.Layout-sidebar')
    || document.querySelector('.discussion-sidebar')
  );
}

// ── Panel builder ────────────────────────────────────────────────────────────

function buildPanel(status, hasToken) {
  const panel = document.createElement('div');
  panel.id = PANEL_ID;
  panel.className = 'discussion-sidebar-item';

  // Header
  const header = document.createElement('div');
  header.className = 'mercuryci-header';
  header.innerHTML = `
    <span class="mercuryci-title">🪐 MercuryCI</span>
    <span class="mercuryci-moon" title="${status.moonGuidance}">
      ${status.moonEmoji} ${status.moonLabel}
    </span>
  `;
  panel.appendChild(header);

  // Retrograde banner
  if (status.mercuryRetrograde) {
    const banner = document.createElement('div');
    banner.className = 'mercuryci-retrograde-banner';
    banner.innerHTML = `
      ☿ Mercury retrograde
      <span class="mercuryci-retrograde-days">
        Direct in ${status.daysUntilDirect} day${status.daysUntilDirect !== 1 ? 's' : ''}
      </span>
    `;
    panel.appendChild(banner);
  }

  // Moon guidance
  const guidance = document.createElement('p');
  guidance.className = 'mercuryci-guidance';
  guidance.textContent = status.moonGuidance;
  panel.appendChild(guidance);

  // No-token notice
  if (!hasToken) {
    const notice = document.createElement('p');
    notice.className = 'mercuryci-notice';
    notice.innerHTML = 'Add a GitHub token in the <a class="mercuryci-settings-link" href="#">extension settings</a> to enable review buttons.';
    notice.querySelector('.mercuryci-settings-link').addEventListener('click', e => {
      e.preventDefault();
      chrome.runtime.sendMessage({ type: 'OPEN_POPUP' });
    });
    panel.appendChild(notice);
  }

  // Review buttons
  const buttons = document.createElement('div');
  buttons.className = 'mercuryci-buttons';

  const defs = [
    { action: 'lgtm',   label: '✅ LGTM',                  title: 'Looks good to me. I read the code.' },
    { action: 'vibes',  label: '🌙 The vibes are right',    title: 'Energetically aligned. The code feels correct.' },
    { action: 'cosmos', label: '🪐 I defer to the cosmos',  title: 'I read the code. The stars must decide.' },
  ];

  for (const { action, label, title } of defs) {
    const btn = document.createElement('button');
    btn.className = `mercuryci-btn mercuryci-btn-${action}`;
    btn.dataset.action = action;
    btn.textContent = label;
    btn.title = title;
    btn.disabled = !hasToken;
    buttons.appendChild(btn);
  }

  panel.appendChild(buttons);

  // Status line (shows after a review is submitted)
  const statusLine = document.createElement('p');
  statusLine.className = 'mercuryci-status';
  statusLine.id = 'mercuryci-status';
  panel.appendChild(statusLine);

  return panel;
}

// ── Button handlers ──────────────────────────────────────────────────────────

function setStatus(msg, isError = false) {
  const el = document.getElementById('mercuryci-status');
  if (!el) return;
  el.textContent = msg;
  el.className = `mercuryci-status ${isError ? 'mercuryci-status-error' : 'mercuryci-status-ok'}`;
}

function disableButtons() {
  document.querySelectorAll('.mercuryci-btn').forEach(b => { b.disabled = true; });
}

function enableButtons() {
  document.querySelectorAll('.mercuryci-btn').forEach(b => { b.disabled = false; });
}

async function handleReview(token, action) {
  const pr = getPRInfo();
  disableButtons();
  setStatus('Consulting the cosmos…');

  let event, body;

  if (action === 'lgtm') {
    event = 'APPROVE';
    body  = '✅ LGTM';
  } else if (action === 'vibes') {
    event = 'APPROVE';
    body  = '🌙 The vibes are right.';
  } else if (action === 'cosmos') {
    const status = getCosmicStatus();
    const decision = cosmosDecides(status);
    event = decision.state;
    body  = `🪐 I defer to the cosmos.\n\n${decision.note}`;
  }

  try {
    await submitReview({ ...pr, token, event, body });
    const verb = event === 'APPROVE' ? 'Approved' : 'Changes requested';
    setStatus(`${verb}. The cosmos have spoken.`);
  } catch (err) {
    setStatus(`Error: ${err.message}`, true);
    enableButtons();
  }
}

function attachHandlers(panel, token) {
  panel.querySelectorAll('.mercuryci-btn').forEach(btn => {
    btn.addEventListener('click', () => handleReview(token, btn.dataset.action));
  });
}

// ── Injection ────────────────────────────────────────────────────────────────

async function injectPanel() {
  if (!isPRPage()) return;
  if (document.getElementById(PANEL_ID)) return;

  const sidebar = getSidebarTarget();
  if (!sidebar) return;

  const { mercuryci_token: token } = await chrome.storage.local.get('mercuryci_token');
  const status = getCosmicStatus();

  const panel = buildPanel(status, !!token);
  sidebar.prepend(panel);

  if (token) attachHandlers(panel, token);
}

function removePanel() {
  document.getElementById(PANEL_ID)?.remove();
}

// ── Navigation handling (GitHub uses Turbo for SPA routing) ──────────────────

function onNavigate() {
  removePanel();
  setTimeout(injectPanel, 300); // brief delay for DOM to settle
}

document.addEventListener('turbo:load',  onNavigate);
document.addEventListener('turbo:render', onNavigate);
document.addEventListener('pjax:end',    onNavigate);

// MutationObserver fallback for pages that don't fire turbo events
const observer = new MutationObserver(() => {
  if (isPRPage() && !document.getElementById(PANEL_ID)) {
    const sidebar = getSidebarTarget();
    if (sidebar) injectPanel();
  }
});

observer.observe(document.body, { childList: true, subtree: false });

// Initial load
injectPanel();
