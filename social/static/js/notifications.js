// static/js/notifications.js
document.addEventListener('DOMContentLoaded', () => {
  function getCookie(name) {
    let v = document.cookie.match('(^|;)\\s*'+name+'\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  const csrftoken = getCookie('csrftoken');

  document.querySelectorAll('.notif-mark-read-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      fetch(btn.dataset.url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          btn.remove();
          const badge = document.querySelector('a[href$="/notifications/"] .bg-red-500');
          if (badge) {
            let count = parseInt(badge.textContent) - 1;
            if (count > 0) {
              badge.textContent = count;
            } else {
              badge.remove();
            }
          }
        }
      });
    });
  });
});
