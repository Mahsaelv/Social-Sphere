document.addEventListener('DOMContentLoaded', () => {
  const form       = document.getElementById('createPostForm');
  const descInput  = form.querySelector('textarea[name="description"]');
  const counter    = document.getElementById('captionCounter');
  const img1Input  = form.querySelector('input[name="image1"]');
  const img2Input  = form.querySelector('input[name="image2"]');
  const preview1   = document.getElementById('preview1');
  const preview2   = document.getElementById('preview2');
  const publishBtn = document.getElementById('publishBtn');

  function updatePublishState() {
    publishBtn.disabled = !(img1Input.files.length || img2Input.files.length);
  }
  img1Input.addEventListener('change', () => { previewFile(img1Input, preview1); updatePublishState(); });
  img2Input.addEventListener('change', () => { previewFile(img2Input, preview2); updatePublishState(); });

  descInput.addEventListener('input', () => {
    const len = descInput.value.length;
    counter.textContent = `${len}/2200`;
  });

  // Image preview helper
  function previewFile(input, container) {
    container.innerHTML = '';
    const file = input.files[0];
    if (!file) {
      container.innerHTML = `<span class="text-zinc-500">No preview</span>`;
      return;
    }
    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    img.className = 'w-full h-full object-cover';
    container.appendChild(img);
  }

  [preview1, preview2].forEach(c => {
    c.innerHTML = `<span class="text-zinc-500">No preview</span>`;
  });
  updatePublishState();
});
