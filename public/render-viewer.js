(() => {
const viewer = document.querySelector('#render-viewer');
const viewerImage = viewer.querySelector('.render-viewer-image');
const caption = viewer.querySelector('#render-viewer-title');
const status = viewer.querySelector('.render-viewer-status');
let trigger;
let previousOverflow = '';
let previousPadding = '';
let request = 0;

function closeViewer() { viewer.close(); }
viewer.querySelector('.render-viewer-close').addEventListener('click', closeViewer);
viewer.addEventListener('click', event => {
  if (event.target === viewer || event.target === viewer.querySelector('.render-viewer-stage')) closeViewer();
});
viewer.addEventListener('close', () => {
  request++;
  document.body.style.overflow = previousOverflow;
  document.body.style.paddingRight = previousPadding;
  viewerImage.removeAttribute('src');
  trigger?.focus({preventScroll:true});
});

document.querySelectorAll('.render-link').forEach(link => {
  link.addEventListener('click', event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    trigger = link;
    const image = link.querySelector('img');
    const ticket = ++request;
    caption.textContent = image.alt;
    viewerImage.alt = image.alt;
    viewerImage.width = Number(link.dataset.fullWidth);
    viewerImage.height = Number(link.dataset.fullHeight);
    viewerImage.src = image.currentSrc || image.src;
    status.textContent = 'Loading original resolution…';
    previousOverflow = document.body.style.overflow;
    previousPadding = document.body.style.paddingRight;
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    document.body.style.paddingRight = `${parseFloat(getComputedStyle(document.body).paddingRight) + scrollbarWidth}px`;
    document.body.style.overflow = 'hidden';
    viewer.showModal();
    const original = new Image();
    original.onload = () => {
      if (ticket !== request || !viewer.open) return;
      viewerImage.src = original.src;
      status.textContent = `${original.naturalWidth} × ${original.naturalHeight} · Original resolution`;
    };
    original.onerror = () => {
      if (ticket === request && viewer.open) status.textContent = 'Original image could not load. Close and try again.';
    };
    original.src = link.href;
  });
});
})();
