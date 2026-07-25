(() => {
  // LANG SWITCH
  const btn = document.querySelector('.site_top_panel_block-lbtn');
  const menu = document.querySelector('.site_top_panel_block-lmenu');
  const wrapper = document.querySelector('.site_top_panel_block-switch');

  if (btn && menu && wrapper) {
    btn.addEventListener('click', () => {
      menu.classList.toggle('open');
    });

    document.addEventListener('click', e => {
      if (!e.target.closest('.site_top_panel_block-switch')) {
        menu.classList.remove('open');
      }
    });

    menu.querySelectorAll('li').forEach(item => {
      item.addEventListener('click', () => {
        const flag = item.querySelector('.site_top_panel_block-ficon');
        const btnFlag = btn.querySelector('.site_top_panel_block-ficon');

        if (flag && btnFlag) {
          btnFlag.innerHTML = flag.innerHTML;
        }

        menu.classList.remove('open');
      });
    });
  }

})();

