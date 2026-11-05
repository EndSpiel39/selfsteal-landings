'use strict';
const sources = document.querySelectorAll('[data-source]');
sources.forEach(button => button.addEventListener('click', () => {
  sources.forEach(other => other.setAttribute('aria-pressed',String(other.dataset.source===button.dataset.source)));
  document.querySelectorAll('[data-source-label]').forEach(label => label.textContent=button.dataset.source);
}));
const timeline = document.querySelector('[data-demo-seek]');
const play = document.querySelector('[data-demo-play]');
let timer = null;
function render() {
  const n = Number(timeline.value);
  const label = `${String(Math.floor(n/60)).padStart(2,'0')}:${String(n%60).padStart(2,'0')}`;
  document.querySelectorAll('[data-clock]').forEach(node => node.textContent=label);
  timeline.style.setProperty('--position',`${n/180*100}%`);
  timeline.setAttribute('aria-valuetext',`${Math.floor(n/60)} мин ${n%60} сек демонстрации`);
}
function stop() {clearInterval(timer);timer=null;play.setAttribute('aria-pressed','false');play.setAttribute('aria-label','Запустить демонстрацию');}
play.addEventListener('click', () => {
  if(timer!==null){stop();return;}
  if(Number(timeline.value)>=180)timeline.value='0';
  play.setAttribute('aria-pressed','true');play.setAttribute('aria-label','Приостановить демонстрацию');
  render();timer=setInterval(()=>{timeline.value=String(Number(timeline.value)+1);render();if(Number(timeline.value)>=180)stop();},1000);
});
timeline.addEventListener('input',render);
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
document.querySelectorAll('a[href="#invite"]').forEach(link=>link.addEventListener('click',()=>{document.querySelector('#invite').open=true;}));
render();
