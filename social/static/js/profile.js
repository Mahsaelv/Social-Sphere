// static/js/profile.js

document.addEventListener('DOMContentLoaded', () => {
  const { postsUrl, savedUrl, followersUrl, followingUrl, followToggle } = window.profileUrls;

  const tabPosts    = document.getElementById('tabPosts');
  const tabSaved    = document.getElementById('tabSaved');
  const postsGrid   = document.getElementById('postsGrid');
  const savedGrid   = document.getElementById('savedGrid');
  const postsLoader = document.getElementById('postsLoader');
  const savedLoader = document.getElementById('savedLoader');

  let postsPage = 1, savedPage = 1;
  let loadingPosts = false, loadingSaved = false;

  function showTab(tab) {
    if (tab === 'posts') {
      tabPosts.classList.add('border-purple-400');
      tabSaved.classList.remove('border-purple-400');
      postsGrid.classList.remove('hidden');
      if (postsPage === 1) postsLoader.classList.remove('hidden');
      savedGrid.classList.add('hidden');
      savedLoader.classList.add('hidden');
      if (postsPage === 1) loadPosts();
    } else {
      tabSaved.classList.add('border-purple-400');
      tabPosts.classList.remove('border-purple-400');
      savedGrid.classList.remove('hidden');
      if (savedPage === 1) savedLoader.classList.remove('hidden');
      postsGrid.classList.add('hidden');
      postsLoader.classList.add('hidden');
      if (savedPage === 1) loadSaved();
    }
  }

  tabPosts.addEventListener('click', () => showTab('posts'));
  tabSaved.addEventListener('click', () => showTab('saved'));
  showTab('posts');

  const observerPosts = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting && !loadingPosts && !postsGrid.classList.contains('hidden')) {
      loadPosts();
    }
  }, { rootMargin: '200px' });
  observerPosts.observe(postsLoader);

  const observerSaved = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting && !loadingSaved && !savedGrid.classList.contains('hidden')) {
      loadSaved();
    }
  }, { rootMargin: '200px' });
  observerSaved.observe(savedLoader);

  function loadPosts() {
    loadingPosts = true;
    fetch(`${postsUrl}?page=${postsPage}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.text())
    .then(html => {
      if (postsPage === 1) {
        postsGrid.innerHTML = '';
      }
      // اگر متنی با «No posts found.» بود، پایان
      if (html.includes('No posts found.')) {
        postsGrid.innerHTML = html;
        postsLoader.classList.add('hidden');
        observerPosts.disconnect();
      } else {
        postsGrid.insertAdjacentHTML('beforeend', html);
        if (postsPage === 1) postsLoader.classList.add('hidden');
        postsPage++;
      }
    })
    .finally(() => {
      loadingPosts = false;
    });
  }

  function loadSaved() {
    loadingSaved = true;
    fetch(`${savedUrl}?page=${savedPage}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.text())
    .then(html => {
      if (savedPage === 1) {
        savedGrid.innerHTML = '';
      }
      if (html.includes('No posts found.')) {
        savedGrid.innerHTML = html;
        savedLoader.classList.add('hidden');
        observerSaved.disconnect();
      } else {
        savedGrid.insertAdjacentHTML('beforeend', html);
        if (savedPage === 1) savedLoader.classList.add('hidden');
        savedPage++;
      }
    })
    .finally(() => {
      loadingSaved = false;
    });
  }

  document.getElementById('profileFollowBtn')?.addEventListener('click', () => {
    const btn = document.getElementById('profileFollowBtn');
    fetch(followToggle, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: new URLSearchParams({ id: window.profileUserId })
    })
    .then(r => r.json())
    .then(data => {
      btn.textContent = data.follow ? 'Unfollow' : 'Follow';
    });
  });

  const modal = document.getElementById('followModal');
  const list  = document.getElementById('followModalList');
  const title = document.getElementById('followModalTitle');

  document.getElementById('followersBtn').addEventListener('click', () => openModal('Followers', followersUrl));
  document.getElementById('followingBtn').addEventListener('click', () => openModal('Following', followingUrl));
  document.getElementById('closeFollowModal').addEventListener('click', () => modal.classList.add('hidden'));

  function openModal(txt, url) {
    title.textContent = txt;
    list.innerHTML = '<li class="px-4 py-2 text-zinc-500">Loading…</li>';
    modal.classList.remove('hidden');
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(res => res.json())
      .then(json => {
        list.innerHTML = '';
        json.users.forEach(u => {
          list.insertAdjacentHTML('beforeend', `
            <li class="flex items-center px-4 py-2 hover:bg-zinc-700 cursor-pointer">
              <img src="${u.photo_url || '/static/images/default_avatar.png'}"
                   class="w-8 h-8 rounded-full mr-3"/>
              <span>${u.full_name}</span>
            </li>`);
        });
      });
  }

  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^|;)\\s*'+name+'\\s*=\\s*([^;]+)'));
    return match ? match.pop() : '';
  }
});
