import {chromium} from 'playwright-core';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../..');
const out=path.join(root,'.impeccable/review/media');
await mkdir(out,{recursive:true});
const catalog=JSON.parse(await readFile(path.join(root,'site/assets/media/catalog.json'),'utf8'));
if(catalog.length!==22 || new Set(catalog.map(c=>c.title)).size!==22)throw Error('Need 22 different trailers');
if(catalog.some(c=>!['VK Видео','Rutube'].includes(c.provider)))throw Error('Unexpected media provider');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const issues=[];
for(const width of [1440,390]){
 const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});
 const external=[];
 let activated=false;
 page.on('pageerror',e=>issues.push(e.message));
 page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:4173/')&&!/^https:\/\/(vkvideo\.ru|rutube\.ru)\//.test(r.url()))external.push(r.url());});
 // Stub the remote frame only for interaction tests. Live provider playback is
 // separately checked in the browser; no fake media is shipped to the website.
 await page.route(/^https:\/\/(vkvideo\.ru|rutube\.ru)\//,route=>route.fulfill({status:200,contentType:'text/html',body:'<!doctype html><html lang="ru"><title>Test provider frame</title><p>Provider frame test fixture</p></html>'}));
 for(let id=1;id<=11;id++){
  activated=false;
  await page.goto(`http://127.0.0.1:4173/variants/${id}/`,{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const items=catalog.filter(c=>c.landing===id);
  if(items.length!==2 || new Set(items.map(c=>c.provider)).size!==2)issues.push(`Site${id} needs both providers`);

  await page.locator('#examples').scrollIntoViewIfNeeded();
  await page.evaluate(()=>Promise.all([...document.querySelectorAll('#examples img')].map(img=>img.decode())));
  if(await page.locator('.sample-choice').count()!==2)issues.push(`Bad choices${id}`);
  for(let n=0;n<2;n++){
   await page.locator(`[data-sample-index="${n}"]`).click();
   if(await page.locator('.sample-active-title').textContent()!==items[n].title)issues.push(`Bad title${id}/${n}`);
   if(await page.locator('.sample-open').getAttribute('href')!==items[n].url)issues.push(`Bad source link${id}/${n}`);

   activated=true;

   const frame=page.locator('.sample-iframe-slot iframe');
   const actual=new URL(await frame.getAttribute('src'));
   const expected=new URL(items[n].embed);
   if(actual.origin!==expected.origin||actual.pathname!==expected.pathname)issues.push(`Bad iframe${id}/${n}`);
   if(items[n].provider==='VK Видео'?(actual.searchParams.get('autoplay')!=='1'||actual.searchParams.get('mute')!=='1'):(actual.searchParams.get('autoplay')!=='true'||actual.searchParams.get('autostartmute')!=='true'))issues.push('Muted autoplay missing');
   await page.locator('.sample-stop').click();
   if(await page.locator('#examples iframe').count())issues.push('Closing player failed to stop iframe');
   if(!await page.locator('.sample-start').evaluate(e=>e===document.activeElement))issues.push('Focus not restored');
   activated=false;
  }
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))issues.push(`Overflow${id}/${width}`);
  if([1,6,7,11].includes(id))await page.locator('#examples').screenshot({path:path.join(out,`site-${id}-${width}.png`)});
 }
 if(external.length)issues.push(...external.map(u=>'Unsolicited remote request '+u));
 await page.close();
}
await browser.close();
await writeFile(path.join(out,'checks.json'),JSON.stringify({issues,trailers:22,sites:11,viewports:[1440,390],remoteFrames:'stubbed for interaction test; live playback checked separately'},null,2));
console.log(JSON.stringify({issues,trailers:22,sites:11,viewports:[1440,390]},null,2));
if(issues.length)process.exitCode=1;
