// Tai's PPA Workspace App JS

// Register Service Worker for PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js').catch(err => {
      console.log('SW registration failed:', err);
    });
  });
}

// Local draft saving for offline note preservation
window.saveLocalNoteDraft = function(orgId, text) {
  if (!orgId) return;
  localStorage.setItem(`ppa_note_draft_${orgId}`, text);
};

window.getLocalNoteDraft = function(orgId) {
  if (!orgId) return '';
  return localStorage.getItem(`ppa_note_draft_${orgId}`) || '';
};

window.clearLocalNoteDraft = function(orgId) {
  if (!orgId) return;
  localStorage.removeItem(`ppa_note_draft_${orgId}`);
};
