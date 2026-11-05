"""Build the eleven offline Ryadom landing variants and preview gallery."""
from pathlib import Path
import json
from build_brands import BRANDS, brand_page
from media_samples import add_media_samples

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
VARIANTS = [
    ('Кинозал', 'cinema', '#101212', '#191c1b', '#f3f3e9', '#a9b1ac', '#dcf78a', '#18200a', 'Хорошее кино.<br>Лучшая <em>компания.</em>', 'Расстояние меняет планы.<br>Но не ваши вечера вместе.'),

]

# The user subsequently requested ten independent brands, preserving only 1.
VARIANTS = VARIANTS[:1] + [(b['name'], b['slug'], b['bg'], b['bg'], b['fg'], b['fg'], b['accent'], b['bg'], b['tag'], b['tag']) for b in BRANDS]

ARROW = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
LOGO = '<svg viewBox="0 0 40 32" fill="none" aria-hidden="true"><rect x="2" y="6" width="23" height="23" rx="7" stroke="currentColor" stroke-width="2.5"/><rect x="15" y="2" width="23" height="23" rx="7" fill="currentColor"/><path d="m24 9 7 4.5-7 4.5V9Z" fill="var(--bg)"/></svg>'
HTML = '''<!doctype html>
<html lang="ru" data-layout="__LAYOUT__" style="__TOKENS__">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Рядом — пространство для совместного просмотра на расстоянии. Закрытое тестирование, участие по персональному приглашению.">
<meta name="theme-color" content="__BG__"><meta name="color-scheme" content="__SCHEME__">
<title>Рядом — смотрим вместе, где бы вы ни были</title>
<link rel="icon" href="__ASSETS__favicon.svg" type="image/svg+xml">
<link rel="preload" href="__ASSETS__manrope.ttf" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="__ASSETS__style.css"><script defer src="__ASSETS__app.js"></script>
</head>
<body>
<a class="skip" href="#main">Перейти к содержимому</a>
<header class="header shell">
  <a class="brand" href="#" aria-label="Рядом — на главную">__LOGO__<span>рядом</span></a>
  <nav aria-label="Главная навигация"><a href="#how">Как это работает</a><a href="#moments">Для ваших вечеров</a><a href="#questions">Вопросы</a></nav>
  <a class="header-access" href="#access"><span class="status-dot"></span>Закрытая бета<span class="tiny-arrow">↗</span></a>
</header>
<main id="main">
  <section class="hero shell" aria-labelledby="hero-title">
    <div class="hero-intro">
      <h1 id="hero-title">__HEADLINE__</h1>
      <div class="hero-copy"><p>__TAGLINE__</p><a class="button primary" href="#demo">Посмотреть, как это устроено __ARROW__</a><span class="hero-note">Совместный просмотр. Свои люди. Один момент.</span></div>
    </div>
    <div class="room" id="demo" aria-label="Демонстрация комнаты совместного просмотра">
      <div class="room-scene"><img src="__ASSETS__mountains.jpg" alt="Горная долина и снежные вершины" width="1920" height="1280" fetchpriority="high"><div class="scene-shade"></div></div>
      <div class="room-top"><span class="room-name"><span class="status-dot"></span><span id="room-name">Вечер с друзьями</span></span><span class="demo-tag">Демонстрация</span></div>
      <div class="film-title"><span>Маленькое путешествие в большой вечер</span><h2>Там, где тихо</h2><p>Пример комнаты · пейзажная сцена</p></div>
      <div class="watch-party" aria-label="Пример переписки">
        <div class="party-heading"><span>Все свои</span><span class="party-count">3 участника</span></div>
        <div class="party-people"><span class="avatar avatar-a">А</span><span class="avatar avatar-m">М</span><span class="avatar avatar-y">Я</span><span class="sync-label"><span class="status-dot"></span>На одной секунде</span></div>
        <div class="chat-line"><span class="chat-name">Аня <time>20:41</time></span><p id="chat-one">Вот бы сейчас туда.</p></div>
        <div class="chat-line"><span class="chat-name">Миша <time>20:41</time></span><p id="chat-two">Главное — с такой компанией.</p></div>
        <div class="chat-reply"><span>Вот ради таких вечеров.</span><span class="chat-check">✓✓</span></div>
        <span class="chat-caption">Пример чата будущей комнаты</span>
      </div>
      <div class="demo-controls"><button type="button" class="demo-toggle" aria-label="Запустить демонстрацию синхронизации" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path class="play-shape" d="m9 5 11 7-11 7Z" fill="currentColor"/><path class="pause-shape" d="M8 5h3v14H8zm6 0h3v14h-3z" fill="currentColor"/></svg></button><span class="demo-time" id="demo-time">00:00</span><input aria-label="Позиция в демонстрации" id="timeline" type="range" min="0" max="180" value="0"><span class="demo-duration">03:00</span><span class="control-caption" id="control-caption">Демо синхронизации</span></div>
    </div>
    <div class="room-caption"><span>Разные города. Один диван — хотя бы по ощущениям.</span><span>Интерфейс-пример · без воспроизведения видео</span></div>
  </section>
  <section class="how shell section" id="how" aria-labelledby="how-title">
    <div class="section-intro"><h2 id="how-title">Ближе, чем<br>кажется.</h2><p>Мы создаём место, где не нужно отсчитывать<br class="desktop-br"> «три, два, один» перед нажатием на play.<br class="desktop-br"> Только вы, история на экране и ваши люди.</p></div>
    <div class="steps">
      <article><span class="step-symbol">__ROOMICON__</span><h3>Ваша комната</h3><p>Личное пространство для своего круга. Приглашение связывает тех, кто хочет провести вечер вместе.</p></article>
      <article><span class="step-symbol">__SYNCICON__</span><h3>Общий момент</h3><p>В основе идеи — синхронный просмотр. Пауза для разговора становится паузой для всей компании.</p></article>
      <article><span class="step-symbol">__CHATICON__</span><h3>Разговор рядом</h3><p>Реакции на неожиданный поворот и обсуждение после титров. Всё, за что мы любим смотреть вместе.</p></article>
    </div>
  </section>
  <section class="moments section" id="moments" aria-labelledby="moments-title"><div class="shell moments-inner">
    <div class="moments-copy"><h2 id="moments-title">Для вечеров,<br>которые <em>сближают.</em></h2><p>Повод найдётся. Компания — уже есть.</p>
    <div class="scenario-tabs" role="tablist" aria-label="Сценарии совместного просмотра">
      <button type="button" role="tab" id="tab-friends" aria-controls="scenario-panel" aria-selected="true" data-scenario="friends">Кино с друзьями __ARROW__</button>
      <button type="button" role="tab" id="tab-date" aria-controls="scenario-panel" aria-selected="false" tabindex="-1" data-scenario="date">Свидание на расстоянии __ARROW__</button>
      <button type="button" role="tab" id="tab-family" aria-controls="scenario-panel" aria-selected="false" tabindex="-1" data-scenario="family">Семейная традиция __ARROW__</button>
    </div></div>
    <div class="scenario-panel" role="tabpanel" id="scenario-panel" aria-labelledby="tab-friends" tabindex="0"><span class="scenario-quote" aria-hidden="true">“</span><h3 id="scenario-title">Ваш киноклуб.<br>Без дресс-кода.</h3><p id="scenario-description">Снова спорить о концовке, смеяться в один момент и выбирать, что смотреть дальше. Просто теперь не обязательно жить в одном городе.</p><div class="scenario-bottom"><span class="small-avatars"><span class="avatar avatar-a">А</span><span class="avatar avatar-m">М</span><span class="avatar avatar-y">Я</span></span><span id="scenario-note">Плед и попкорн — каждый приносит свои.</span></div></div>
  </div></section>
  <section class="access shell section" id="access" aria-labelledby="access-title">
    <div class="access-copy"><h2 id="access-title">Сначала —<br>небольшим <em>кругом.</em></h2><p>«Рядом» сейчас в закрытом тестировании. Мы доводим до ума комнаты и совместный просмотр, прежде чем пригласить всех.</p><p>Присоединиться можно по персональной ссылке от команды. Открытой регистрации пока нет.</p><a class="text-link" href="#access-details">Как получить доступ __ARROW__</a>
    <details id="access-details" class="access-details"><summary>Об участии в тестировании</summary><p>Новых участников приглашает команда проекта. Если вам уже прислали приглашение, воспользуйтесь ссылкой из сообщения. На этой странице нельзя создать аккаунт или активировать код.</p></details></div>
    <div class="invite" aria-label="Участие только по приглашению"><div class="invite-top"><span class="brand">__LOGO__<span>рядом</span></span><span class="invite-label">Личное приглашение</span></div><div class="invite-body"><span>Для хорошей<br>компании всегда<br>найдётся <em>место.</em></span></div><div class="invite-bottom"><span class="status-dot"></span><span>Закрытое тестирование</span><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 10V7a5 5 0 0 1 10 0v3M5 10h14v11H5z" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="15" r="1" fill="currentColor"/></svg></div></div>
  </section>
  <section class="faq shell section" id="questions" aria-labelledby="faq-title"><h2 id="faq-title">Если интересно.</h2><div class="faq-list">
    <details><summary>Что такое «Рядом»?</summary><p>Проект сервиса для совместного просмотра видео на расстоянии. Мы работаем над приватными комнатами, синхронизацией и общением во время просмотра.</p></details>
    <details><summary>Можно зарегистрироваться прямо сейчас?</summary><p>Открытая регистрация пока недоступна. Во время закрытого тестирования подключение проходит по персональным приглашениям от команды.</p></details>
    <details><summary>Какие видео можно будет смотреть?</summary><p>Поддерживаемые источники и форматы уточняются в ходе тестирования. «Рядом» не предоставляет собственный каталог фильмов и не заменяет подписки на видеосервисы.</p></details>
    <details><summary>Когда откроется доступ для всех?</summary><p>Точная дата пока не объявлена. Сначала мы хотим проверить основной сценарий с небольшой группой участников и учесть их обратную связь.</p></details>
    <details><summary>Это уже работающая комната просмотра?</summary><p>На этой странице показан интерактивный пример интерфейса. Он не воспроизводит видео и не соединяет участников. Доступ к тестовой версии предоставляется отдельно.</p></details>
  </div></section>
</main>
<footer class="footer shell"><a class="brand" href="#" aria-label="Рядом — наверх">__LOGO__<span>рядом</span></a><span>Быть вместе — уже хороший план.</span><span>© 2026 Рядом · Закрытое тестирование</span></footer>
</body></html>'''

