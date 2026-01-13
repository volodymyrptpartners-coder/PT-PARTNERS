(() => {
  const yearEl = document.getElementById('site_footer_block-footer-year');
  if (!yearEl) return;

  yearEl.textContent = new Date().getFullYear();
})();

