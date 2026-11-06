const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const path=require('path'),fs=require('fs/promises');
const {pathToFileURL}=require('url');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE?{executablePath:process.env.CHROMIUM_EXECUTABLE}:{})});
 const results=[];
 const names=process.argv.slice(2).length?process.argv.slice(2):['signal-desk','editorial-dossier','evidence-table'];
 let prior=[];try{prior=JSON.parse(await fs.readFile(path.resolve(__dirname,'../verification/readability-results.json'),'utf8'))}catch{}
 for(const name of names){
  const context=await browser.newContext({viewport:{width:1440,height:900},offline:true});
  const page=await context.newPage();
  await page.goto(pathToFileURL(path.resolve(__dirname,'..',name+'.html')).href);
  await page.evaluate(()=>document.fonts.ready);
  const check=()=>{
   function rgb(text){const v=text.match(/[\d.]+/g);return v?[+v[0],+v[1],+v[2],v.length>3?+v[3]:1]:[0,0,0,0]}
   function background(el){if(!el)return [255,255,255,1];const bg=rgb(getComputedStyle(el).backgroundColor);if(bg[3]>=1)return bg;const p=background(el.parentElement);return [0,1,2].map(i=>bg[i]*bg[3]+p[i]*(1-bg[3])).concat(1)}
   function lum(c){const s=c.slice(0,3).map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4});return s[0]*.2126+s[1]*.7152+s[2]*.0722}
   const lowContrast=[],smallText=[];let checked=0;
   const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
   while(walker.nextNode()){
    const node=walker.currentNode,el=node.parentElement;
    if(!node.textContent.trim()||el.closest('script,style,dialog,[hidden]')||!el.getClientRects().length)continue;
    const cs=getComputedStyle(el);if(cs.visibility==='hidden')continue;
    const text=node.textContent.trim().slice(0,90), fg=rgb(cs.color),bg=background(el),ratio=(Math.max(lum(fg),lum(bg))+.05)/(Math.min(lum(fg),lum(bg))+.05);
    checked++;
    if(ratio<4.5)lowContrast.push({text,ratio:+ratio.toFixed(2),selector:el.className||el.tagName,fg:cs.color,bg});
    if(parseFloat(cs.fontSize)<12)smallText.push({text,font:cs.fontSize});
   }
   return {checked,lowContrast,smallText,overflow:document.documentElement.scrollWidth>innerWidth};
  };
  const desktop=await page.evaluate(check);
  await page.setViewportSize({width:1024,height:768});
  const narrow=await page.evaluate(check);
  results.push({direction:name,desktop,narrow});
  await context.close();
 }
 await fs.writeFile(path.resolve(__dirname,'../verification/readability-results.json'),JSON.stringify([...prior.filter(item=>!names.includes(item.direction)),...results],null,2)+'\n');
 console.log(JSON.stringify(results,null,2));
 if(results.some(r=>[r.desktop,r.narrow].some(v=>v.overflow||v.lowContrast.length||v.smallText.length)))process.exitCode=1;
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
