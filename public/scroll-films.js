const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const saveData = navigator.connection?.saveData === true;
const clock = seconds => `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${Math.floor(seconds % 60).toString().padStart(2, '0')}`;
let scheduled = false;
const films = [];

class ScrollFilm {
  constructor(element) {
    this.element = element;
    this.stage = element.querySelector('.film-stage');
    this.video = element.querySelector('video');
    this.poster = element.querySelector('.film-poster');
    this.button = element.querySelector('.film-mode');
    this.status = element.querySelector('.film-instruction');
    this.progress = element.querySelector('[role="progressbar"]');
    this.time = element.querySelector('.film-time');
    this.duration = Number(element.dataset.duration);
    this.manual = reducedMotion.matches || saveData;
    this.loaded = false;
    this.ready = false;
    this.seeking = false;
    this.target = 0;
    this.slowSeeks = 0;
    this.seekTimer = null;
    this.loadTimer = null;
    this.video.muted = true;
    this.video.defaultMuted = true;
    this.video.controls = this.manual;
    this.video.autoplay = false;
    element.classList.add('enhanced');
    element.classList.toggle('manual-mode', this.manual);
    this.setLabels();
    this.layout();
    this.button.addEventListener('click', () => this.manual ? this.useScroll() : this.useControls(false));
    this.video.addEventListener('loadedmetadata', () => {
      if (!Number.isFinite(this.video.duration) || this.video.duration <= 0) return this.fail();
      this.duration = this.video.duration;
      this.layout();
      this.update();
    });
    this.video.addEventListener('loadeddata', () => {
      clearTimeout(this.loadTimer);
      this.ready = true;
      this.element.dataset.ready = 'true';
      this.poster.hidden = true;
      this.video.classList.add('has-frame');
      this.update();
    });
    this.video.addEventListener('seeked', () => {
      clearTimeout(this.seekTimer);
      const elapsed = performance.now() - (this.seekStart || performance.now());
      this.seeking = false;
      this.poster.hidden = true;
      this.video.classList.add('has-frame');
      this.element.dataset.currentTime = this.video.currentTime.toFixed(4);
      this.time.textContent = `${clock(this.video.currentTime)} / ${clock(this.duration)}`;
      if (elapsed > 1100) this.slowSeeks += 1; else this.slowSeeks = 0;
      if (!this.manual && this.slowSeeks >= 3) return this.useControls(false, 'Use the playback controls for this film.');
      if (!this.manual) this.seek();
    });
    this.video.addEventListener('timeupdate', () => {
      this.element.dataset.currentTime = this.video.currentTime.toFixed(4);
      if (this.manual) this.time.textContent = `${clock(this.video.currentTime)} / ${clock(this.duration)}`;
    });
    this.video.addEventListener('play', () => { if (!this.manual) this.video.pause(); });
    this.video.addEventListener('error', () => this.fail());
  }

  setLabels() {
    this.status.textContent = this.manual ? 'Watch the film at your own pace' : 'Scroll to explore the film';
    this.button.textContent = this.manual ? 'Use scroll' : 'Playback controls';
    this.progress.hidden = this.manual;
    this.time.textContent = `00:00 / ${clock(this.duration)}`;
  }

  layout() {
    const ratio = Number(this.element.dataset.ratio);
    const mobile = window.innerWidth < 700;
    const inset = mobile ? 12 : 20;
    const viewportHeight = document.documentElement.clientHeight;
    const height = Math.min(viewportHeight - inset * 2, Math.max(viewportHeight * (mobile ? 0.82 : 0.8), this.stage.clientWidth / ratio + 96));
    this.stageHeight = Math.max(240, height);
    this.inset = inset;
    const pixelsPerSecond = Number(this.element.dataset.pixelsPerSecond || 70);
    const mobileFactor = mobile ? 0.9 : 1.2;
    this.distance = clamp(this.duration * pixelsPerSecond * mobileFactor, Math.max(1500, viewportHeight * 2), 6500);
    this.element.style.setProperty('--stage-height', `${this.stageHeight}px`);
    this.element.style.setProperty('--scroll-distance', `${this.distance}px`);
    this.element.style.setProperty('--sticky-top', `${inset}px`);
    this.element.dataset.scrollDistance = this.distance.toFixed(1);
  }

  load() {
    if (this.loaded || this.element.classList.contains('film-error')) return;
    this.loaded = true;
    this.video.preload = 'auto';
    this.video.src = this.video.dataset.src;
    this.video.load();
    this.loadTimer = setTimeout(() => {
      if (!this.ready && !this.manual) this.useControls(false, 'The film is loading. You can continue to the images below.');
    }, 12000);
  }

