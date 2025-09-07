document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.post-slider').forEach(slider => {
    // parse image URLs from the data-images attribute
    const images = JSON.parse(slider.dataset.images)
    let idx = parseInt(slider.dataset.index, 10) || 0

    const imgElem = slider.querySelector('img')
    const prevBtn = slider.querySelector('.prev-btn')
    const nextBtn = slider.querySelector('.next-btn')

    function showImage(newIdx) {
      idx = (newIdx + images.length) % images.length
      imgElem.src = images[idx]
      slider.dataset.index = idx
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', e => {
        e.preventDefault()
        showImage(idx - 1)
      })
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', e => {
        e.preventDefault()
        showImage(idx + 1)
      })
    }

    imgElem.addEventListener('click', () => showImage(idx + 1))
  })
})