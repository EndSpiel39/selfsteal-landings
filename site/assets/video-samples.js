'use strict';
for (const section of document.querySelectorAll('.watch-samples')) {
  const clips = JSON.parse(section.querySelector('[data-sample-catalog]').textContent);
  const choices = [...section.querySelectorAll('[data-sample-index]')];
  const screen = section.querySelector('.sample-screen');
  const slot = section.querySelector('.sample-iframe-slot');
  const start = section.querySelector('.sample-start');
  const stop = section.querySelector('.sample-stop');
  const status = section.querySelector('.sample-status');
  const poster = section.querySelector('.sample-poster');
  let selected = 0;
  let currentFrame = null;
  let autoStopped = false;
  function trustedEmbed(clip) {
    const url = new URL(clip.embed);
    if(url.protocol !== 'https:') return false;
    if(clip.provider === 'VK Видео') return url.hostname === 'vkvideo.ru' && url.pathname === '/video_ext.php' && /^-?\d+$/.test(url.searchParams.get('oid') || '') && /^\d+$/.test(url.searchParams.get('id') || '');
    return clip.provider === 'Rutube' && url.hostname === 'rutube.ru' && /^\/play\/embed\/[a-f0-9]{32}\/?$/.test(url.pathname);
  }
  function closePlayer(focus=false) {
    currentFrame = null;
    slot.replaceChildren();
    screen.classList.remove('player-active');
    start.disabled = false;
    start.hidden = false;
    stop.hidden = true;
    status.textContent = 'Автозапуск без звука при появлении блока на экране. Нажмите play, если браузер его остановил.';
    if(focus)start.focus();
  }
  function select(index) {
    closePlayer();
    selected = index;
    const clip = clips[index];
    choices.forEach((choice,i)=>choice.setAttribute('aria-pressed',String(i===index)));
    poster.src = clip.poster;
    poster.alt = `Обложка трейлера «${clip.title}»`;
    section.querySelector('.sample-active-title').textContent = clip.title;
    section.querySelector('.sample-active-author').textContent = clip.author;
    const link = section.querySelector('.sample-open');
    link.href = clip.url;
    link.firstChild.textContent = `Открыть в ${clip.provider}`;
    start.querySelector('span').textContent = `Смотреть в плеере ${clip.provider}`;
    autoStopped = false;
    openPlayer();
  }
  choices.forEach((choice,index)=>choice.addEventListener('click',()=>select(index)));
  stop.addEventListener('click',()=>{autoStopped=true;closePlayer(true);});
  function openPlayer() {
    if(currentFrame)return;
    autoStopped=false;
    const clip = clips[selected];
    if(!trustedEmbed(clip)) {
      status.textContent = 'Адрес плеера не распознан. Откройте видео по ссылке на площадку.';
      return;
    }
    // Browser-compatible autoplay: both providers receive muted startup.
    // Begin when visible, or immediately after the user selects a trailer.
    const iframe = document.createElement('iframe');
    currentFrame = iframe;
    iframe.title = `${clip.title} — ${clip.provider}`;
    iframe.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
    iframe.allowFullscreen = true;
    iframe.referrerPolicy = 'no-referrer';
    iframe.addEventListener('load',()=>{if(currentFrame===iframe)status.textContent=`Управление видео — в плеере ${clip.provider}.`;});
    iframe.addEventListener('error',()=>{if(currentFrame===iframe)status.textContent='Не удалось загрузить плеер. Откройте видео на площадке по ссылке выше.';});
    const playerUrl = new URL(clip.embed);
    if(clip.provider==='VK Видео'){playerUrl.searchParams.set('autoplay','1');playerUrl.searchParams.set('mute','1');}
    else {playerUrl.searchParams.set('autoplay','true');playerUrl.searchParams.set('autostartmute','true');}
    iframe.src = playerUrl.href;
    start.hidden = true;
    stop.hidden = false;
    screen.classList.add('player-active');
    status.textContent = `Загружаем плеер ${clip.provider}… Если видео не появится, откройте его на площадке.`;
    slot.replaceChildren(iframe);
  }
  start.addEventListener('click',openPlayer);
  if('IntersectionObserver' in window){
    const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)&&!autoStopped)openPlayer();},{threshold:.2});
    observer.observe(screen);
  }
}