  release() {
    if (!this.loaded) return;
    this.video.pause();
    clearTimeout(this.loadTimer);
    clearTimeout(this.seekTimer);
    this.seeking = false;
    this.loaded = false;
    this.ready = false;
    this.poster.hidden = false;
    this.video.classList.remove('has-frame');
    this.element.dataset.ready = 'false';
    this.video.removeAttribute('src');
    this.video.load();
  }

  update() {
    const rect = this.element.getBoundingClientRect();
    const near = rect.top < window.innerHeight + 800 && rect.bottom > -800;
    if (near) this.load();
    else if (rect.bottom < -1800 || rect.top > window.innerHeight + 1800) this.release();
    if (this.manual) {
      if (rect.bottom <= 0 || rect.top >= window.innerHeight) this.video.pause();
      return;
    }
    const rawProgress = clamp((this.inset - rect.top) / this.distance);
    const hold = Number(this.element.dataset.hold || 0.035);
    const progress = clamp(rawProgress / (1 - hold));
    this.target = Math.min(Math.max(0, this.duration - 0.001), progress * this.duration);
    this.progress.style.setProperty('--progress', progress);
    this.progress.setAttribute('aria-valuenow', `${Math.round(progress * 100)}`);
    this.progress.setAttribute('aria-valuetext', `${clock(this.target)} of ${clock(this.duration)}`);
    this.element.dataset.progress = progress.toFixed(5);
    this.element.dataset.targetTime = this.target.toFixed(4);
    if (this.ready && near) this.seek();
  }

  seek() {
    if (this.manual || !this.ready || this.seeking || !this.loaded || document.hidden) return;
    if (Math.abs(this.video.currentTime - this.target) < 0.018) return;
    this.video.pause();
    this.seeking = true;
    this.seekStart = performance.now();
    this.seekTimer = setTimeout(() => {
      this.seeking = false;
      this.useControls(false, 'Use the playback controls for this film.');
    }, 3500);
    try { this.video.currentTime = this.target; }
    catch { clearTimeout(this.seekTimer); this.seeking = false; this.fail(); }
  }

  useControls(play, message) {
    const rect = this.element.getBoundingClientRect();
    const wasPinned = !this.manual && rect.top < this.inset && rect.bottom > this.inset;
    const top = window.scrollY + rect.top;
    this.manual = true;
    this.video.pause();
    clearTimeout(this.seekTimer);
    this.seeking = false;
    this.element.classList.add('manual-mode');
    this.video.controls = true;
    this.setLabels();
    if (message) this.status.textContent = message;
    if (wasPinned) window.scrollTo({top: Math.max(0, top - this.inset), behavior: 'instant'});
    this.load();
    if (play) {
      this.poster.hidden = true;
      this.video.classList.add('has-frame');
      this.video.play().then(() => { this.button.hidden = true; }).catch(() => { this.status.textContent = 'Press play on the film to begin.'; });
    }
  }

  useScroll() {
    const top = window.scrollY + this.element.getBoundingClientRect().top;
    const progress = clamp(this.video.currentTime / this.duration);
    this.manual = false;
    this.video.pause();
    this.video.controls = false;
    this.element.classList.remove('manual-mode');
    this.setLabels();
    this.layout();
    window.scrollTo({top:Math.max(0,top-this.inset+progress*(1-Number(this.element.dataset.hold||0.035))*this.distance),behavior:'instant'});
    this.update();
  }

  fail() {
    clearTimeout(this.loadTimer);
    if (this.element.classList.contains('film-error')) return;
    this.useControls(false);
    this.element.classList.add('film-error');
    this.poster.hidden = false;
    this.video.classList.remove('has-frame');
    this.button.hidden = true;
    this.status.textContent = 'The film is unavailable. Continue to the project images below.';
  }
}

document.querySelectorAll('.film[data-duration]').forEach(element => films.push(new ScrollFilm(element)));
function updateFilms() { scheduled = false; films.forEach(film => film.update()); }
function schedule() { if (!scheduled) { scheduled = true; requestAnimationFrame(updateFilms); } }
window.addEventListener('scroll', schedule, { passive: true });
window.addEventListener('resize', () => { films.forEach(film => film.layout()); schedule(); }, { passive: true });
document.addEventListener('visibilitychange', () => { films.forEach(film => film.video.pause()); if (!document.hidden) schedule(); });
reducedMotion.addEventListener('change', event => { if (event.matches) films.forEach(film => film.useControls(false)); });
schedule();
