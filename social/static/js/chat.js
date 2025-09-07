// static/js/chat.js

document.addEventListener('DOMContentLoaded', () => {
  // CSRF helper
  function getCookie(name) {
    const m = document.cookie.match(new RegExp('(^|;)\\s*'+name+'\\s*=\\s*([^;]+)'));
    return m ? m.pop() : '';
  }
  const csrftoken = getCookie('csrftoken');
  const inboxUrl  = window.socialUrls.inboxUrl;

  document.querySelectorAll('.thread-item').forEach(item => {
    item.addEventListener('click', () => {
      const other = item.dataset.recipient;
      if (inboxUrl && other) {
        window.location.href = `${inboxUrl}?start=${other}`;
      }
    });
  });

  // ارسال پیام
  const chatForm = document.getElementById('chatForm');
  const msgList  = document.getElementById('messageList');
  if (msgList) msgList.scrollTop = msgList.scrollHeight;
  if (!chatForm) return;

  chatForm.addEventListener('submit', async e => {
    e.preventDefault();
    const url  = chatForm.action;
    const data = new FormData(chatForm);

    try {
      const res = await fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken':     csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: data
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const msg = await res.json();
      appendMessage(msg);
      chatForm.reset();
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  });

  function appendMessage({ sender_photo, content, timestamp, is_mine }) {
    if (!msgList) return;
    const wrapper = document.createElement('div');
    if (is_mine) {
      wrapper.classList.add('flex','justify-end');
      wrapper.innerHTML = `
        <div>
          <div class="px-4 py-2 bg-purple-600 text-white rounded-lg">
            ${content}
          </div>
          <p class="text-xs text-purple-300 mt-1">${timestamp}</p>
        </div>`;
    } else {
      wrapper.classList.add('flex','items-start','space-x-3');
      const avatarHtml = sender_photo
        ? `<img src="${sender_photo}" class="w-8 h-8 rounded-full object-cover flex-none"/>`
        : `<div class="w-8 h-8 rounded-full bg-zinc-700 flex-none"></div>`;
      wrapper.innerHTML = `
        ${avatarHtml}
        <div>
          <div class="px-4 py-2 bg-zinc-800 text-zinc-100 rounded-lg">${content}</div>
          <p class="text-xs text-zinc-500 mt-1">${timestamp}</p>
        </div>`;
    }
    msgList.appendChild(wrapper);
    msgList.scrollTop = msgList.scrollHeight;
  }
});
