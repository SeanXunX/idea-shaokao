/* Schema-2 interface: render the journal's actual research artifacts. */
UI.mount();
(() => {
  'use strict';
  document.body.classList.add('research-mode');
  const e = UI.escape, app = document.getElementById('github-app');
  const p = D.project, research = D.research, rounds = research.rounds;
  const titles = {abstract:'Abstract',introduction:'Introduction',related_work:'Related Work',problem_formulation:'Problem Formulation',insight_hypothesis:'Key Insight and Research Hypothesis',proposed_method:'Proposed Method',technical_design:'Technical Design',theoretical_analysis:'Theoretical Analysis',experimental_design:'Experimental Design',expected_results:'Expected Results and Quantitative Predictions',expected_contributions:'Expected Contributions',limitations:'Limitations and Risks',conclusion:'Conclusion'};
  const allPapers = rounds.flatMap(r => r.iterations.filter(a => a.paper).map(a => ({...a,round:r.number})));
  const selected = allPapers.find(a => a.paper_id === research.selected_paper_id);
  const source = (id,label='Original record ↗') => `<button type="button" class="link-button" data-evidence="${e(id)}">${e(label)}</button>`;
  const missing = message => `<p class="missing">${e(message)}</p>`;
  const chip = value => `<span class="badge">${e(value)}</span>`;
  const notify = id => D.targets[id] ? UI.noteButton(id,'Annotate') : '';
  const storage = () => '<p class="storage-message" data-storage-status></p>';
  const date = stamp => {try{return new Date(stamp).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'})}catch{return stamp}};
  const scalar = value => typeof value === 'object' ? JSON.stringify(value) : String(value ?? 'Not recorded');
  const math = (value,display=false) => {
    try {return '<span class="'+(display?'math-display':'math-inline')+'">'+katex.renderToString(value,{displayMode:display,throwOnError:false,trust:false,maxSize:20,maxExpand:500,strict:'ignore',macros:{}})+'</span>'}
    catch {return '<code>'+e(value)+'</code>'}
  };
  const inline = value => String(value).split(/(\\\([\s\S]*?\\\))/).map(part=>part.startsWith('\\(')&&part.endsWith('\\)')?math(part.slice(2,-2)):e(part).replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/\[([^\]]+)\]\((https:\/\/[^\s)]+)\)/g,'<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')).join('');
  // The document is escaped before formatting. HTML, script, and arbitrary URL
  // protocols from papers/reviews never enter the DOM as active markup.
  function prose(value) {
    const lines = String(value ?? '').split('\n');
    let html='', buffer=[];
    const flush=()=>{if(buffer.length){html += '<p>'+inline(buffer.join(' '))+'</p>';buffer=[]}};
    for(let i=0;i<lines.length;i++) {
      const line=lines[i];
      if(line.trim().startsWith('$$')&&line.trim().endsWith('$$')&&line.trim().length>4) {
        flush();html+=math(line.trim().slice(2,-2),true);
      } else if(/^```/.test(line)||line.trim()==='$$') {
        flush(); const fence=line.trim()==='$$'?'$$':'```', code=[];
        while(++i<lines.length&&!lines[i].startsWith(fence))code.push(lines[i]);
        html+=fence==='$$'?math(code.join('\n'),true):'<pre class="paper-equation"><code>'+e(code.join('\n'))+'</code></pre>';
      } else if(line.includes('|') && i+1<lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[i+1])) {
        flush();const cells=s=>s.trim().replace(/^\||\|$/g,'').split('|').map(c=>c.trim());
        const header=cells(line);i++;const rows=[];
        while(i+1<lines.length&&lines[i+1].includes('|'))rows.push(cells(lines[++i]));
        html+='<div class="table-scroll"><table class="simple-table"><thead><tr>'+header.map(c=>'<th>'+inline(c)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(c=>'<td>'+inline(c)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
      } else if(/^#{1,6}\s/.test(line)) {flush();html+='<h4>'+inline(line.replace(/^#+\s/,''))+'</h4>'}
      else if(!line.trim())flush(); else buffer.push(line);
    }
    flush();return html;
  }
  function table(headers,rows) {
    return '<div class="table-scroll"><table class="simple-table"><thead><tr>'+headers.map(h=>'<th>'+e(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(c=>'<td>'+e(c)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
  }
  function predictions(paper) {
    return '<div class="prediction-notice">Hypothetical predictions · These are estimates to test, not completed measurements.</div>'+table(['Experiment / metric','Estimated baseline','Predicted range','Assumptions & rationale','Failure condition'],paper.predictions.map(row=>[
      row.experiment_id+' · '+row.metric,row.baseline,row.estimate?row.estimate.join('–')+' '+row.unit:row.nonquantitative_reason,
      row.assumptions+' '+row.rationale+(row.unsupported_estimate_warning?' '+row.unsupported_estimate_warning:''),row.failure_condition]));
  }
  function paperBody(paper,idPrefix='paper') {
    return Object.entries(titles).map(([key,label])=>`<section class="academic-section" id="${e(idPrefix+'-'+key)}"><h2>${e(label)}</h2><div class="academic-prose">${prose(paper.sections[key])}</div>${key==='expected_results'?predictions(paper):''}</section>`).join('');
  }
  function heading(title,description='') {return `<div class="page-heading"><div><h1>${e(title)}</h1>${description?'<p class="page-description">'+e(description)+'</p>':''}</div></div>`}
  function outcome() {
    const labels={accepted_simulation:'Simulated acceptance readiness',budget_exhausted:'Budget exhausted · acceptance not established',abandoned:'Idea abandoned after novelty failure',needs_rubric:'Official rubric pending',in_progress:'Research and review in progress'};
    return `<div class="outcome-panel" data-outcome="${e(p.status)}"><h2>Final simulated review outcome</h2><strong>${e(labels[p.status]||p.status)}</strong><p>${e(p.rationale)}</p><p class="quiet">A simulated Accept means the proposal appears competitive under the reconstructed process. It does not guarantee acceptance by the actual conference.</p></div>`;
  }
  function overview() {
    const paper=selected?.paper.result;
    app.innerHTML=heading(p.title,`${research.conference.name} ${research.conference.year} · ${research.conference.track}`)+
      (paper?`<article class="research-overview"><p class="overview-abstract">${e(paper.summary)}</p><div class="summary-pair"><section><h2>Core research insight</h2><p>${e(paper.core_insight)}</p></section><section><h2>Main novelty</h2><p>${e(paper.main_novelty)}</p></section></div><section><h2>Key contributions</h2>${paper.contributions.map(c=>'<p>'+e(c)+'</p>').join('')}</section><section><h2>High-level method</h2><p>${e(paper.high_level_method)}</p></section><section><h2>Most important experimental validation</h2><p>${e(paper.key_validation)}</p></section>${outcome()}<div class="overview-actions"><a class="btn btn-primary" href="#paper">Read final paper</a><a class="btn" href="#process">Explore review process</a>${notify('section:overview')}</div></article>`:missing('No complete paper is available yet. The Review Process shows the current stage and pending work.')+outcome())+storage();
  }
  function paperView(paperId) {
    const a=allPapers.find(x=>x.paper_id===paperId)||selected;
    if(!a){app.innerHTML=heading('Final Paper')+missing('No complete paper-level proposal has been recorded.');return}
    const paper=a.paper.result;
    app.innerHTML=`<header class="paper-title">${chip((a.paper_id===p.version?p.paperStatus:'Research proposal')+' · hypothetical results')}<h1>${e(paper.title)}</h1><p>${e(research.conference.name)} ${research.conference.year} · ${e(research.conference.track)} · ${e(a.paper_id)}</p><div class="record-links">${source(a.paper.source_id,'Frozen paper record ↗')}${notify('paper:'+a.paper_id)}</div></header><div class="reading-layout"><aside class="reading-nav" aria-label="Paper sections"><div class="nav-caption">Paper contents</div>${Object.entries(titles).map(([key,label])=>`<a class="paper-toc" href="#paper/${e(a.paper_id)}/${key}">${e(label)}</a>`).join('')}</aside><article class="academic-paper">${paperBody(paper)}<section class="academic-section"><h2>References and evidence limits</h2>${a.literature.result.papers.map(row=>`<p class="bibliography-entry">[${e(row.id)}] ${e(row.authors)} (${e(row.year)}). <a href="${e(row.url)}" target="_blank" rel="noopener noreferrer">${e(row.title)}</a>. Inspected: ${e(row.access_depth)}; ${e(row.locator)}.</p>`).join('')}</section><details class="experiment-appendix"><summary>Detailed experiment specifications</summary>${paper.experiments.map(x=>`<section><h3>${e(x.id)} · ${e(x.hypothesis)}</h3><dl class="review-fields">${Object.entries(x).filter(([key])=>key!=='id'&&key!=='hypothesis').map(([key,value])=>'<dt>'+e(key)+'</dt><dd>'+prose(value)+'</dd>').join('')}</dl></section>`).join('')}</details>${storage()}</article></div>`;
  }
  function choice(field,value) {
    const row=field.options.find(x=>typeof x.value===typeof value&&x.value===value);
    return row?(String(value)===row.label?row.label:`${value}: ${row.label}`):scalar(value);
  }
  function scoreRow(record,rubric) {
    const data=record.result;
    if(!data.fields)return data.verdict?chip(data.verdict):data.recommendation?chip(data.recommendation):'';
    return ['overall_field','confidence_field'].map(key=>{const field=rubric.fields.find(f=>f.id===rubric[key]);return `<span class="record-score"><strong>${e(field.name)}</strong> ${e(choice(field,data.fields[field.id]))}</span>`}).join('');
  }
  function concernRows(rows) {
    return rows?.length?`<div class="review-concerns">${rows.map(c=>`<section id="concern-${e(c.id)}"><h4>${e(c.id)} ${chip(c.severity)}</h4><p>${e(c.claim)}</p><p><strong>Evidence.</strong> ${e(c.evidence)}</p><p><strong>Resolution criterion.</strong> ${e(c.resolution_criterion)}</p></section>`).join('')}</div>`:'';
  }
  function responseRows(rows) {
    return rows?.length?`<div class="response-thread">${rows.map(row=>`<section class="response-comment"><h4>Response to ${e(row.concern_id)}</h4>${prose(row.response)}<p><strong>Evidence.</strong> ${e(row.evidence)}</p><p><strong>Change.</strong> ${e(row.change)}</p><p><strong>Remaining uncertainty.</strong> ${e(row.remaining_uncertainty)}</p></section>`).join('')}</div>`:'';
  }
  function recordBody(record,rubric) {
    const data=record.result;
    let output='';
    if(data.fields) output+=`<dl class="review-fields">${rubric.fields.filter(f=>Object.hasOwn(data.fields,f.id)).map(f=>`<dt>${e(f.name)}${f.requirement_scope==='internal_completeness'?'<small>Official instruction heading · internal completeness requirement</small>':''}</dt><dd>${prose(f.kind==='choice'?choice(f,data.fields[f.id]):scalar(data.fields[f.id]))}${data.score_justifications?.[f.id]?'<p class="score-justification">'+e(data.score_justifications[f.id])+'</p>':''}</dd>`).join('')}</dl>`;
    const excluded=new Set(['fields','score_justifications','concerns','responses','comparison_table','readiness','concern_status','verdict','recommendation']);
    for(const [key,value] of Object.entries(data)) {
      if(excluded.has(key)||typeof value==='object')continue;
      output+=`<section class="record-section"><h4>${e(key.replaceAll('_',' '))}</h4>${prose(value)}</section>`;
    }
    if(data.comparison_table)output+=table(['Closest paper','Overlapping claim','Mechanism comparison','Precise difference','Evidence location'],data.comparison_table.map(x=>[x.paper_id,x.overlapping_claim,x.mechanism_comparison,x.precise_difference,x.evidence_locator]));
    output+=concernRows(data.concerns)+responseRows(data.responses);
    if(data.readiness) output+=table(['Readiness criterion','Judgment','Evidence'],Object.entries(data.readiness).map(([key,value])=>[key.replaceAll('_',' '),value.met?'Met':'Not established',value.evidence]));
    if(data.concern_status)output+=table(['Concern','Disposition','Reason','Evidence'],Object.entries(data.concern_status).map(([key,value])=>[key,value.status,value.reason,value.evidence]));
    return output;
  }
  function card(label,role,record,rubric,{open=false,kind='review'}={}) {
    if(!record)return `<div class="pending-record"><h3>${e(label)}</h3>${missing('Pending · no returned report or favorable score is implied.')}</div>`;
    return `<details class="review-record record-${e(kind)}" ${open?'open':''}><summary><div class="record-heading"><span class="record-role">${e(role)}</span><h3>${e(label)}</h3></div><div class="record-score-line">${scoreRow(record,rubric)}</div><div class="record-metadata"><span>${e(record.round_id)}</span><span>${e(record.paper_id||'Research development')}</span><time datetime="${e(record.at)}">${e(date(record.at))}</time><span>Recorded</span></div></summary><div class="review-record-body">${recordBody(record,rubric)}<div class="record-links">${source(record.source_id)}</div></div></details>`;
  }
  function rubricView(rubric) {
    if(!rubric)return missing('Official rubric unavailable. Formal reviews are blocked.');
    return `<details class="rubric-details"><summary>Official review rubric · ${e(rubric.version)} ${rubric.historical?'· Historical fallback':''}</summary><p>${e(rubric.form_basis.replaceAll('_',' '))} · ${e(rubric.conference.name)} ${rubric.conference.year} · ${e(rubric.conference.track)}</p>${rubric.fields.filter(f=>f.options.length).map(f=>`<h4>${e(f.name)}</h4>${table(['Exact value','Exact label / description'],f.options.map(x=>[x.value,x.label]))}`).join('')}<h4>Uncertainty and provenance limits</h4>${rubric.uncertainties.map(x=>'<p>'+e(x)+'</p>').join('')}<p>${e(rubric.differences_previous_year)}</p><h4>Discussion procedure</h4>${table(['Role','Exchange','Character limit'],rubric.procedures.exchanges.map(x=>[x.role,x.label,x.max_chars??'Not specified']))}<p><strong>AC.</strong> ${e(rubric.procedures.ac.summary)}</p><p><strong>SAC.</strong> ${e(rubric.procedures.sac.summary)}</p></details>`;
  }
  function processView(number) {
    const r=rounds.find(r=>r.number===Number(number))||rounds.at(-1);
    if(!r){app.innerHTML=heading('Review Process')+rubricView(research.rubric)+missing('No review round has started. Fetch and verify the official conference rubric first.');return}
    const a=r.iterations.at(-1), rubric=r.rubric;
    const submitted=r.submission;
    app.innerHTML=heading('Review Process','Each round preserves its complete submission, adversarial validation, independent judgments, and research revisions.')+`<div class="reading-layout process-layout"><aside class="reading-nav" aria-label="Research rounds"><div class="nav-caption">Submissions</div>${rounds.map(x=>`<a class="round-link" href="#process/${x.number}" ${x.number===r.number?'aria-current="page"':''}><strong>Round ${x.number}</strong><small>${e(x.iterations.at(-1)?.paper_id||'In preparation')}</small><small>${e(x.outcome||x.phase.replaceAll('_',' '))}</small></a>`).join('')}</aside><article class="process-record"><header class="round-heading"><div><h2>Round ${r.number} — ${r.number===1?'Initial':'Revised'} Submission</h2><p>${e(a?.paper?.result.title||'Paper in preparation')}</p><p class="quiet">${e(a?.paper_id||'Unsubmitted')} · ${e(r.phase.replaceAll('_',' '))}</p></div>${notify('round:'+r.number)}</header>${r.revision?card('Research changes from the previous round','Author',r.revision,rubric,{open:true,kind:'author'})+`<a class="text-link compare-link" href="#compare/${r.number}">Compare paper versions side by side →</a>`:''}${rubricView(rubric)}<section class="process-stage"><h2>Paper submission</h2>${submitted?`<details class="review-record"><summary><h3>${e(submitted.paper.title)}</h3><div class="record-metadata">${e(submitted.paper_id)} · ${e(date(submitted.submitted_at))} · Frozen ${e(submitted.paper_sha256.slice(0,12))}</div></summary><div class="review-record-body academic-paper">${paperBody(submitted.paper,'submission')}<a href="#paper/${e(submitted.paper_id)}">Open complete paper →</a></div></details>`:missing('Formal submission is pending. Every novelty adversary must return PASS before conference-style review.')}</section><section class="process-stage"><h2>Internal Novelty Stress Test</h2>${r.iterations.length?r.iterations.map(x=>`<details class="novelty-iteration" ${x===a?'open':''}><summary>Attempt ${x.number} · ${e(x.paper_id||'Paper pending')} · ${e(x.gate||'In progress')}</summary>${x.paper?`<a class="text-link" href="#paper/${e(x.paper_id)}">Read this complete paper version →</a>`:''}${['prior_art','conceptual','significance'].map((role,i)=>card(['Prior-Art Investigation','Conceptual Novelty Critique','Top-Conference Significance Challenge'][i],['Adversary A','Adversary B','Adversary C'][i],x.stress[role],rubric,{kind:'novelty'})).join('')}${card('Author response and recomposition','Author',x.response,rubric,{kind:'author'})}</details>`).join(''):missing('Literature investigation and idea composition are pending.')}</section><section class="process-stage"><h2>Independent initial reviews</h2><p class="section-caption">Initial scores are sealed from peers until all assigned reviews return. Original judgments remain preserved.</p>${Array.from({length:research.config.reviewers},(_,i)=>{const role='R'+(i+1);return card('Official review · initial scores',role,r.reviews[role],rubric)}).join('')}</section><section class="process-stage"><h2>Author rebuttal</h2>${card('Response to individual reviewer concerns','Author',r.rebuttal,rubric,{kind:'author'})}</section><section class="process-stage"><h2>Reviewer discussion and updated evaluations</h2>${Object.keys(r.reviews).map(role=>card('Post-rebuttal reassessment · updated scores',role,r.discussion[role],rubric)).join('')||missing('No reviewer follow-up has returned.')}${r.exchanges.map(x=>`<h3>${e(x.procedure.label)}</h3>${Object.entries(x.responses).map(([role,record])=>card(x.procedure.label,role,record,rubric,{kind:role==='author'?'author':'review'})).join('')}`).join('')}${Object.entries(r.final_reviews).map(([role,record])=>record.task_id!==r.discussion[role]?.task_id?card('Final justification · final scores',role,record,rubric):'').join('')}</section><section class="process-stage"><h2>Area Chair meta-review</h2>${card('Meta-review and disagreement analysis','AC · '+rubric.procedures.ac.scope.replaceAll('_',' '),r.ac,rubric,{kind:'chair'})}</section><section class="process-stage"><h2>Senior assessment</h2>${card('Final assessment and readiness decision','SAC · '+rubric.procedures.sac.scope.replaceAll('_',' '),r.sac,rubric,{kind:'chair'})}${r.chair_disagreement?`<p class="disagreement">Chair disagreement preserved: AC ${e(r.chair_disagreement.ac)}; SAC ${e(r.chair_disagreement.sac)}. ${e(r.chair_disagreement.rationale)}</p>`:''}</section><details class="rubric-details"><summary>Literature evidence and search coverage</summary>${r.literature?table(['Paper','Insight','Assumptions','Limitations','Contribution difference'],r.literature.result.papers.map(x=>[x.title,x.insight,x.assumptions,x.limitations,x.contribution_difference]))+source(r.literature.source_id,'Full evidence map and search log ↗'):missing('No literature investigation returned.')}</details>${storage()}</article></div>`;
  }
  function compareView(number) {
    const current=rounds.find(r=>r.number===Number(number)), previous=rounds.find(r=>r.number===Number(number)-1);
    const left=previous?.iterations.at(-1),right=current?.iterations.at(-1);
    if(!left?.paper||!right?.paper){app.innerHTML=heading('Paper version comparison')+missing('Two complete successive paper versions are required.');return}
    app.innerHTML=heading('Paper version comparison')+`<a class="back-link" href="#process/${current.number}">← Back to review round</a><p class="comparison-summary">${e(current.revision?.result.summary||'No change summary recorded.')}</p><div class="version-comparison">${[left,right].map(a=>`<article><header><span class="mono">${e(a.paper_id)}</span><h2>${e(a.paper.result.title)}</h2></header>${paperBody(a.paper.result,a.paper_id)}</article>`).join('')}</div>`;
  }
  document.getElementById('project-slug').textContent=p.slug;
  document.getElementById('header-tools').innerHTML=UI.notesButton()+UI.exportButton();
  document.getElementById('project-context').innerHTML=`<div class="project-label">${e(research.conference.name)} ${research.conference.year} <span class="quiet">${e(research.conference.track)}</span></div><div class="project-meta">${p.testCase?'<strong>SOFTWARE TEST FIXTURE · synthetic agent judgments</strong>':'Simulated peer review · research proposal'}</div>`;
  document.getElementById('section-nav').innerHTML=[['overview','Overview'],['paper','Final Paper'],['process','Review Process']].map(([key,label])=>`<a class="section-link" data-section="${key}" href="#${key}">${label}</a>`).join('');
  function route() {
    const parts=location.hash.slice(1).split('/'),raw=parts[0]||'overview';
    const section=raw==='compare'?'process':['overview','paper','process'].includes(raw)?raw:'overview';
    window.scrollTo(0,0);
    if(raw==='compare')compareView(parts[1]);else if(section==='paper')paperView(parts[1]);else if(section==='process')processView(parts[1]);else overview();
    document.querySelectorAll('[data-section]').forEach(a=>a.setAttribute('aria-current',a.dataset.section===section?'page':'false'));
    document.title=`${section==='paper'?'Final Paper':section==='process'?'Review Process':'Overview'} · ${p.title}`;
    app.dataset.route=parts.join('/')||'overview';UI.status();
    if(section==='paper'&&parts[2])requestAnimationFrame(()=>document.getElementById('paper-'+parts[2])?.scrollIntoView({block:'start'}));
  }
  document.querySelector('.skip-link').addEventListener('click',event=>{event.preventDefault();document.getElementById('main-content').focus()});
  window.addEventListener('hashchange',route);route();
})();
