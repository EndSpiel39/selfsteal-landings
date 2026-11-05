'use strict';
const timeline = document.querySelector('#timeline');
const toggle = document.querySelector('.demo-toggle');
const room = document.querySelector('.room');
let demoInterval = null;
const renderTime = () => {
  const value = Number(timeline.value);
  document.querySelector('#demo-time').textContent = `${Math.floor(value / 60).toString().padStart(2, '0')}:${(value % 60).toString().padStart(2, '0')}`;
  timeline.style.setProperty('--progress', `${value / 180 * 100}%`);
  timeline.setAttribute('aria-valuetext', `${Math.floor(value / 60)} мин ${value % 60} сек демонстрации`);
};
function stopDemo() {
  clearInterval(demoInterval);
  demoInterval = null;
  toggle.setAttribute('aria-pressed', 'false');
  toggle.setAttribute('aria-label', 'Запустить демонстрацию синхронизации');
  room.dataset.playing = 'false';
  document.querySelector('#control-caption').textContent = 'Демо синхронизации';
}
toggle.addEventListener('click', () => {
  if (demoInterval !== null) { stopDemo(); return; }
  if (Number(timeline.value) >= 180) timeline.value = '0';
  toggle.setAttribute('aria-pressed', 'true');
  toggle.setAttribute('aria-label', 'Приостановить демонстрацию');
  room.dataset.playing = 'true';
  document.querySelector('#control-caption').textContent = 'Общая позиция просмотра';
  renderTime();
  demoInterval = setInterval(() => {
    timeline.value = String(Math.min(180, Number(timeline.value) + 1));
    renderTime();
    if (Number(timeline.value) >= 180) stopDemo();
  }, 1000);
});
timeline.addEventListener('input', renderTime);
document.addEventListener('visibilitychange', () => { if (document.hidden) stopDemo(); });
renderTime();

const scenarios = {
  friends: {title:'Ваш киноклуб.<br>Без дресс-кода.',description:'Снова спорить о концовке, смеяться в один момент и выбирать, что смотреть дальше. Просто теперь не обязательно жить в одном городе.',note:'Плед и попкорн — каждый приносит свои.',room:'Вечер с друзьями',one:'Вот бы сейчас туда.',two:'Главное — с такой компанией.'},
  date: {title:'Встреча, которую<br>не нужно откладывать.',description:'Пока билеты в другой город ждут своего часа, можно выбрать историю на двоих. И никуда не торопиться после финальных титров.',note:'Одно настроение на двоих.',room:'Вечер на двоих',one:'Давай досмотрим и ещё поговорим?',two:'У меня как раз есть весь вечер.'},
  family: {title:'Ваш воскресный<br>вечер. Снова вместе.',description:'У каждого свои дела и часовые пояса. Пусть хотя бы один вечер будет общим — с любимой историей и родными голосами по ту сторону экрана.',note:'Расстояние — временно. Традиции — с вами.',room:'Наш семейный вечер',one:'Все собрались? Можно начинать.',two:'Теперь точно все. Включаем!'}
};
const tabs = [...document.querySelectorAll('[role="tab"]')];
function selectScenario(tab) {
  const data = scenarios[tab.dataset.scenario];
  tabs.forEach(item => { item.setAttribute('aria-selected', String(item === tab)); item.tabIndex = item === tab ? 0 : -1; });
  document.querySelector('#scenario-panel').setAttribute('aria-labelledby', tab.id);
  document.querySelector('#scenario-title').innerHTML = data.title;
  document.querySelector('#scenario-description').textContent = data.description;
  document.querySelector('#scenario-note').textContent = data.note;
  document.querySelector('#room-name').textContent = data.room;
  document.querySelector('#chat-one').textContent = data.one;
  document.querySelector('#chat-two').textContent = data.two;
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectScenario(tab));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) { event.preventDefault(); selectScenario(tabs[next]); tabs[next].focus(); }
  });
});
document.querySelector('a[href="#access-details"]').addEventListener('click', () => { document.querySelector('#access-details').open = true; });
