/* Generated-report integration test. Requires Playwright only for development. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('fs/promises'),path=require('path'),os=require('os'),assert=require('assert/strict');
const {execFileSync}=require('child_process'),{pathToFileURL}=require('url');
const repo=path.resolve(__dirname,'..'),python=process.env.PYTHON||'python3';
const render=workspace=>JSON.parse(execFileSync(python,[path.join(repo,'scripts/render_review.py'),workspace],{encoding:'utf8'}));
const read=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const write=async(p,d)=>fs.writeFile(p,JSON.stringify(d,null,2));
const settled=page=>page.waitForFunction(()=>document.querySelector('#github-app').dataset.route===(location.hash.slice(1)||'overview'));
(async()=>{
 const temp=await fs.mkdtemp(path.join(os.tmpdir(),'idea-shaokao-review-browser-'));
 const workspace=path.join(temp,'adaptive-cache');
 execFileSync(python,['-c',"import sys;sys.path.insert(0,sys.argv[1]);from review_fixture import make_workspace,add_research_design;_,i=make_workspace(sys.argv[2]);add_research_design(sys.argv[2],i)",path.join(repo,'tests'),workspace]);
 const rendered=render(workspace),html=path.join(workspace,'final/review.html'),url=pathToFileURL(html).href;
 const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
 try{
 const context=await browser.newContext({viewport:{width:1440,height:900},offline:true,acceptDownloads:true});
 const page=await context.newPage(),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await page.goto(url);assert.ok((await page.locator('#github-app').innerText()).includes('SAC recommends Proceed'));
 assert.equal(await page.locator('[data-section="overview"]').getAttribute('aria-current'),'page');
 assert.equal(await page.locator('.round-summary').count(),2);
 await page.locator('[data-section="issues"]').click();await settled(page);
 assert.equal(await page.locator('.issue-row').count(),1);
 const sourceSnapshot=await page.evaluate(()=>JSON.stringify(D.sources));
 for(const [width,height] of [[1440,900],[1024,768]]){
  await page.setViewportSize({width,height});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 }
 await page.locator('[data-state="all"]').click();assert.equal(await page.locator('.issue-row').count(),2);
 await page.selectOption('#round-filter','2');assert.equal(await page.locator('.issue-row').count(),1);
 await page.selectOption('#round-filter','all');await page.selectOption('#severity-filter','Critical');assert.equal(await page.locator('.issue-row').count(),1);
 await page.selectOption('#severity-filter','all');await page.fill('#issue-query','R01-R2-01');assert.equal(await page.locator('.issue-row').count(),1);
 await page.locator('[data-issue="I-1"]').click();await page.waitForURL('**#issue/I-1');await page.locator('.comment').first().waitFor();assert.equal(await page.locator('.comment').count(),3);
 await page.locator('[data-evidence="initial"]').first().click();assert.equal(await page.locator('#source-text').textContent(),await page.evaluate(()=>D.sources.initial.text));
 await page.selectOption('#source-select','response');assert.equal(await page.locator('#source-text').textContent(),await page.evaluate(()=>D.sources.response.text));await page.locator('#evidence-dialog [data-close-dialog]').click();
 const comment='Keep this wording: <img src=x onerror="window.injected=true">\n```\nA source-specific question.';
 await page.locator('[data-annotate="issue:I-1"]').click();await page.fill('#note-text',comment);await page.locator('#annotation-form [type="submit"]').click();
 await page.locator('[data-show-notes]').first().click();assert.equal(await page.evaluate(()=>!!window.injected),false);
 await page.locator('[data-edit-note]').click();await page.fill('#note-text',comment+'\nEdited.');await page.locator('#annotation-form [type="submit"]').click();
 await page.evaluate(()=>UI.annotate('claim:H-cost'));await page.fill('#note-text','A claim-specific note.');await page.locator('#annotation-form [type="submit"]').click();
 for(const [target,text] of [['claim:H-cost','Unfinished claim draft.'],['issue:I-2','Unfinished issue draft.']]){await page.evaluate(t=>UI.annotate(t),target);await page.fill('#note-text',text);await page.locator('#annotation-dialog [data-close-dialog]').first().click()}
 await page.reload();assert.equal(await page.locator('[data-note-count]').first().textContent(),'2');assert.equal(await page.evaluate(()=>UI.backup().drafts.length),2);
 const backupDownload=page.waitForEvent('download');await page.locator('[data-show-notes]').first().click();await page.locator('[data-export-backup]').click();const download=await backupDownload;const backup=await read(await download.path());assert.equal(backup.notes.length,2);assert.equal(backup.drafts.length,2);await page.locator('#notes-dialog [data-close-dialog]').click();
 assert.equal(await page.evaluate(snapshot=>JSON.stringify(D.sources)===snapshot,sourceSnapshot),true);
 // Regenerate the same HTML at a later version with changed sources and removed targets.
 const statePath=path.join(workspace,'state.json'),indexPath=path.join(workspace,'final/review-data.json');
 const state=await read(statePath);state.proposal_version='v02';state.current_round=3;await write(statePath,state);
 const index=await read(indexPath);index.issues=[];await write(indexPath,index);
 await fs.appendFile(path.join(workspace,'proposal/v01/proposal.md'),'\nA revised claim record, still unmeasured.\n');
 assert.equal(render(workspace).workspace_id,rendered.workspace_id);
 await page.reload();await page.waitForURL('**#issues');assert.equal(await page.locator('[data-note-count]').first().textContent(),'2');
 await page.locator('[data-show-notes]').first().click();const notes=await page.locator('#notes-list').innerText();assert.ok(notes.includes('Target no longer appears'));assert.ok(notes.includes('Source content has changed'));assert.ok(notes.includes(comment));
 await page.locator('[data-resume-draft]').last().click();assert.equal(await page.inputValue('#note-text'),'Unfinished issue draft.');await page.locator('#annotation-dialog [data-close-dialog]').first().click();
 const mdDownload=page.waitForEvent('download');await page.locator('[data-export-feedback]').first().click();const md=await fs.readFile(await(await mdDownload).path(),'utf8');for(const text of ['Current proposal: v02','Annotated proposal: v01','issue:I-1',comment,'SHA-256'])assert.ok(md.includes(text));
 await page.locator('[data-section="overview"]').click();await settled(page);assert.ok((await page.locator('#github-app').innerText()).includes('Hypothesis — untested'));assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.locator('[data-section="reviews"]').click();await settled(page);let history=await page.locator('#github-app').innerText();assert.ok(history.includes('6/8'));assert.ok(history.includes('Not recorded'));assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.locator('.round-link[href="#reviews/1"]').click();await settled(page);history=await page.locator('#github-app').innerText();assert.ok(history.includes('5/8'));assert.ok(history.includes('Author response'));assert.ok(!history.includes('6/8'));
 await page.locator('[data-annotate="round:1"]').click();await page.fill('#note-text','A note on the first round.');await page.locator('#annotation-form [type="submit"]').click();const roundNote=(await page.evaluate(()=>UI.backup())).notes.find(n=>n.target==='round:1');assert.equal(roundNote.context.round,1);assert.equal(roundNote.context.version,'v01');assert.equal(roundNote.context.stage,'proposal');
 await page.locator('.round-link[href="#reviews/2"]').click();await settled(page);assert.ok((await page.locator('.round-snapshot').innerText()).includes('proposal stays at v01'));
 await page.locator('[data-section="plan"]').click();await settled(page);assert.equal(await page.locator('.paper-section').count(),8);assert.equal(await page.locator('.experiment-block').count(),1);
 const fullPlan=await page.locator('.plan-document').innerText();for(const text of ['64 MiB','five trace seeds','No measured miss rate','Section design','Hypothesis','Failure / stop criterion'])assert.ok(fullPlan.includes(text),text);
 await page.locator('[data-plan-link="paper"]').click();await page.waitForURL('**#plan/paper');await page.waitForFunction(()=>document.querySelector('#plan-paper').getBoundingClientRect().top<40);
 await page.locator('.experiment-references a').first().click();await page.waitForURL('**#plan/experiments/E-early');await page.waitForFunction(()=>document.querySelector('#experiment-E-early').classList.contains('target-highlight'));assert.ok(await page.locator('#experiment-E-early').isVisible());
 await page.locator('[data-annotate="experiment:E-early"]').click();await page.fill('#note-text','Check the total 64 MiB budget.');await page.locator('#annotation-form [type="submit"]').click();assert.ok((await page.evaluate(()=>UI.backup())).notes.some(n=>n.target==='experiment:E-early'&&n.context.sources.length));
 for(const [width,height] of [[1440,900],[1024,768],[768,1024],[390,844]]){await page.setViewportSize({width,height});for(const route of ['overview','reviews/1','reviews/2','plan','plan/paper','plan/experiments/E-early','issues','sources']){await page.goto(url+'#'+route);await settled(page);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${width}px ${route}`)}}
 await page.setViewportSize({width:1024,height:768});
 await page.locator('[data-section="sources"]').click();await settled(page);assert.equal(await page.locator('.source-row').count(),9);
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);await context.close();
 // A copied report and a fresh browser can restore portable annotations and drafts.
 const portable=path.join(temp,'portable-review.html');await fs.copyFile(html,portable);
 const restored=await browser.newContext({viewport:{width:1024,height:768},offline:true,acceptDownloads:true});const p=await restored.newPage();await p.goto(pathToFileURL(portable).href);assert.equal(await p.locator('[data-note-count]').first().textContent(),'0');
 await p.locator('[data-show-notes]').first().click();await p.locator('#notes-import').setInputFiles({name:'review_notes.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(backup))});await p.waitForFunction(()=>document.querySelector('[data-note-count]').textContent==='2');assert.equal(await p.locator('[data-note-count]').first().textContent(),'2');assert.equal(await p.evaluate(()=>UI.backup().drafts.length),2);
 const conflicting=JSON.parse(JSON.stringify(backup));conflicting.notes[0].text='An alternate edited version.';conflicting.drafts=[{key:'edit:'+backup.notes[0].id,editingId:backup.notes[0].id,target:backup.notes[0].target,context:backup.notes[0].context,type:'Question',text:'Draft for the imported alternate version.'}];await p.evaluate(b=>UI.restore(b),conflicting);assert.equal(await p.locator('[data-note-count]').first().textContent(),'3');const restoredDraft=await p.evaluate(()=>UI.backup().drafts.find(d=>d.text==='Draft for the imported alternate version.'));assert.notEqual(restoredDraft.editingId,backup.notes[0].id);assert.equal(await p.evaluate(id=>UI.backup().notes.find(n=>n.id===id).text,restoredDraft.editingId),'An alternate edited version.');
 const wrong={...backup,workspace_id:'another-workspace'};await p.locator('#notes-import').setInputFiles({name:'wrong.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(wrong))});await p.locator('#import-error').waitFor({state:'visible'});assert.ok(await p.locator('#import-error').isVisible());assert.equal(await p.locator('[data-note-count]').first().textContent(),'3');
 await p.locator('[data-delete-note]').first().click();assert.equal(await p.locator('[data-note-count]').first().textContent(),'2');await restored.close();
 const fallback=await browser.newContext({viewport:{width:1024,height:768},offline:true,acceptDownloads:true});await fallback.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Storage denied','SecurityError')}}));const f=await fallback.newPage();await f.goto(url);assert.ok(await f.locator('#github-app .storage-fallback').isVisible());await f.locator('[data-section="issues"]').click();await settled(f);await f.locator('#github-app [data-annotate="section:decision"]').click();await f.fill('#note-text','Session-only feedback.');await f.locator('#annotation-form [type="submit"]').click();const sessionDownload=f.waitForEvent('download');await f.locator('[data-export-feedback]').first().click();assert.ok((await fs.readFile(await(await sessionDownload).path(),'utf8')).includes('Session-only feedback.'));await fallback.close();
 const partial=path.join(temp,'partial');execFileSync(python,['-c',"import sys;sys.path.insert(0,sys.argv[1]);from review_fixture import make_workspace,write_index;from pathlib import Path;import json;p=Path(sys.argv[2]);s,i=make_workspace(p,slug='partial-study',mode='single_agent');s.update(current_round=0,status='budget_stopped',recommendation='Undetermined');(p/'state.json').write_text(json.dumps(s));i['overview'].update(assessor='Author',recommendation='Undetermined',sources=['report']);[(i.__setitem__(k,[])) for k in ('issues','claims','reviewers','timeline','experiments')];write_index(p,i)",path.join(repo,'tests'),partial]);render(partial);const partialPage=await browser.newPage({viewport:{width:1024,height:768}});const partialURL=pathToFileURL(path.join(partial,'final/review.html')).href;await partialPage.goto(partialURL);let body=await partialPage.locator('body').innerText();assert.ok(body.includes('Structured self-review'));assert.ok(body.includes('No recommendation recorded'));assert.ok(!body.includes('SAC recommends'));await partialPage.locator('[data-section="issues"]').click();await settled(partialPage);assert.ok((await partialPage.locator('body').innerText()).includes('No concerns recorded'));await partialPage.locator('[data-section="reviews"]').click();await settled(partialPage);assert.ok((await partialPage.locator('body').innerText()).includes('No review rounds recorded'));await partialPage.locator('[data-section="plan"]').click();await settled(partialPage);assert.ok((await partialPage.locator('body').innerText()).includes('A section-by-section paper design has not been recorded'));await partialPage.close();
 console.log(JSON.stringify({result:'passed',workspace,checks:['real-file rendering','multiple rounds and missing scores','offline standalone HTML','all filters and original-ID search','source fidelity','annotation edit/delete','safe verbatim comments','persistent notes and multiple drafts','stable identity across regeneration','changed-source and removed-target contexts','Markdown export original context','JSON backup/restore in a fresh browser and file location','non-destructive conflict restore','wrong-workspace backup rejection','storage-denied fallback','single-agent partial empty states','overview-first navigation','sourced round snapshots and changes','complete experiment settings','paper section design and linked experiments','experiment-specific annotations','four viewports across all routes','zero errors and network requests']},null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
