/* Run before the document paints, then attach to the shared header button. */
(() => {
  const key = 'a-lecoute.theme.v1';
  const media = window.matchMedia?.('(prefers-color-scheme: dark)');
  let preference = null;
  function readPreference() {
    try {
      const value = localStorage.getItem(key);
      return value === 'dark' || value === 'light' ? value : null;
    } catch { return null; }
  }
  function apply() {
    const theme = preference ?? (media?.matches ? 'dark' : 'light');
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', theme === 'dark' ? '#101b16' : '#f4f5ef');
    const button = document.querySelector('[data-theme-toggle]');
    if (button) {
      button.setAttribute('aria-pressed', String(theme === 'dark'));
      button.title = theme === 'dark' ? 'Passer au thème clair' : 'Passer au thème sombre';
    }
  }
  preference = readPreference();
  apply();
  function attach() {
    const button = document.querySelector('[data-theme-toggle]');
    button?.addEventListener('click', () => {
      preference = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(key, preference); } catch { /* Works in memory when storage is blocked. */ }
      apply();
    });
    apply();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', attach, { once: true });
  else attach();
  media?.addEventListener('change', () => { if (!preference) apply(); });
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) { preference = readPreference(); apply(); }
  });
})();
