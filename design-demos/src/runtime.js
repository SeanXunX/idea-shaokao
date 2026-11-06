/* Offline review UI. Bundled sources are immutable; annotations have a separate store. */
'use strict';
const D = JSON.parse(document.getElementById('review-data').textContent);
const UI = (() => {
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const issue = id => D.issues.find(item => item.id === id);
  const target = id => D.targets[id];
  let notes = [], key = '', storageAvailable = false, editingId = null, currentTarget = null, toastTimer;
  const types = ['Question', 'Needs evidence', 'Suggested change'];
  const sourceButton = (id, label) => `<button type="button" class="ui-button source-button" data-evidence="${escape(id)}">${escape(label || D.sources[id]?.title || 'Read source')} <span aria-hidden="true">↗</span></button>`;
  const noteButton = (id, label) => `<button type="button" class="ui-button annotation-button" data-annotate="${escape(id)}">${escape(label || 'Add annotation')} <span aria-hidden="true">+</span></button>`;
  const notesButton = () => '<button type="button" class="ui-button" data-show-notes>My notes <span data-note-count>0</span></button>';
  const exportButton = () => '<button type="button" class="ui-button" data-export-feedback>Export feedback <span aria-hidden="true">↓</span></button>';
  function issueBody(id) {
    const i = issue(id); if (!i) return '';
    return `<div class="issue-body" data-inspected-issue="${escape(id)}"><p class="issue-meta">Original IDs: ${i.aliases.map(escape).join(' · ')}<br>${i.aliases.length > 1 ? 'Duplicate concerns grouped; original reviewer identities retained.' : 'Original reviewer concern retained.'}</p><div class="issue-steps"><section class="issue-step"><h4>01 / Reviewer concern</h4><p>${escape(i.concern)}</p>${sourceButton(i.sources[0], 'Original review')}</section><section class="issue-step"><h4>02 / Author response</h4><p>${escape(i.response)}</p>${sourceButton('rebuttal', 'Author rebuttal')}</section><section class="issue-step"><h4>03 / Reassessment</h4><p>${escape(i.reassessment)}</p>${sourceButton(i.sources.find(s => s.startsWith('final')) || 'sac', 'Final assessment')}</section></div><div class="issue-criterion"><strong>Closure criterion</strong><p>${escape(i.criterion)}</p><p>Recorded status: <strong>${escape(i.status)}</strong>. ${id === 'R01-R2-03' ? 'Only the reporting/action requirement is resolved; runtime is still unknown.' : 'The disposition applies to unchanged, reviewed v01.'}</p></div><div class="issue-actions">${noteButton(id, 'Annotate this issue')}${sourceButton('issues', 'Full issue tracker')}${sourceButton('sac', 'SAC assessment')}</div></div>`;
  }
  function status() {
    document.querySelectorAll('[data-note-count]').forEach(el => el.textContent = notes.length);
    document.querySelectorAll('[data-storage-status]').forEach(el => {
      el.textContent = storageAvailable ? (notes.length ? 'Draft notes saved in this browser' : 'Local drafts available') : 'Session only · export to keep notes';
      el.classList.toggle('storage-fallback', !storageAvailable);
    });
    window.dispatchEvent(new CustomEvent('dossier:notes', {detail:{count:notes.length}}));
  }
  function persist() {
    if (storageAvailable) {
      try { localStorage.setItem(key, JSON.stringify(notes)); }
      catch { storageAvailable = false; }
    }
    status();
  }
  function toast(text) {
    const el = document.getElementById('dossier-toast');
    el.textContent = text; el.hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(() => el.hidden = true, 3200);
  }
  function showEvidence(id) {
    const source = D.sources[id]; if (!source) return;
    const dlg = document.getElementById('evidence-dialog');
    document.getElementById('source-select').value = id;
    document.getElementById('source-title').textContent = source.title;
    document.getElementById('source-meta').textContent = `${source.kind} · ${source.path}\nSHA-256: ${source.sha256}`;
    document.getElementById('source-text').textContent = source.text;
    if (!dlg.open) dlg.showModal();
    dlg.scrollTop = 0;
  }
  function saveDraft() {
    if (!storageAvailable || editingId) return;
    try { localStorage.setItem(key + ':draft', JSON.stringify({target:currentTarget, type:document.getElementById('note-type').value, text:document.getElementById('note-text').value})); }
    catch { storageAvailable = false; status(); }
  }
  function annotate(id, noteId = null) {
    if (!target(id)) return;
    editingId = noteId; currentTarget = id;
    const note = notes.find(n => n.id === noteId);
    let draft;
    if (!note && storageAvailable) { try { draft = JSON.parse(localStorage.getItem(key + ':draft') || 'null'); } catch {} }
    document.getElementById('note-heading').textContent = note ? 'Edit annotation' : 'Add annotation';
    document.getElementById('note-target').textContent = `${id} · ${target(id).title}`;
    document.getElementById('note-type').value = note?.type || (draft?.target === id && types.includes(draft.type) ? draft.type : types[0]);
    document.getElementById('note-text').value = note?.text ?? (draft?.target === id ? draft.text : '') ?? '';
    document.getElementById('note-error').hidden = true;
    document.getElementById('notes-dialog').close();
    document.getElementById('annotation-dialog').showModal();
    document.getElementById('note-text').focus();
  }
  function renderNotes() {
    const host = document.getElementById('notes-list');
    host.innerHTML = notes.length ? notes.map(note => `<article class="note-entry"><div class="note-context">${escape(note.type)} · ${escape(note.target)}</div><h3>${escape(target(note.target).title)}</h3><p>${escape(note.text)}</p><div class="note-context">${escape(note.sources.map(id => D.sources[id].path).join(' · '))}</div><div class="dialog-actions"><button type="button" class="ui-button" data-edit-note="${escape(note.id)}">Edit</button><button type="button" class="ui-button" data-delete-note="${escape(note.id)}">Delete</button></div></article>`).join('') : '<p class="empty-notes">No annotations yet. Attach a question or suggestion to a claim, issue, or report section.</p>';
  }
  function showNotes() { renderNotes(); document.getElementById('notes-dialog').showModal(); }
  function markdown() {
    const p = D.project;
    let out = `# Idea Shaokao — Review Feedback\n\nProject: ${p.slug}\nProposal version: ${p.version}\nReview round: ${p.round} of ${p.maxRounds}\nStage: ${p.stage}\nRecorded SAC recommendation: ${p.decision}\n\nThese human annotations are separate from the scientific record. They do not alter source evidence, issue dispositions, or reviewer judgments.\n`;
    if (!notes.length) return out + '\nNo annotations saved.\n';
    notes.forEach((note, index) => {
      const runs = note.text.match(/`+/g) || [];
      const fence = '`'.repeat(Math.max(3, ...runs.map(s => s.length + 1)));
      out += `\n## ${index + 1}. ${target(note.target).title}\n\nTarget ID: ${note.target}\nType: ${note.type}\nUpdated: ${note.updatedAt}\nSource references:\n`;
      note.sources.forEach(id => { const s = D.sources[id]; out += `- ${s.path} (SHA-256: ${s.sha256})\n`; });
      out += `\n${fence}text\n${note.text}\n${fence}\n`;
    });
    return out;
  }
  function exportFeedback() {
    const url = URL.createObjectURL(new Blob([markdown()], {type:'text/markdown;charset=utf-8'}));
    const link = document.createElement('a'); link.href = url; link.download = 'review_feedback.md';
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast('Feedback exported. The research record is unchanged.');
  }
  function mount(direction) {
    key = `idea-shaokao:dossier:v1:${D.project.slug}:${D.project.version}:${direction}`;
    try {
      localStorage.setItem(key + ':probe', '1'); localStorage.removeItem(key + ':probe'); storageAvailable = true;
      const saved = JSON.parse(localStorage.getItem(key) || '[]');
      if (Array.isArray(saved)) notes = saved.filter(n => n && typeof n.id === 'string' && target(n.target) && types.includes(n.type) && typeof n.text === 'string' && typeof n.updatedAt === 'string').map(n => ({...n,sources:target(n.target).sources}));
    } catch { storageAvailable = false; }
    document.body.insertAdjacentHTML('beforeend', `<dialog class="dossier-dialog" id="evidence-dialog" aria-labelledby="source-title"><header><div><span class="dialog-kicker">Bundled evidence · read only</span><h2 id="source-title">Source</h2></div><button type="button" class="ui-button" data-close-dialog>Close reader ×</button></header><div class="dialog-content"><label for="source-select">Source document</label><select id="source-select">${Object.values(D.sources).map(s => `<option value="${escape(s.id)}">${escape(s.title)}</option>`).join('')}</select><p id="source-meta" class="source-meta"></p><pre id="source-text" class="source-text"></pre></div></dialog><dialog class="dossier-dialog" id="annotation-dialog" aria-labelledby="note-heading"><header><div><span class="dialog-kicker">Human feedback · local draft</span><h2 id="note-heading">Add annotation</h2></div><button type="button" class="ui-button" data-close-dialog>Close ×</button></header><form id="annotation-form" class="dialog-content"><p id="note-target" class="source-meta"></p><label for="note-type">Comment type</label><select id="note-type">${types.map(type => `<option>${type}</option>`).join('')}</select><label for="note-text">Your comment</label><textarea id="note-text" placeholder="What should the researcher investigate, clarify, or change?" required></textarea><p class="dialog-help">Your wording is preserved. Saving a note does not resolve a research issue or change the SAC recommendation.</p><p id="note-error" role="alert" hidden>Please enter a comment.</p><div class="dialog-actions"><button type="submit" class="ui-button">Save annotation</button><button type="button" class="ui-button" data-close-dialog>Cancel</button><span class="dialog-help" data-storage-status></span></div></form></dialog><dialog class="dossier-dialog" id="notes-dialog" aria-labelledby="notes-heading"><header><div><span class="dialog-kicker">Your annotations</span><h2 id="notes-heading">Review notes <span data-note-count>0</span></h2></div><button type="button" class="ui-button" data-close-dialog>Close notes ×</button></header><div class="dialog-content"><p class="feedback-separation">Personal feedback, separate from the scientific record.</p><div id="notes-list"></div><div class="dialog-actions">${exportButton()}<span data-storage-status></span></div></div></dialog><div id="dossier-toast" class="dossier-toast" role="status" hidden></div>`);
    document.addEventListener('click', event => {
      const el = event.target.closest('button,a'); if (!el) return;
      if (el.hasAttribute('data-evidence')) showEvidence(el.dataset.evidence);
      else if (el.hasAttribute('data-annotate')) annotate(el.dataset.annotate);
      else if (el.hasAttribute('data-show-notes')) showNotes();
      else if (el.hasAttribute('data-export-feedback')) exportFeedback();
      else if (el.hasAttribute('data-close-dialog')) el.closest('dialog').close();
      else if (el.hasAttribute('data-edit-note')) { const n = notes.find(n => n.id === el.dataset.editNote); if(n) annotate(n.target,n.id); }
      else if (el.hasAttribute('data-delete-note')) { notes = notes.filter(n => n.id !== el.dataset.deleteNote); persist(); renderNotes(); toast('Annotation deleted.'); }
      if (el.hasAttribute('data-issue')) window.dispatchEvent(new CustomEvent('dossier:issue', {detail:{id:el.dataset.issue}}));
    });
    document.getElementById('source-select').addEventListener('change', event => showEvidence(event.target.value));
    document.getElementById('note-text').addEventListener('input', saveDraft);
    document.getElementById('note-type').addEventListener('change', saveDraft);
    document.getElementById('annotation-form').addEventListener('submit', event => {
      event.preventDefault();
      const text = document.getElementById('note-text').value;
      if (!text.trim()) { document.getElementById('note-error').hidden = false; return; }
      const now = new Date().toISOString();
      const prior = notes.find(n => n.id === editingId);
      const note = {id:prior?.id || `note-${Date.now()}-${Math.random().toString(36).slice(2,8)}`,target:currentTarget,type:document.getElementById('note-type').value,text,sources:target(currentTarget).sources,createdAt:prior?.createdAt || now,updatedAt:now};
      notes = prior ? notes.map(n => n.id === prior.id ? note : n) : [...notes,note];
      if (storageAvailable) { try { localStorage.removeItem(key + ':draft'); } catch { storageAvailable = false; } }
      persist(); document.getElementById('annotation-dialog').close();
      toast(storageAvailable ? 'Annotation saved in this browser.' : 'Annotation saved for this session. Export to keep it.');
    });
    status();
    setTimeout(status,0);
  }
  return {escape,issue,issueBody,sourceButton,noteButton,notesButton,exportButton,mount,showEvidence,annotate,showNotes,exportFeedback,markdown};
})();
