/* Run with PLAYWRIGHT_MODULE pointing to a Playwright installation when not local. */
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('fs/promises');
const path = require('path');
const {pathToFileURL} = require('url');
const assert = require('assert/strict');
const root = path.resolve(__dirname,'..');
const names = process.argv.slice(2).length ? process.argv.slice(2) : ['signal-desk','editorial-dossier','evidence-table'];
(async () => {
 const browser = await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE ? {executablePath:process.env.CHROMIUM_EXECUTABLE} : {})});
 const report = [];
 let prior=[]; try {prior=JSON.parse(await fs.readFile(path.join(root,'verification','interaction-results.json'),'utf8'))} catch {}
 for (const name of names) {
  const context = await browser.newContext({viewport:{width:1440,height:900},acceptDownloads:true,offline:true});
  const page = await context.newPage(), errors=[], requests=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
  const url=pathToFileURL(path.join(root,name+'.html')).href;
  await page.goto(url);
  await page.evaluate(()=>document.fonts.ready);
  await page.waitForFunction(()=>document.querySelector('#evidence-dialog'));
  const initial = await page.evaluate(()=>({decision:D.project.decision,claims:D.claims.map(c=>c.status),sources:JSON.stringify(D.sources), fonts:[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family)}));
  assert.equal(initial.decision,'Kill');
  for (const [w,h] of [[1440,900],[1024,768]]) {
   await page.setViewportSize({width:w,height:h});
   await page.evaluate(()=>window.scrollTo(0,0));
   const dimensions = await page.evaluate(()=>({width:document.documentElement.scrollWidth,viewport:innerWidth}));
   assert.ok(dimensions.width<=w,`${name} overflow at ${w}: ${dimensions.width}`);
   await page.screenshot({path:path.join(root,'screenshots',`${name}-${w}.png`)});
  }
  await page.setViewportSize({width:1440,height:900});
  if (await page.locator('[data-nav="history"]').count()) {
   await page.locator('[data-nav="history"]').click();
   assert.ok(await page.locator('#history-panel').isVisible());
   await page.locator('[data-nav="claims"]').click();
   assert.ok(await page.locator('#claims-panel').isVisible());
   await page.locator('#claims-panel [data-annotate="H02"]').click();
   assert.ok((await page.locator('#note-target').innerText()).startsWith('H02'));
   await page.locator('#annotation-dialog [data-close-dialog]').first().click();
   await page.locator('[data-nav="issues"]').click();
   for(let stage=0;stage<6;stage++) {
    await page.locator(`[data-stage="${stage}"]`).click();
    assert.equal(await page.locator(`[data-stage="${stage}"]`).getAttribute('aria-selected'),'true');
   }
  } else {
   for(const href of await page.locator('nav a[href^="#"]').evaluateAll(els=>els.map(el=>el.getAttribute('href')))) {
    await page.locator(`nav a[href="${href}"]`).click();
    assert.equal(new URL(page.url()).hash,href);
   }
  }
  for (const id of ['R01-R1-02','R01-R1-03','R01-R2-03','R01-R1-01']) {
   await page.locator(`[data-issue="${id}"]`).first().click();
   assert.ok((await page.locator('body').innerText()).includes(await page.evaluate(id=>UI.issue(id).title,id)),`${name}: issue ${id} not displayed`);
  }
  const sourceButton=page.locator('button[data-evidence="initial-r2"]').first();
  await sourceButton.click();
  assert.equal(await page.locator('#evidence-dialog').evaluate(el=>el.open),true);
  assert.equal(await page.locator('#source-text').textContent(),await page.evaluate(()=>D.sources['initial-r2'].text));
  await page.selectOption('#source-select','sac');
  assert.equal(await page.locator('#source-text').textContent(),await page.evaluate(()=>D.sources.sac.text));
  await page.locator('#evidence-dialog [data-close-dialog]').click();
  // Opening a reader from a scrolled content position must preserve the underlying page.
  await page.evaluate(()=>window.scrollTo(0,Math.min(600,document.documentElement.scrollHeight-innerHeight)));
  const before=await page.evaluate(()=>scrollY);
  await page.evaluate(()=>UI.showEvidence('rebuttal'));
  await page.locator('#evidence-dialog [data-close-dialog]').click();
  assert.ok(Math.abs((await page.evaluate(()=>scrollY))-before)<=2,`${name}: reader lost scroll position`);
  const comment='Check the negative-input boundary.\nPreserve this wording: <img src=x onerror="window.fixtureInjected=true">\n```text\n原文 preserved.';
  await page.locator('[data-annotate="R01-R1-01"]').first().click();
  await page.selectOption('#note-type','Needs evidence');
  await page.fill('#note-text',comment);
  await page.locator('#annotation-form button[type="submit"]').click();
  assert.equal(await page.locator('[data-note-count]').first().textContent(),'1');
  await page.locator('[data-show-notes]').first().click();
  assert.ok((await page.locator('#notes-list').innerText()).includes(comment));
  assert.equal(await page.evaluate(()=>Boolean(window.fixtureInjected)),false);
  await page.locator('[data-edit-note]').click();
  const edited=comment+'\nEdited after checking the source.';
  await page.fill('#note-text',edited);
  await page.locator('#annotation-form button[type="submit"]').click();
  await page.reload();
  await page.evaluate(()=>document.fonts.ready);
  assert.equal(await page.locator('[data-note-count]').first().textContent(),'1',`${name}: reload lost saved note`);
  await page.locator('[data-show-notes]').first().click();
  assert.ok((await page.locator('#notes-list').innerText()).includes(edited));
  const downloaded = page.waitForEvent('download');
  await page.locator('#notes-dialog [data-export-feedback]').click();
  const download=await downloaded;
  assert.equal(download.suggestedFilename(),'review_feedback.md');
  const exported=await fs.readFile(await download.path(),'utf8');
  for(const fragment of ['faster-nonnegative-projection','v01','Review round: 1 of 1','R01-R1-01','reviewer-R2-initial.md',edited,'SHA-256']) assert.ok(exported.includes(fragment),`${name}: export lost ${fragment.slice(0,40)}`);
  await page.locator('[data-delete-note]').click();
  assert.equal(await page.locator('[data-note-count]').first().textContent(),'0');
  await page.locator('#notes-dialog [data-close-dialog]').click();
  for(const id of ['H01','H02','H03','decision','review-history','experiments']) {
   await page.evaluate(id=>UI.annotate(id),id);
   assert.ok((await page.locator('#note-target').innerText()).startsWith(id));
   await page.locator('#annotation-dialog [data-close-dialog]').first().click();
  }
  // Saved draft composition survives reload before submission.
  await page.evaluate(()=>UI.annotate('H01'));
  await page.fill('#note-text','An unfinished draft stays local.');
  await page.locator('#annotation-dialog [data-close-dialog]').first().click();
  await page.reload();
  await page.evaluate(()=>UI.annotate('H01'));
  assert.equal(await page.inputValue('#note-text'),'An unfinished draft stays local.');
  await page.locator('#annotation-dialog [data-close-dialog]').first().click();
  const unchanged=await page.evaluate(snapshot=>JSON.stringify(D.sources)===snapshot,initial.sources);
  assert.ok(unchanged,`${name}: evidence changed`);
  const badLinks=await page.evaluate(()=>[...document.querySelectorAll('a[href^="#"]')].filter(a=>a.getAttribute('href').length>1&&!document.getElementById(a.getAttribute('href').slice(1))).map(a=>a.getAttribute('href')));
  assert.deepEqual(badLinks,[]);
  assert.deepEqual(errors,[],`${name} console errors`);
  assert.deepEqual(requests,[],`${name} network dependencies`);
  await context.close();
  const fallback=await browser.newContext({viewport:{width:1024,height:768},acceptDownloads:true,offline:true});
  await fallback.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Storage unavailable','SecurityError')}}));
  const p=await fallback.newPage();
  await p.goto(url);
  assert.ok((await p.locator('[data-storage-status]').first().textContent()).includes('Session only'));
  await p.evaluate(()=>UI.annotate('decision'));
  await p.fill('#note-text','Keep this session-only note.');
  await p.locator('#annotation-form button[type="submit"]').click();
  assert.equal(await p.locator('[data-note-count]').first().textContent(),'1');
  const fallbackDownload=p.waitForEvent('download');
  await p.locator('[data-export-feedback]').first().click();
  assert.ok((await fs.readFile(await(await fallbackDownload).path(),'utf8')).includes('Keep this session-only note.'));
  await fallback.close();
  report.push({direction:name,artifactSha256:require('crypto').createHash('sha256').update(await fs.readFile(path.join(root,name+'.html'))).digest('hex'),result:'passed',viewports:['1440x900','1024x768'],checks:['functional section navigation','offline rendering','embedded fonts','four issue groups','source text fidelity','source switching','reading position','annotation creation/edit/deletion','verbatim safe text','local persistence','draft recovery','Markdown feedback download','claim and section targets','storage-denied fallback','immutable evidence','anchors','zero console errors','zero network requests'],loadedFonts:initial.fonts});
  console.log(`${name}: passed`);
 }
 await fs.writeFile(path.join(root,'verification','interaction-results.json'),JSON.stringify([...prior.filter(item=>!names.includes(item.direction)),...report],null,2)+'\n');
 await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
