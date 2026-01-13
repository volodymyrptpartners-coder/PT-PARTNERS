(() => {
  const layout = document.querySelector('.main_block');
  if (!layout) return;

  const fabs = document.querySelectorAll('.contact_fab_block-fab');
  if (!fabs.length) return;

  const alignFab = fab => {
    const rect = layout.getBoundingClientRect();
    const offsetRight = window.innerWidth - rect.right;
    fab.style.right = `${offsetRight + 20}px`;
  };

  const alignAll = () => {
    fabs.forEach(alignFab);
  };

  // initial
  window.addEventListener('load', alignAll);

  // responsive
  window.addEventListener('resize', alignAll);
})();

