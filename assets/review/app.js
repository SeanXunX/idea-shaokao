UI.mount();
(() => {
  const e = UI.escape, app = document.getElementById('github-app'), p = D.project;
  const paths = {overview:'Overview', reviews:'Idea & review', plan:'Final plan', issues:'Issues', sources:'Sources'};
  const modes = {independent:'Independent model-agent review', external_review:'External review', single_agent:'Structured self-review', unselected:'Review mode not selected'};
  const convergence = {converged:'Converged', not_converged:'Not converged', not_assessed:'Convergence not assessed'};
  const plan = D.plan, snapshots = D.rounds;
  const closed = i => ['Resolved','Rejected with justification'].includes(i.status);
  const bucket = i => closed(i) ? 'resolved' : 'open';
  const counts = {open:D.issues.filter(i => !closed(i)).length, resolved:D.issues.filter(closed).length, all:D.issues.length};
  const rounds = [...new Set([...snapshots.map(r => r.round), ...D.issues.map(i => i.round), ...D.issues.flatMap(i => i.discussion.map(d => d.round)), ...D.reviewers.map(r => r.round), ...D.timeline.map(t => t.round)].filter(n => n > 0))].sort((a,b) => a-b);
  let state = 'open', severity = 'all', query = '', round = 'all';
  const filterKey = 'idea-shaokao:review:filters:' + p.workspaceId;
  try {
    const saved = JSON.parse(sessionStorage.getItem(filterKey) || 'null');
    if (saved) {
      if (['open','resolved','all'].includes(saved.state)) state = saved.state;
      if (['all','Critical','Major','Moderate','Minor'].includes(saved.severity)) severity = saved.severity;
      if (typeof saved.query === 'string') query = saved.query;
      if (saved.round === 'all' || rounds.includes(Number(saved.round))) round = saved.round;
    }
  } catch {}
  const saveFilters = () => {try {sessionStorage.setItem(filterKey, JSON.stringify({state,severity,query,round}))} catch {}};
  const sourceLink = (id, label) => `<button type="button" class="link-button" data-evidence="${e(id)}">${e(label || D.sources[id].path)}</button>`;
  const refs = ids => `<div class="record-links">${ids.map(id => sourceLink(id, D.sources[id].title)).join('<span aria-hidden="true">·</span>')}</div>`;
  const feedback = (id, label='Add feedback') => UI.noteButton(id, label);
  const storage = () => '<p class="storage-message" data-storage-status></p>';
  const badge = i => `<span class="severity-label severity-${i.severity.toLowerCase()}">${e(i.severity)}</span>`;
  const roundLabel = n => n ? 'Round ' + String(n).padStart(2,'0') : 'Before review';
  const missing = text => `<p class="missing">${e(text)}</p>`;
  const statusLabel = p.recommendation === 'Undetermined' ? 'No recommendation recorded' : (p.assessor === 'Unassigned' ? 'Assessment' : p.assessor) + ' recommends ' + p.recommendation;
  const decision = () => `<section class="decision-strip" aria-label="Current assessment"><div><span class="badge recommendation-${p.recommendation.toLowerCase()}">${e(statusLabel)}</span><span class="quiet">${e(p.stage)} stage</span></div><p>${e(p.rationale)}</p>${sourceLink(p.sources[0], 'Assessment source ↗')}</section>`;
  const heading = (title, description, action='') => `<div class="page-heading"><div><h1>${e(title)}</h1><p class="page-description">${e(description)}</p></div>${action}</div>`;
  const titleRow = (title, extra='') => `<div class="section-heading"><h2>${e(title)}</h2>${extra}</div>`;
  const score = value => value ? sourceLink(value.source, value.score) : '<span class="missing-inline">Not recorded</span>';
  const roundSnapshot = n => snapshots.find(r => r.round === n);
  const roundIssues = n => D.issues.filter(i => i.round === n || i.discussion.some(d => d.round === n));
  const block = (record, empty) => record ? `<p class="record-text">${e(record.text)}</p>${refs(record.sources)}` : missing(empty);
  const targetFeedback = n => D.targets['round:'+n] ? feedback('round:'+n,'Annotate round') : feedback('section:reviews','Review feedback');

  document.getElementById('project-slug').textContent = p.slug;
  document.getElementById('header-tools').innerHTML = UI.notesButton() + UI.exportButton();
  document.getElementById('project-context').innerHTML = `<div class="project-label">Research workspace${p.testCase ? '<span class="badge">Test case</span>' : ''}</div><div class="project-meta"><span>${e(p.stage)} stage</span><span class="mono">${e(p.version)}</span><span>Round ${p.round} / ${p.maxRounds}</span><span>${e(convergence[p.convergence] || p.convergence)}</span></div>`;
  document.getElementById('section-nav').innerHTML = Object.entries(paths).map(([id,label]) => `<a class="section-link ${id === 'issues' ? 'secondary-start' : ''}" href="#${id}" data-section="${id}">${label}${id === 'issues' ? `<span class="count">${counts.open}</span>` : ''}</a>`).join('');

  function roundSummary(n) {
    const r = roundSnapshot(n), reviewers = D.reviewers.filter(x => x.round === n);
    const outcome = r?.outcome?.text || D.timeline.filter(t => t.round === n).at(-1)?.summary || 'No outcome summary recorded.';
    return `<a class="round-summary" href="#reviews/${n}"><span class="round-number">${String(n).padStart(2,'0')}</span><div><div class="round-summary-heading"><strong>${roundLabel(n)}</strong><span class="mono quiet">${e(r?.version || 'Version not recorded')}</span></div><p>${e(r?.idea?.text || 'Idea snapshot not recorded for this round.')}</p><div class="round-outcome">${e(outcome)}</div></div><span class="round-summary-end">${reviewers.length ? reviewers.map(x => `${e(x.id)} ${e(x.final?.score || x.initial?.score || '—')}`).join('<br>') : 'Open round'}<span aria-hidden="true">→</span></span></a>`;
  }

  function overview() {
    const method = plan.idea.find(x => ['method','mechanism','insight'].includes(x.id));
    app.innerHTML = `${heading(p.title, 'The current idea, the review that shaped it, and the plan to carry it forward.', feedback('section:overview'))}${decision()}<div class="overview-layout"><div class="overview-main"><section class="overview-section">${titleRow('Current idea', '<a class="text-link" href="#plan/idea">View method design →</a>')}<p class="idea-summary">${e(p.description)}</p>${method ? `<div class="method-summary"><h3>${e(method.title)}</h3><p>${e(method.text)}</p>${refs(method.sources)}</div>` : ''}${D.claims.length ? `<div class="claim-list">${D.claims.map(c => `<div class="claim-row"><span class="record-id">${e(c.id)}</span><div><h3>${e(c.title)}</h3><p>${e(c.text)}</p><div class="claim-meta"><span class="evidence-state">${e(c.status)}</span>${refs(c.sources)}${feedback('claim:'+c.id,'Annotate')}</div></div></div>`).join('')}</div>` : missing('No claim index recorded. The original report retains the stated scope.')}</section><section class="overview-section">${titleRow('Idea & review progression', '<a class="text-link" href="#reviews">Read full process →</a>')}${rounds.length ? `<div class="round-summary-list">${rounds.map(roundSummary).join('')}</div>` : missing('No review rounds recorded yet.')}<p class="section-caption">Each round keeps its own idea, author response, review record, and outcome.</p></section></div><aside class="overview-aside"><section class="next-action"><h2>Next action</h2><p>${e(p.nextAction)}</p><a class="btn btn-primary" href="#plan">Open final plan <span aria-hidden="true">→</span></a></section><section class="record-context"><h2>Research record</h2><dl><dt>Review stage</dt><dd>${e(p.stage)}</dd><dt>Proposal</dt><dd class="mono">${e(p.version)}</dd><dt>Review mode</dt><dd>${e(modes[p.mode] || p.mode)}</dd><dt>Progress</dt><dd>${p.lastCompletedRound != null ? p.lastCompletedRound+' completed · ' : ''}${p.round} / ${p.maxRounds} rounds</dd><dt>Convergence</dt><dd>${e(convergence[p.convergence] || p.convergence)}</dd><dt>Run status</dt><dd>${e(p.status.replaceAll('_',' '))}</dd></dl>${sourceLink('report','Read full final report ↗')}</section><section class="record-context"><h2>Final plan</h2><a href="#plan/idea">01 <span>Idea & method</span></a><a href="#plan/experiments">02 <span>Experiment design</span></a><a href="#plan/story">03 <span>Research story</span></a><a href="#plan/paper">04 <span>Paper outline</span></a><a href="#plan/roadmap">05 <span>Implementation roadmap</span></a></section></aside></div>${storage()}`;
  }

  function reviewTable(items) {
    if (!items.length) return missing('No independent reviewer score records supplied for this round.');
    const rubrics = new Map();
    items.forEach(r => {const key=JSON.stringify([r.stage,r.rubric]);if(!rubrics.has(key))rubrics.set(key,{stage:r.stage,rubric:r.rubric,reviewers:[]});rubrics.get(key).reviewers.push(r.id)});
    return `<div class="table-scroll"><table class="simple-table review-table"><thead><tr><th>Reviewer / focus</th><th>Initial</th><th>After rebuttal</th><th>Confidence</th></tr></thead><tbody>${items.map(r => `<tr><td><strong>${e(r.id)}</strong><span class="table-detail">${e(r.focus)}</span></td><td class="score-cell">${score(r.initial)}</td><td class="score-cell">${score(r.final)}</td><td class="confidence-cell">${e(r.confidence)}</td></tr>`).join('')}</tbody></table></div><details class="rubric-details"><summary>Stage & scoring rubric</summary>${[...rubrics.values()].map(r=>`<p><strong>${e(r.reviewers.join(', '))}</strong><span>${e(r.stage)} · ${e(r.rubric)}</span></p>`).join('')}</details>`;
  }

  function reviews(selected) {
    const n = rounds.includes(Number(selected)) ? Number(selected) : rounds.at(-1);
    if (!n) {
      app.innerHTML = `${heading('Idea & review', modes[p.mode] || p.mode, feedback('section:reviews'))}<div class="empty-panel"><h2>No review rounds recorded</h2><p>The research overview and final plan contain the work available so far.</p><a class="btn" href="#overview">Read overview</a></div>${D.timeline.length ? phaseTimeline(D.timeline) : ''}${storage()}`;
      return;
    }
    const r = roundSnapshot(n), reviewers = D.reviewers.filter(x => x.round === n), entries = D.timeline.filter(t => t.round === n), concerns = roundIssues(n);
    const position = rounds.indexOf(n);
    app.innerHTML = `${heading('Idea & review', 'Follow each idea through review, discussion, author response, and revision.', feedback('section:reviews'))}<div class="reading-layout"><aside class="reading-nav" aria-label="Review rounds"><div class="nav-caption">Review rounds</div>${rounds.map(num => {const snap=roundSnapshot(num);return `<a class="round-link" href="#reviews/${num}" ${num===n?'aria-current="page"':''}><span>${roundLabel(num)}</span><small>${e(snap?.version || 'Version not recorded')}</small></a>`}).join('')}<p class="nav-help">${e(modes[p.mode] || p.mode)}<br>${e(convergence[p.convergence] || p.convergence)}</p></aside><article class="reading-content"><header class="round-heading"><div><h2>${roundLabel(n)}</h2><div class="inline-meta"><span class="mono">${e(r?.version || 'Version not recorded')}</span><span>${e(r?.status || 'Status not recorded')}</span></div></div>${targetFeedback(n)}</header><div class="round-snapshot"><section><h3>Idea entering this round</h3>${block(r?.idea, 'No idea snapshot indexed for this round. Open the submitted sources in the review process below.')}</section><section><h3>What changed</h3>${block(r?.changes, 'No change record indexed for this round. A new review round alone does not imply a revised idea.')}</section></div><section class="reading-section">${titleRow('Reviewer assessments')}${reviewTable(reviewers)}<p class="section-caption">Scores keep their original scale and rubric. Missing assessments remain visible.</p></section><section class="reading-section">${titleRow('Review process')}${entries.length ? phaseTimeline(entries) : missing('No timeline entries indexed for this round. Read the original reviews above.')}</section><section class="reading-section">${titleRow('Concerns & responses', `<span class="quiet">${concerns.length} records</span>`)}${concerns.length ? `<div class="concern-list">${concerns.map(i => {const entries=i.discussion.filter(d => d.round===n);return `<div class="concern-item"><div><button class="issue-title" type="button" data-issue="${e(i.id)}">${e(i.title)}</button>${badge(i)}</div><p class="issue-subline">${e(i.id)} · Current disposition: ${e(i.status)}</p>${entries.length ? `<p>${e(entries.at(-1).text)}</p>` : missing('No discussion entry recorded in this round.')}<button class="link-button" type="button" data-issue="${e(i.id)}">Read full discussion →</button></div>`}).join('')}</div>` : missing('No concerns indexed for this round. This is not evidence of validity.')}</section><section class="round-conclusion"><h3>Round outcome</h3>${block(r?.outcome, 'No round outcome summary recorded. Inspect the chair or author assessment in the original sources.')}</section><nav class="reading-pagination" aria-label="Adjacent rounds">${position>0?`<a href="#reviews/${rounds[position-1]}">← ${roundLabel(rounds[position-1])}</a>`:'<span></span>'}${position<rounds.length-1?`<a href="#reviews/${rounds[position+1]}">${roundLabel(rounds[position+1])} →</a>`:'<a href="#plan">Continue to final plan →</a>'}</nav>${storage()}</article></div>`;
  }

  function phaseTimeline(entries) {
    return `<ol class="phase-timeline">${entries.map((t,index) => `<li><span class="phase-number" aria-hidden="true">${String(index+1).padStart(2,'0')}</span><div class="phase-content"><div class="phase-heading"><h3>${e(t.label)}</h3><span class="quiet">${e(t.role)}</span></div><p>${e(t.summary)}</p>${sourceLink(t.source,'Read original record ↗')}</div></li>`).join('')}</ol>`;
  }

  const planSections = {idea:'Idea & method', experiments:'Experiment design', story:'Research story', paper:'Paper outline', roadmap:'Implementation roadmap'};
  function planBlocks(collection) {
    return plan[collection].map(x => `<section class="plan-block"><div class="block-heading"><h3>${e(x.title)}</h3>${feedback('plan:'+collection+':'+x.id,'Annotate')}</div><p class="record-text">${e(x.text)}</p>${refs(x.sources)}</section>`).join('');
  }
  function experiments() {
    const fields = {hypothesis:'Hypothesis', setup:'Setup & configuration', data:'Data / workloads', baselines:'Baselines', metrics:'Metrics', controls:'Controls & ablations', success:'Success criterion', failure:'Failure / stop criterion', resources:'Resources & execution', result:'Observed evidence'};
    return D.experiments.length ? D.experiments.map(x => `<article class="experiment-block" id="experiment-${e(x.id)}"><header><div class="experiment-id mono">${e(x.id)}</div><div><h3>${e(x.title)}</h3><p>${e(x.kind)}</p></div><span class="badge">${e(x.status)}</span></header><p class="experiment-summary">${e(x.summary)}</p><dl class="experiment-fields">${Object.entries(fields).map(([key,label]) => `<div><dt>${label}</dt><dd ${x[key] ? '' : 'class="missing-inline"'}>${e(x[key] || 'Not recorded')}</dd></div>`).join('')}</dl><div class="block-footer">${refs(x.sources)}${feedback('experiment:'+x.id,'Annotate experiment')}</div></article>`).join('') : missing('No experiment entries supplied. No execution or result is implied.');
  }
  function paper() {
    return plan.paper.length ? `<div class="paper-outline">${plan.paper.map((x,index) => `<section class="paper-section"><div class="paper-section-number mono">${String(index+1).padStart(2,'0')}</div><div><div class="block-heading"><h3>${e(x.title)}</h3>${feedback('plan:paper:'+x.id,'Annotate')}</div><dl class="paper-fields"><dt>Purpose</dt><dd>${e(x.goal)}</dd><dt>Section design</dt><dd>${e(x.design)}</dd><dt>Evidence / figures</dt><dd>${e(x.evidence)}</dd></dl>${x.experiments.length ? `<div class="experiment-references">${x.experiments.map(id => `<a class="badge" href="#plan/experiments/${e(id)}">${e(id)} ↗</a>`).join('')}</div>` : ''}${refs(x.sources)}</div></section>`).join('')}</div>` : missing('A section-by-section paper design has not been recorded for this study. The original final report remains available.');
  }
  function roadmap() {
    return plan.roadmap.length ? `<div class="roadmap-list">${plan.roadmap.map((x,index) => `<section class="roadmap-step"><span class="mono quiet">${String(index+1).padStart(2,'0')}</span><div><div class="block-heading"><h3>${e(x.title)}</h3>${feedback('plan:roadmap:'+x.id,'Annotate')}</div><p>${e(x.task)}</p><dl class="roadmap-fields"><dt>Dependencies</dt><dd>${e(x.dependencies)}</dd><dt>Deliverable</dt><dd>${e(x.artifact)}</dd><dt>Effort / resources</dt><dd>${e(x.estimate)}</dd></dl>${refs(x.sources)}</div></section>`).join('')}</div>` : missing('No implementation roadmap indexed. The next action below is taken from the research checkpoint.');
  }
  function renderPlan(part, experimentId) {
    app.innerHTML = `${heading('Final research plan', 'The selected idea, experiment specifications, research narrative, and paper design.', feedback('section:plan'))}<div class="plan-context"><span class="mono">${e(p.version)}</span><span>${e(p.stage)} stage</span><span class="badge recommendation-${p.recommendation.toLowerCase()}">${e(p.recommendation)}</span>${sourceLink('report','Full final report ↗')}</div><div class="reading-layout"><aside class="reading-nav" aria-label="Plan contents"><div class="nav-caption">On this page</div>${Object.entries(planSections).map(([id,label],index) => `<a class="plan-link" href="#plan/${id}" data-plan-link="${id}"><span class="mono">0${index+1}</span>${label}</a>`).join('')}<p class="nav-help">${e(p.version)} · ${e(p.stage)}<br>Sources accompany each design decision.</p></aside><article class="reading-content plan-document"><section class="plan-section" id="plan-idea">${titleRow('Idea & method', '<span class="section-index">01</span>')}${plan.idea.length ? planBlocks('idea') : `<p>${e(p.description)}</p>${missing('Detailed method design has not been indexed. Read the original final report.')}`}${D.claims.length ? `<div class="plan-claims"><h3>Claims & evidence status</h3>${D.claims.map(c => `<div><code>${e(c.id)}</code><p><strong>${e(c.title)}</strong> — ${e(c.text)}<span class="table-detail">${e(c.status)}</span></p>${feedback('claim:'+c.id,'Annotate')}</div>`).join('')}</div>` : ''}</section><section class="plan-section" id="plan-experiments">${titleRow('Experiment design', '<span class="section-index">02</span>')}<p class="section-intro">Setups, comparisons, and decision criteria. Each record distinguishes planned work from observed evidence.</p>${experiments()}</section><section class="plan-section" id="plan-story">${titleRow('Research story', '<span class="section-index">03</span>')}${plan.story.length ? planBlocks('story') : missing('The research narrative has not been indexed: problem, gap, insight, evidence chain, and limitations need a sourced account.')}</section><section class="plan-section" id="plan-paper">${titleRow('Paper outline', '<span class="section-index">04</span>')}<p class="section-intro">What each section should establish, how to develop it, and which evidence it needs.</p>${paper()}</section><section class="plan-section" id="plan-roadmap">${titleRow('Implementation roadmap', '<span class="section-index">05</span>')}${roadmap()}<div class="next-step"><h3>Exact next action</h3><p>${e(p.nextAction)}</p></div></section><div class="document-end">${UI.sourceButton('report','Read original final report')}${feedback('section:plan')}</div>${storage()}</article></div>`;
    const active = Object.hasOwn(planSections,part) ? part : 'idea';
    updatePlanNav(active);
    if (Object.hasOwn(planSections,part)) {
      const target = experimentId ? document.getElementById('experiment-'+experimentId) : null;
      const section = target || document.getElementById('plan-'+part);
      requestAnimationFrame(() => {
        window.scrollTo({top:Math.max(0,section.getBoundingClientRect().top+window.scrollY-24),behavior:'instant'});
        if (target) {target.classList.add('target-highlight');target.setAttribute('tabindex','-1');target.focus({preventScroll:true})}
      });
    }
    if ('IntersectionObserver' in window) {
      planObserver = new IntersectionObserver(entries => {
        const first = entries.filter(x => x.isIntersecting).sort((a,b) => a.boundingClientRect.top-b.boundingClientRect.top)[0];
        if (first) updatePlanNav(first.target.id.slice(5));
      }, {rootMargin:'-5% 0px -65% 0px'});
      document.querySelectorAll('.plan-section').forEach(section => planObserver.observe(section));
    }
  }
  function updatePlanNav(id) {document.querySelectorAll('[data-plan-link]').forEach(a => a.setAttribute('aria-current',a.dataset.planLink===id?'location':'false'))}
  let planObserver;

  function roundSelect() {
    return rounds.length > 1 ? `<select class="severity-select" id="round-filter" aria-label="Filter by round"><option value="all">All rounds</option>${rounds.map(n => `<option value="${n}" ${round===String(n)?'selected':''}>${roundLabel(n)}</option>`).join('')}</select>` : '';
  }
  function renderList() {
    app.innerHTML = `${heading('Research issues', 'Inspect specific concerns and their complete discussion threads.', feedback('section:decision'))}${decision()}<form class="search-form" id="issue-search"><label class="sr-only" for="issue-query">Search issues</label><input type="search" class="search-input" id="issue-query" placeholder="Search concerns, original IDs, or responses…" value="${e(query)}"><button class="btn" type="submit">Search</button></form><div class="list-box"><div class="list-toolbar"><div class="state-filters" aria-label="Issue state">${['open','resolved','all'].map(s => `<button type="button" class="state-filter" data-state="${s}" aria-pressed="${state===s}">${s==='open'?'Open':s==='resolved'?'Resolved':'All'} <span class="count">${counts[s]}</span></button>`).join('')}</div><div class="filter-controls">${roundSelect()}<select class="severity-select" id="severity-filter" aria-label="Filter by severity">${['all','Critical','Major','Moderate','Minor'].map(s => `<option value="${s}" ${severity===s?'selected':''}>${s==='all'?'All severities':s}</option>`).join('')}</select></div></div><div id="issue-rows" aria-live="polite"></div></div><p class="section-caption" id="list-summary"></p>${storage()}`;
    renderRows();
  }
  function renderRows() {
    saveFilters();
    const needle = query.toLowerCase().trim();
    const items = D.issues.filter(i => (state==='all'||bucket(i)===state) && (severity==='all'||i.severity===severity) && (round==='all'||i.round===Number(round)||i.discussion.some(d=>d.round===Number(round))) && (!needle||[i.title,i.id,...i.aliases,...i.discussion.map(d=>d.text),i.severity,i.status].join(' ').toLowerCase().includes(needle)));
    document.getElementById('issue-rows').innerHTML = items.length ? items.map(i => `<article class="issue-row"><span class="issue-status ${bucket(i)}" aria-hidden="true">${closed(i)?'✓':'○'}</span><div><div class="issue-row-title"><button type="button" class="issue-title" data-issue="${e(i.id)}">${e(i.title)}</button>${badge(i)}</div><div class="issue-subline">${e(i.id)} · ${roundLabel(i.round)} · ${e(i.status)}</div></div><span class="row-chevron" aria-hidden="true">→</span></article>`).join('') : `<div class="empty-panel"><h2>${D.issues.length?'No matching issues':'No concerns recorded'}</h2><p>${D.issues.length?'Try another search or clear the filters.':'This report has no indexed issues. This alone does not establish validity or readiness.'}</p>${D.issues.length?'<button type="button" class="btn" data-clear-filters>Clear filters</button>':'<a class="btn" href="#overview">Read research overview</a>'}</div>`;
    document.getElementById('list-summary').textContent = `${items.length} of ${D.issues.length} issue records shown. Original IDs and sources are retained.`;
  }
  function renderIssue(id) {
    const i = D.issues.find(i => i.id === id);
    if (!i) {location.hash='issues';return}
    app.innerHTML = `<a class="back-link" href="#issues">← All issues</a><div class="detail-heading"><h1>${e(i.title)}</h1><div class="inline-meta"><span class="badge">${e(i.status)}</span>${badge(i)}<span class="mono">${e(i.id)}</span><span>${roundLabel(i.round)}</span></div></div><div class="detail-layout"><div class="thread">${i.discussion.length ? i.discussion.map(d => `<section class="comment"><header class="comment-header"><span><strong>${e(d.author)}</strong><span> · ${e(d.phase)} · ${roundLabel(d.round)}</span></span>${sourceLink(d.source,'View source ↗')}</header><div class="comment-body"><p>${e(d.text)}</p></div></section>`).join('') : missing('No discussion has been recorded for this concern.')}<div class="thread-action">${feedback('issue:'+i.id)}<span class="quiet">Human feedback is separate from the research record.</span></div>${storage()}</div><aside class="detail-sidebar"><section><h2>Original issue IDs</h2>${i.aliases.map(id=>`<code>${e(id)}</code>`).join('')}</section><section><h2>Closure criterion</h2><p>${e(i.criterion)}</p></section><section><h2>Evidence</h2><div class="source-links">${i.sources.map(id=>sourceLink(id)).join('')}</div></section><section><a href="#reviews/${i.round}">Open ${roundLabel(i.round)} →</a></section></aside></div>`;
  }
  function sources() {
    const values = Object.values(D.sources);
    app.innerHTML = `${heading('Original sources', `${values.length} bundled documents. Exact source text and SHA-256 hashes remain available offline.`)}<div class="source-list">${values.map(s=>`<div class="source-row"><div>${sourceLink(s.id,s.path)}<p>${e(s.id)}</p></div><span class="mono source-hash">${e(s.sha256.slice(0,12))}</span></div>`).join('')}</div>${storage()}`;
  }

  function route() {
    planObserver?.disconnect();
    const parts = location.hash.slice(1).split('/'), raw = parts[0] || 'overview';
    const section = raw === 'issue' ? 'issues' : Object.hasOwn(paths,raw) ? raw : 'overview';
    document.querySelectorAll('[data-section]').forEach(a=>a.setAttribute('aria-current',a.dataset.section===section?'page':'false'));
    window.scrollTo(0,0);
    if (raw === 'issue') {let id;try{id=decodeURIComponent(parts.slice(1).join('/'))}catch{id=''}renderIssue(id)}
    else if (section==='overview') overview();
    else if (section==='reviews') reviews(parts[1]);
    else if (section==='plan') renderPlan(parts[1],parts[2]);
    else if (section==='sources') sources();
    else renderList();
    UI.status();
    document.title = `${raw==='issue'?'Issue':paths[section]} · ${p.title} · idea-shaokao`;
    app.dataset.route = parts.join('/') || 'overview';
  }
  app.addEventListener('submit',event=>{if(event.target.id==='issue-search'){event.preventDefault();query=document.getElementById('issue-query').value;renderRows()}});
  app.addEventListener('input',event=>{if(event.target.id==='issue-query'){query=event.target.value;renderRows()}});
  app.addEventListener('change',event=>{if(event.target.id==='severity-filter'){severity=event.target.value;renderRows()}if(event.target.id==='round-filter'){round=event.target.value;renderRows()}});
  app.addEventListener('click',event=>{const btn=event.target.closest('button');if(!btn)return;if(btn.hasAttribute('data-state')){state=btn.dataset.state;renderList();UI.status()}if(btn.hasAttribute('data-clear-filters')){state='all';severity='all';round='all';query='';renderList();UI.status()}});
  document.querySelector('.skip-link').addEventListener('click',event=>{event.preventDefault();document.getElementById('main-content').focus();document.getElementById('main-content').scrollIntoView()});
  window.addEventListener('dossier:issue',event=>{location.hash='issue/'+encodeURIComponent(event.detail.id)});
  window.addEventListener('hashchange',route);
  route();
})();
