import { chromium } from 'playwright-core';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
const root = path.resolve(import.meta.dirname, '../..');
const out = path.join(root, '.impeccable/review');
await mkdir(out, {recursive:true});
const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const problems = [];
const externalRequests = new Set();
const report = [];
for (const [width, height] of [[1440,1000],[390,844],[1100,850]]) {
  const page = await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});
  page.on('pageerror', e => problems.push(`${width}: ${e.message}`));
  page.on('request', r => { if (!r.url().startsWith('http://127.0.0.1:4173/')) externalRequests.add(r.url()); });
  for (let id = 1; id <= 11; id++) {
    const response = await page.goto(`http://127.0.0.1:4173/variants/${id}/`,{waitUntil:'networkidle'});
    if (response.status() !== 200) problems.push(`${width}, ${id}: ${response.status()}`);
    await page.evaluate(() => document.fonts.ready);
    const measurements = await page.evaluate(() => ({
      overflow:document.documentElement.scrollWidth > innerWidth,
      broken:[...document.images].filter(i=>!i.complete || i.naturalWidth===0).map(i=>i.src),
      heading:document.querySelector('h1').getBoundingClientRect().toJSON(),
      room:document.querySelector('.room,.video-preview').getBoundingClientRect().toJSON(),
      chat:document.querySelector('.watch-party')?.getBoundingClientRect().toJSON(),
      film:document.querySelector('.film-title')?.getBoundingClientRect().toJSON(),
      copy:document.querySelector('.hero-copy')?.getBoundingClientRect().toJSON(),
      top:document.querySelector('.room-top')?.getBoundingClientRect().toJSON(),
    }));
    report.push({width,id,...measurements});
    if(measurements.overflow) problems.push(`${width}, ${id}: horizontal overflow`);
    if(measurements.broken.length) problems.push(`${width}, ${id}: broken images`);
    if(id===1 || width!==1100) {
      await page.screenshot({path:path.join(out,id===1 ? width===1440?'desktop.png':width===390?'mobile.png':`user-${width}.png`:`variant-${id}-${width}.png`),fullPage:true});
      if (id===1) await page.screenshot({path:path.join(out,`hero-${width}.png`),fullPage:false});
    }
    await page.locator('.demo-toggle,[data-demo-play]').click({trial:true,timeout:3000});
    if(id>1){
      await page.locator('[data-source="Telegram"]').first().click();
      if(await page.locator('[data-source-label]').first().textContent()!=='Telegram')problems.push(`${width}, ${id}: source selector failed`);
    }
  }
  if(width===390) {
    await page.goto('http://127.0.0.1:4173/');
    await page.getByRole('tab',{name:'Свидание на расстоянии'}).click();
    if(await page.locator('#room-name').textContent() !== 'Вечер на двоих') problems.push('Scenario selection failed');
    await page.getByRole('tab',{name:'Свидание на расстоянии'}).press('ArrowRight');
    if(await page.locator('#room-name').textContent() !== 'Наш семейный вечер') problems.push('Keyboard tabs failed');
    await page.locator('.demo-toggle').click();
    await page.waitForTimeout(1150);
    if(Number(await page.locator('#timeline').inputValue()) < 1) problems.push('Playback demo did not advance');
    await page.locator('.demo-toggle').click();
    if(await page.locator('.demo-toggle').getAttribute('aria-pressed')!=='false') problems.push('Playback demo did not pause');
    await page.getByRole('link',{name:'Как получить доступ'}).click();
    if(!await page.locator('#access-details').evaluate(e=>e.open)) problems.push('Invitation details did not open');
    await page.getByText('Когда откроется доступ для всех?',{exact:true}).click();
    if(!await page.getByText('Точная дата пока не объявлена.',{exact:false}).isVisible()) problems.push('FAQ failed');
    if(await page.locator('form,input:not([type="range"])').count()) problems.push('Unexpected registration form');
  }
  await page.close();
}
const gallery = await browser.newPage({viewport:{width:1440,height:1000}});
await gallery.goto('http://127.0.0.1:4173/gallery.html',{waitUntil:'networkidle'});
if(await gallery.locator('.card').count() !== 11) problems.push('Gallery must have 11 variants');
await gallery.screenshot({path:path.join(out,'gallery.png'),fullPage:true});
await browser.close();
await writeFile(path.join(out,'qa.json'),JSON.stringify({problems,externalRequests:[...externalRequests],measurements:report},null,2));
console.log(JSON.stringify({problems,externalRequests:[...externalRequests],variants:11,viewports:[1440,390,1100],screenshots:out},null,2));
if(problems.length || externalRequests.size) process.exitCode = 1;
