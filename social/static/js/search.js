document.addEventListener('DOMContentLoaded', () => {
  const btnOpen    = document.getElementById('openSearch');
  const btnClose   = document.getElementById('closeSearch');
  const overlay    = document.getElementById('searchOverlay');
  const drawer     = document.getElementById('searchDrawer');
  const form       = document.getElementById('searchForm');
  const input      = document.getElementById('searchInput');
  const results    = document.getElementById('searchResults');
  const recentUl   = document.getElementById('recentList');
  const recentCont = document.getElementById('recentContainer');

  let recent = JSON.parse(localStorage.getItem('recentSearches') || '[]');

  function renderRecent() {
    recentUl.innerHTML = '';
    if (recent.length === 0) {
      recentUl.innerHTML = '<li class="text-zinc-500">No recent searches.</li>';
    } else {
      recent.forEach((q, idx) => {
        const li = document.createElement('li');
        li.className = 'flex justify-between items-center text-zinc-100 hover:text-purple-300 transition';
        li.innerHTML = `
          <button class="text-left truncate flex-1">${q}</button>
          <button class="ml-2 text-zinc-500 hover:text-red-500" data-index="${idx}">✕</button>`;
        li.querySelector('button:first-child')
          .addEventListener('click', () => doSearch(q));
        li.querySelector('button[data-index]')
          .addEventListener('click', e => {
            recent.splice(+e.currentTarget.dataset.index, 1);
            localStorage.setItem('recentSearches', JSON.stringify(recent));
            renderRecent();
          });
        recentUl.appendChild(li);
      });
    }
  }

  function showDrawer() {
    overlay.classList.remove('hidden');
    drawer.classList.remove('-translate-x-full');
    recentCont.classList.remove('hidden');
    results.classList.add('hidden');
    renderRecent();
    input.value = '';
    input.focus();
  }
  function hideDrawer() {
    drawer.classList.add('-translate-x-full');
    overlay.classList.add('hidden');
    results.innerHTML = '';
  }

  btnOpen.addEventListener('click', e => { e.preventDefault(); showDrawer(); });
  btnClose.addEventListener('click', hideDrawer);
  overlay.addEventListener('click', hideDrawer);

  function doSearch(query) {
    recentCont.classList.add('hidden');
    results.classList.remove('hidden');
    if (query && !recent.includes(query)) {
      recent.unshift(query);
      if (recent.length > 5) recent.pop();
      localStorage.setItem('recentSearches', JSON.stringify(recent));
    }
    fetch(`/search/?q=${encodeURIComponent(query)}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(r => r.text())
    .then(html => {
      results.innerHTML = html || '<p class="text-zinc-500">No user found.</p>';
    });
  }

  form.addEventListener('submit', e => {
    e.preventDefault();
    const q = input.value.trim();
    if (q) doSearch(q);
  });
});