ICONS = {
    '__ROOMICON__': '<svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><rect x="4" y="6" width="24" height="18" rx="4"/><path d="M11 28h10M16 24v4m-4-17 8 4-8 4v-8Z"/></svg>',
    '__SYNCICON__': '<svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M7 9a11 11 0 0 1 18 2l2 4m0-8v8h-8M25 23A11 11 0 0 1 7 21l-2-4m0 8v-8h8"/></svg>',
    '__CHATICON__': '<svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M5 5h22v17H14l-9 6V5Z"/><path d="M11 12h10m-10 5h6"/></svg>',
}

def page(i: int, assets: str):
    if i > 0:
        return add_media_samples(brand_page(i, assets), i, assets)
    name, layout, bg, surface, fg, muted, accent, ink, headline, tagline = VARIANTS[i]
    tokens = f'--bg:{bg};--surface:{surface};--fg:{fg};--muted:{muted};--accent:{accent};--accent-ink:{ink}'
    result = HTML
    for key, value in {'__LAYOUT__': layout, '__TOKENS__': tokens, '__BG__': bg, '__SCHEME__': 'dark' if bg in ['#101212','#100f16','#242823','#102322','#131d2b'] else 'light', '__ASSETS__': assets, '__HEADLINE__': headline, '__TAGLINE__': tagline, '__ARROW__': ARROW, '__LOGO__': LOGO, **ICONS}.items():
        result = result.replace(key, value)
    return add_media_samples(result, i, assets)

