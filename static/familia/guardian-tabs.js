(() => {
  const names = new Set(['tarefas', 'premios', 'familia', 'analises']);
  const currentName = () => {
    const name = location.hash.replace(/^#tab-/, '');
    return names.has(name) ? name : 'tarefas';
  };
  const select = name => {
    document.querySelectorAll('.guardian-panel').forEach(panel => {
      panel.hidden = panel.id !== `tab-${name}`;
    });
    document.querySelectorAll('[data-guardian-tab]').forEach(link => {
      const active = link.dataset.guardianTab === name;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
  };

  const initialize = () => {
    if (!document.querySelector('.guardian-panel')) return;
    document.querySelectorAll('[data-guardian-tab]').forEach(link => {
      link.addEventListener('click', event => {
        event.preventDefault();
        const name = link.dataset.guardianTab;
        if (!names.has(name)) return;
        if (location.hash !== link.hash) history.pushState(null, '', link.hash);
        select(name);
      });
    });
    if (!names.has(location.hash.replace(/^#tab-/, ''))) {
      history.replaceState(null, '', `${location.pathname}${location.search}#tab-tarefas`);
    }
    select(currentName());
    window.addEventListener('popstate', () => select(currentName()));
    window.addEventListener('hashchange', () => select(currentName()));
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize);
  else initialize();
})();
