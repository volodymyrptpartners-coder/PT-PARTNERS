(() => {
  document
    .querySelectorAll('.accordion_container-section')
    .forEach(section => {
      section
        .querySelectorAll('.accordion_container-item')
        .forEach(item => {
          const button = item.querySelector('.accordion_container-button');
          const content = item.querySelector('.accordion_container-content');

          if (!button || !content) return;

          button.addEventListener('click', () => {
            const expanded = button.getAttribute('aria-expanded') === 'true';
            button.setAttribute('aria-expanded', String(!expanded));
            content.hidden = expanded;
          });
        });
    });
})();

