"""Render real, click-to-load VK Video/Rutube examples for every landing."""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]

def add_media_samples(html, index, assets):
    entries = json.loads((ROOT/'site/assets/media/catalog.json').read_text(encoding='utf-8'))
    clips = [item for item in entries if item['landing'] == index+1]
    if len(clips) < 2:
        raise ValueError(f'Landing {index+1} needs at least two different videos')
    first = clips[0]
    playlist = ''
    for n, clip in enumerate(clips):
        playlist += f'''<button type="button" class="sample-choice" data-sample-index="{n}" aria-pressed="{'true' if n==0 else 'false'}"><img src="{assets}{escape(clip['poster'])}" alt="" width="160" height="90" loading="lazy"><span><span class="sample-provider">{escape(clip['provider'])} · {escape(clip['kind'])}</span><strong>{escape(clip['title'])}</strong><span class="sample-author">{escape(clip['author'])}</span></span></button>'''
    payload = json.dumps([{**clip, 'poster': assets+clip['poster']} for clip in clips],ensure_ascii=False).replace('<','\\u003c')
    markup = f'''<section class="watch-samples {'shell' if index==0 else 'wrap'}" id="examples" aria-labelledby="samples-title"><div class="samples-heading"><h2 id="samples-title">Сначала —<br>короткий трейлер.</h2><p>Настоящие видео из VK Видео и Rutube.<br>Выберите историю под настроение.</p></div><div class="samples-layout"><div class="sample-main"><div class="sample-screen"><img class="sample-poster" src="{assets}{escape(first['poster'])}" alt="Обложка трейлера «{escape(first['title'])}»" width="960" height="540" loading="lazy"><button class="sample-start" type="button"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 11 7-11 7Z" fill="currentColor"/></svg><span>Смотреть в плеере {escape(first['provider'])}</span></button><div class="sample-iframe-slot"></div></div><div class="sample-meta"><div><h3 class="sample-active-title">{escape(first['title'])}</h3><p class="sample-active-author">{escape(first['author'])}</p></div><a class="sample-open" href="{escape(first['url'])}" target="_blank" rel="noopener noreferrer">Открыть в {escape(first['provider'])}<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 17 17 7M7 7h10v10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></a></div><div class="sample-status-row"><p class="sample-status" role="status">Автозапуск без звука. Включить звук можно в плеере.</p><button class="sample-stop" type="button" hidden>Закрыть плеер</button></div></div><div class="sample-list" role="group" aria-label="Выбрать трейлер">{playlist}<p class="sample-explainer">Это примеры просмотра по ссылке. Комнаты с друзьями доступны отдельно по приглашению. Если плеер недоступен, откройте видео на площадке.</p></div></div><script type="application/json" data-sample-catalog>{payload}</script></section>'''
    html = html.replace('</section>','</section>'+markup,1)
    html = html.replace('</head>',f'<link rel="stylesheet" href="{assets}video-samples.css"><script defer src="{assets}video-samples.js"></script></head>',1)
    return html