def build():
    SITE.mkdir(exist_ok=True)
    # Ship the same asset bytes on Windows, Linux and GitHub checkout.
    for asset in (SITE/'assets').rglob('*'):
        if asset.is_file() and asset.suffix.lower() in {'.css','.js','.svg','.txt','.json'}:
            raw = asset.read_bytes()
            normalized = raw.replace(b'\r\n', b'\n')
            if normalized != raw:
                asset.write_bytes(normalized)
    (SITE / 'index.html').write_text(page(0, 'assets/'), encoding='utf-8', newline='\n')
    for i, variant in enumerate(VARIANTS):
        folder = SITE / 'variants' / str(i + 1)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'index.html').write_text(page(i, '../../assets/'), encoding='utf-8', newline='\n')
    for b in BRANDS:
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="{b["bg"]}"/><text x="32" y="47" text-anchor="middle" font-family="Georgia,serif" font-size="47" fill="{b["accent"]}">{b["name"][0]}</text></svg>'
        (SITE/'assets/brands'/f'{b["slug"]}.svg').write_text(svg,encoding='utf-8',newline='\n')
    (SITE / 'variants.json').write_text(json.dumps([{'id': i+1, 'name': 'Рядом' if i==0 else v[0], 'layout': v[1], 'description': 'Оригинальный Рядом · сохранён' if i==0 else BRANDS[i-1]['layout'], 'bg': v[2], 'fg': v[4], 'accent':v[6], 'headline':v[8].replace('<br>',' ').replace('<em>','').replace('</em>','')} for i,v in enumerate(VARIANTS)], ensure_ascii=False, indent=2), encoding='utf-8')
    print('Built 11 variants and the default landing.')

if __name__ == '__main__':
    build()
