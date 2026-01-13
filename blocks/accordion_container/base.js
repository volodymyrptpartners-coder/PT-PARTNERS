(() => {
  // CHANGED: гарантуємо запуск після того, як DOM вже є
  const init = () => {
    document.querySelectorAll('.accordion_container-item').forEach(item => {
      const button = item.querySelector('.accordion_container-button');
      const content = item.querySelector('.accordion_container-content');

      if (!button || !content) return;

      // CHANGED: явна ініціалізація a11y + синхронізація з поточним DOM-станом
      const isOpen = item.classList.contains('open');
      button.setAttribute('aria-expanded', String(isOpen));

      button.addEventListener('click', () => {
        const open = item.classList.toggle('open');
        button.setAttribute('aria-expanded', String(open));
      });
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

