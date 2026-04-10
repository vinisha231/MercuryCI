// background.js — Service worker for MercuryCI extension

// Re-inject the content script into existing PR tabs when the extension
// is first installed or updated (avoids needing a full browser restart).
chrome.runtime.onInstalled.addListener(async () => {
  const tabs = await chrome.tabs.query({ url: 'https://github.com/*/pull/*' });
  for (const tab of tabs) {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ['src/cosmic.js', 'src/github_api.js', 'src/content.js'],
    }).catch(() => {}); // ignore tabs we can't access
  }
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'OPEN_POPUP') {
    // Can't open popup programmatically in MV3 — open options page instead
    chrome.runtime.openOptionsPage?.();
  }
});
