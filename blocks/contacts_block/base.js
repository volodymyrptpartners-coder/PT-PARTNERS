// Copy to clipboard
(() => {
  document.querySelectorAll('.contacts_block-card').forEach(card => {
    card.addEventListener('click', e => {
      if (e.target.closest('[data-no-copy]')) return;

      const value = card.dataset.copy;
      if (!value) return;

      navigator.clipboard.writeText(value)
        .then(() => {
          card.classList.add('copied');
          setTimeout(() => card.classList.remove('copied'), 1500);
        })
        .catch(() => {
          console.warn('Clipboard unavailable:', value);
        });
    });
  });
})();


// EMAIL
(() => {
  const links = document.querySelectorAll('a[data-email-link]');
  if (!links.length) return;

  const isMobile = /Android|iPhone|iPad|iPod|Windows Phone|webOS/i.test(
    navigator.userAgent
  );

  links.forEach(link => {
    const href = link.getAttribute('href');
    if (!href || !href.startsWith('mailto:')) return;

    if (isMobile) return;

    const [mailtoPart, query = ''] = href.split('?');
    const email = mailtoPart.replace('mailto:', '');

    const params = new URLSearchParams(query);

    const gmailParams = new URLSearchParams();
    gmailParams.set('to', email);
    gmailParams.set('fs', '1');
    gmailParams.set('tf', 'cm');

    if (params.has('subject')) {
      gmailParams.set('su', params.get('subject'));
    }

    if (params.has('body')) {
      gmailParams.set('body', params.get('body'));
    }

    if (params.has('cc')) {
      gmailParams.set('cc', params.get('cc'));
    }

    if (params.has('bcc')) {
      gmailParams.set('bcc', params.get('bcc'));
    }

    const gmailUrl =
      'https://mail.google.com/mail/u/0/?' + gmailParams.toString();

    link.setAttribute('href', gmailUrl);
  });
})();

