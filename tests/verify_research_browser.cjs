/* Real generated schema-2 report, using explicitly synthetic agent results. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const {execFileSync}=require('child_process'),fs=require('fs/promises'),path=require('path'),os=require('os'),assert=require('assert/strict');
const {pathToFileURL}=require('url');
(async()=>{
 const repo=path.resolve(__dirname,'..'),temp=await fs.mkdtemp(path.join(os.tmpdir(),'shaokao-engine-browser-')),workspace=path.join(temp,'study');
 execFileSync('python3',['-c',"import sys;sys.path.insert(0,sys.argv[1]);from engine_fixture import create,drive;from shaokao.report import render;drive(s:=create(sys.argv[2]));render(s)",path.join(repo,'tests'),workspace]);
 const url=pathToFileURL(path.join(workspace,'final/review.html')).href;
 const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
 try{
 const context=await browser.newContext({offline:true,viewport:{width:1440,height:1000},acceptDownloads:true});
 const page=await context.newPage(),errors=[],requests=[];
 page.on('pageerror',error=>errors.push(String(error)));
 page.on('request',request=>{if(/^https?:/.test(request.url()))requests.push(request.url())});
 const route=async hash=>{await page.goto(url+'#'+hash);await page.waitForFunction(hash=>document.querySelector('#github-app').dataset.route===hash,hash)};
 await route('overview');
 assert.equal(await page.locator('[data-section]').count(),3);
 const overview=await page.locator('#github-app').innerText();
 for(const text of ['Core research insight','Main novelty','Key contributions','High-level method','Most important experimental validation','Simulated acceptance readiness','does not guarantee acceptance'])assert.ok(overview.includes(text),text);
 assert.equal(await page.locator('.review-record').count(),0);
 assert.equal(await page.locator('.round-summary').count(),0);
 await route('paper');
 assert.equal(await page.locator('.academic-section[id]').count(),13);
 assert.ok(await page.locator('.katex').count()>=2);
 assert.ok(await page.locator('math').count()>=2);
 assert.ok((await page.locator('.prediction-notice').innerText()).includes('not completed measurements'));
 assert.ok((await page.locator('.academic-paper').innerText()).includes('-2–5 percentage points'));
 await page.locator('.paper-toc').filter({hasText:'Related Work'}).click();
 await page.waitForFunction(()=>document.querySelector('#paper-related_work').getBoundingClientRect().top<50);
 await route('process/1');
 assert.equal(await page.locator('.round-link').count(),2);
 await page.getByText('Official review · initial scores',{exact:true}).first().click();
 assert.ok((await page.locator('.record-review').first().innerText()).includes('5: Accept:'));
 assert.ok((await page.locator('.record-review').first().innerText()).includes('internal completeness requirement'));
 await page.getByText('Response to individual reviewer concerns',{exact:true}).click();
 assert.equal(await page.locator('.response-comment:visible').count(),3);
 await page.locator('[data-evidence]:visible').first().click();await page.locator('#source-text').waitFor();
 assert.ok((await page.locator('#source-meta').innerText()).includes('SHA-256:'));
 await page.locator('#evidence-dialog [data-close-dialog]').click();
 await route('process/2');
 const process=await page.locator('.process-record').innerText();
 for(const text of ['Research changes from the previous round','Internal Novelty Stress Test','Independent initial reviews','Author rebuttal','updated evaluations','Area Chair meta-review','Senior assessment'])assert.ok(process.includes(text),text);
 await page.getByText('Final assessment and readiness decision',{exact:true}).click();
 assert.ok((await page.locator('.record-chair').last().innerText()).includes('internal simulation'));
 await page.getByText('Compare paper versions side by side →').click();
 await page.waitForURL('**#compare/2');await page.locator('.version-comparison').waitFor();assert.equal(await page.locator('.version-comparison>article').count(),2);
 const comparison=await page.locator('.version-comparison').innerText();assert.ok(comparison.includes('v1'));assert.ok(comparison.includes('v2'));
 await route('paper');await page.locator('[data-annotate^="paper:"]').click();
 const note='<img src=x onerror="window.injected=true"> A paper-specific question.';
 await page.fill('#note-text',note);await page.locator('#annotation-form [type=submit]').click();
 assert.equal(await page.evaluate(()=>!!window.injected),false);
 assert.equal((await page.evaluate(()=>UI.backup())).notes[0].context.version,'round-02.paper-01');
 await page.reload();assert.equal(await page.locator('[data-note-count]').first().textContent(),'1');
 const screenshotDir=processEnv('SHAOKAO_SCREENSHOTS');
 for(const width of [1440,1024,768,390]){
  await page.setViewportSize({width,height:1000});
  for(const hash of ['overview','paper','process/1','process/2','compare/2']){
   await route(hash);
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${width} ${hash} horizontal overflow`);
   if(screenshotDir&&[1440,390].includes(width)&&['overview','paper','process/2'].includes(hash)){
    await fs.mkdir(screenshotDir,{recursive:true});await page.screenshot({path:path.join(screenshotDir,hash.replace('/','-')+'-'+width+'.png'),fullPage:false});
   }
  }
 }
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 await context.close();
 console.log(JSON.stringify({result:'passed',workspace,checks:['three primary views','concise final overview','complete paper prose','hypothetical prediction ranges','exact venue score labels','threaded rebuttal','full multi-round history','source hash reader','official vs internal chair scope','side-by-side revisions','persistent paper annotations','safe content','four responsive viewports','offline zero requests and browser errors']},null,2));
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
function processEnv(key){return process.env[key]}
