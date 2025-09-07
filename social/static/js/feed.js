// static/js/feed.js

document.addEventListener('DOMContentLoaded', () => {

  function getCookie(name) {
    let v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  const csrftoken = getCookie('csrftoken');

  const { likeUrl, saveUrl, followUrl, inboxUrl } = window.socialUrls;

  document.body.addEventListener('click', e => {
    const btn = e.target.closest('.like-btn');
    if (!btn) return;
    e.preventDefault();

    fetch(likeUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: new URLSearchParams({ post_id: btn.dataset.postId })
    })
    .then(res => res.json())
    .then(data => {
      const svg = btn.querySelector('svg');
      svg.classList.toggle('text-red-500', data.liked);
      svg.classList.toggle('text-zinc-300', !data.liked);


      const container = btn.closest('article')    // feed_ajax.html
                      || btn.closest('main')      // detail.html
                      || document;
      const countEl = container.querySelector('.likes-count');
      if (countEl) {
        countEl.textContent = data.likes_count + ' likes';
      }
    });
  });

  document.querySelectorAll('.save-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      fetch(saveUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: new URLSearchParams({ post_id: btn.dataset.postId })
      })
      .then(res => res.json())
      .then(data => {
        const svg = btn.querySelector('svg');
        svg.classList.toggle('text-purple-400', data.saved);
        svg.classList.toggle('text-zinc-300', !data.saved);
      });
    });
  });

  document.querySelectorAll('.suggest-follow-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      fetch(followUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: new URLSearchParams({ id: btn.dataset.userId })
      })
      .then(res => res.json())
      .then(data => {
        btn.textContent = data.follow ? 'Unfollow' : 'Follow';
      });
    });
  });

  document.querySelectorAll('.message-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const recipient = btn.dataset.recipient;
      const postId    = btn.dataset.postId;
      window.location.href = `${inboxUrl}?start=${recipient}&post=${postId}`;
    });
  });

  let page = 2;
  const postContainer  = document.getElementById('postContainer');
  const skeleton       = document.getElementById('skeletonContainer');
  const loader         = document.getElementById('loader');
  new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
      loader.classList.remove('hidden');
      fetch(`?page=${page}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(res => res.text())
      .then(html => {
        if (page === 2 && skeleton) skeleton.remove();
        loader.classList.add('hidden');
        postContainer.insertAdjacentHTML('beforeend', html);
        page++;
      });
    }
  }, { rootMargin: '0px 0px 200px 0px' }).observe(loader);

  const modal    = document.getElementById('detailModal');
  const modalCon = document.getElementById('modalContent');
  postContainer.addEventListener('click', e => {
    const trigger = e.target.closest('.comment-btn, .view-comments');
    if (!trigger) return;
    e.preventDefault();
    fetch(trigger.dataset.detailUrl, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.text())
    .then(html => {
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const main = doc.querySelector('main');
      if (!main) return;
      modalCon.innerHTML = main.innerHTML;
      modal.classList.remove('hidden');
      initModalCommentAjax();
    });
  });
  document.getElementById('closeModal')
          .addEventListener('click', () => modal.classList.add('hidden'));

  function initModalCommentAjax() {
    const form = modalCon.querySelector('.comment-form');
    const list = modalCon.querySelector('.comment-list');
    if (!form || !list) return;
    form.addEventListener('submit', e => {
      e.preventDefault();
      const data = new FormData(form);
      fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: data
      })
      .then(res => res.json())
      .then(obj => {
        const div = document.createElement('div');
        div.className = 'flex items-start space-x-3';
        div.innerHTML = `
          <img src="${obj.user_photo || '/static/images/default_avatar.png'}"
               class="w-8 h-8 rounded-full object-cover flex-none"/>
          <div class="flex-1">
            <p class="text-sm">
              <span class="font-semibold">${obj.name}</span> ${obj.body}
            </p>
            <p class="text-xs text-zinc-500">${obj.created}</p>
          </div>
        `;
        list.appendChild(div);
        form.reset();
      });
    });
  }
});
