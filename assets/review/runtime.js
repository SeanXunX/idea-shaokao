'use strict';
const D = JSON.parse(document.getElementById('review-data').textContent);
const UI = (() => {
  const escape = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const own = (object,key) => Object.prototype.hasOwnProperty.call(object,key);
  const target = id => own(D.targets,id) ? D.targets[id] : null;
  const types = ['Question','Needs evidence','Suggested change'];
  const key = 'idea-shaokao:review:v1:'+D.project.workspaceId;
  let notes=[], drafts=new Map(), available=false, active=null, toastTimer;
  const newId=()=>globalThis.crypto?.randomUUID?.()||'note-'+Date.now()+'-'+Math.random().toString(36).slice(2);
  const sourceButton=(id,label)=>`<button type="button" class="ui-button" data-evidence="${escape(id)}">${escape(label||D.sources[id]?.title||'Read source')}</button>`;
  const noteButton=(id,label='Add feedback')=>`<button type="button" class="ui-button" data-annotate="${escape(id)}">${escape(label)}</button>`;
  const notesButton=()=>'<button type="button" class="ui-button" data-show-notes>My notes <span data-note-count>0</span></button>';
  const exportButton=()=>'<button type="button" class="ui-button" data-export-feedback>Export feedback</button>';
  function snapshot(id){const t=target(id);return {title:t.title,version:t.version??D.project.version,round:t.round??D.project.round,stage:t.stage??D.project.stage,sources:t.sources.map(id=>({id,path:D.sources[id].path,sha256:D.sources[id].sha256}))}}
  function validContext(c){return c&&typeof c.title==='string'&&typeof c.version==='string'&&Number.isInteger(c.round)&&typeof c.stage==='string'&&Array.isArray(c.sources)&&c.sources.every(s=>s&&typeof s.id==='string'&&typeof s.path==='string'&&typeof s.sha256==='string'&&/^[a-f0-9]{64}$/.test(s.sha256))}
  function validNote(n){return n&&typeof n.id==='string'&&typeof n.target==='string'&&types.includes(n.type)&&typeof n.text==='string'&&validContext(n.context)&&typeof n.createdAt==='string'&&typeof n.updatedAt==='string'}
  function validDraft(d){return d&&typeof d.key==='string'&&typeof d.target==='string'&&types.includes(d.type)&&typeof d.text==='string'&&validContext(d.context)&&(d.editingId===null||typeof d.editingId==='string')}
  function status(){
    document.querySelectorAll('[data-note-count]').forEach(el=>el.textContent=notes.length);
    document.querySelectorAll('[data-storage-status]').forEach(el=>{el.textContent=available?'Notes stay in this browser. Export or back up to keep a portable copy.':'Session only · export or back up to keep notes';el.classList.toggle('storage-fallback',!available)});
    window.dispatchEvent(new CustomEvent('dossier:notes',{detail:{count:notes.length}}));
  }
  function persist(){if(available){try{localStorage.setItem(key,JSON.stringify(notes));localStorage.setItem(key+':drafts',JSON.stringify([...drafts.values()]))}catch{available=false}}status()}
  function toast(text){const el=document.getElementById('dossier-toast');el.textContent=text;el.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.hidden=true,3200)}
  function showEvidence(id){
    if(!own(D.sources,id))return;
    const s=D.sources[id],dlg=document.getElementById('evidence-dialog');
    document.getElementById('source-title').textContent=s.title;
    document.getElementById('source-select').value=id;
    document.getElementById('source-meta').textContent=s.path+'\nSHA-256: '+s.sha256;
    document.getElementById('source-text').textContent=s.text;
    if(!dlg.open)dlg.showModal();dlg.scrollTop=0;
  }
  function condition(note){
    if(!target(note.target))return 'Target no longer appears in this report. Original context retained.';
    const changed=note.context.sources.some(s=>!own(D.sources,s.id)||D.sources[s.id].sha256!==s.sha256);
    return [note.context.version!==D.project.version?'From proposal '+note.context.version:null,changed?'Source content has changed since this annotation.':null].filter(Boolean).join(' · ');
  }
  function annotate(id,noteId=null,draftId=null){
    const note=notes.find(n=>n.id===noteId),draftKey=draftId||(noteId?'edit:'+noteId:'new:'+id),draft=drafts.get(draftKey);
    if(!target(id)&&!note&&!draft)return;
    active={target:id,editingId:noteId,key:draftKey,context:draft?.context||note?.context||snapshot(id)};
    document.getElementById('note-heading').textContent=note?'Edit annotation':'Add annotation';
    document.getElementById('note-target').textContent=id+' · '+active.context.title+'\nProposal '+active.context.version+' · '+active.context.stage+' · round '+active.context.round;
    document.getElementById('note-type').value=draft?.type||note?.type||types[0];
    document.getElementById('note-text').value=draft?.text??note?.text??'';
    document.getElementById('note-context-status').textContent=condition({target:id,context:active.context});
    document.getElementById('note-error').hidden=true;
    document.getElementById('notes-dialog').close();document.getElementById('annotation-dialog').showModal();document.getElementById('note-text').focus();
  }
  function saveDraft(){if(!active)return;const value=document.getElementById('note-text').value;if(value)drafts.set(active.key,{...active,text:value,type:document.getElementById('note-type').value});else drafts.delete(active.key);persist()}
  function renderNotes(){
    document.getElementById('notes-list').innerHTML=notes.length?notes.map(n=>`<article class="note-entry"><div class="note-context">${escape(n.type)} · ${escape(n.target)} · ${escape(n.context.version)}</div><h3>${escape(n.context.title)}</h3>${condition(n)?`<p class="note-context">${escape(condition(n))}</p>`:''}<p>${escape(n.text)}</p><div class="note-context">${n.context.sources.map(s=>escape(s.path)).join(' · ')}</div><div class="dialog-actions"><button type="button" class="ui-button" data-edit-note="${escape(n.id)}">Edit</button><button type="button" class="ui-button" data-delete-note="${escape(n.id)}">Delete</button></div></article>`).join(''):'<p class="empty-notes">No saved annotations. Add feedback to an issue, claim, or report section.</p>';
    document.getElementById('draft-list').innerHTML=drafts.size?`<h3>Unfinished drafts</h3>`+[...drafts.values()].map(d=>`<article class="note-entry"><div class="note-context">${escape(d.target)} · ${escape(d.context.version)}</div><h3>${escape(d.context.title)}</h3><div class="dialog-actions"><button type="button" class="ui-button" data-resume-draft="${escape(d.key)}">Resume draft</button><button type="button" class="ui-button" data-delete-draft="${escape(d.key)}">Discard draft</button></div></article>`).join(''):'';
  }
  function showNotes(){renderNotes();document.getElementById('notes-dialog').showModal()}
  function markdown(){
    const p=D.project;
    let out=`# Idea Shaokao — Review Feedback\n\nProject: ${p.slug}\nWorkspace ID: ${p.workspaceId}\nCurrent proposal: ${p.version}\nReview round: ${p.round} of ${p.maxRounds}\nStage: ${p.stage}\nRecorded recommendation: ${p.recommendation}\n\nHuman feedback is separate from the research record. Each annotation retains the version and sources originally reviewed.\n`;
    if(!notes.length)return out+'\nNo saved annotations. Unfinished drafts are available in the JSON backup.\n';
    notes.forEach((n,i)=>{const fence='`'.repeat(Math.max(3,...(n.text.match(/`+/g)||[]).map(s=>s.length+1)));out+=`\n## ${i+1}. ${n.context.title}\n\nTarget ID: ${n.target}\nType: ${n.type}\nAnnotated proposal: ${n.context.version}\nAnnotated round: ${n.context.round}\nAnnotated stage: ${n.context.stage}\nUpdated: ${n.updatedAt}\n${condition(n)?'Context: '+condition(n)+'\n':''}Source references:\n`;n.context.sources.forEach(s=>out+=`- ${s.path} (SHA-256: ${s.sha256})\n`);out+=`\n${fence}text\n${n.text}\n${fence}\n`});return out;
  }
  function download(name,contents,type){const url=URL.createObjectURL(new Blob([contents],{type})),a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000)}
  function exportFeedback(){download('review_feedback.md',markdown(),'text/markdown;charset=utf-8');toast('Feedback exported. The research record is unchanged.')}
  function backup(){return {schema_version:1,workspace_id:D.project.workspaceId,notes,drafts:[...drafts.values()]}}
  function exportBackup(){download('review_notes.json',JSON.stringify(backup(),null,2)+'\n','application/json');toast('Notes and unfinished drafts backed up.')}
  function restore(input){
    if(!input||input.schema_version!==1||input.workspace_id!==D.project.workspaceId)throw new Error('This backup belongs to a different workspace or uses an unsupported format.');
    if(!Array.isArray(input.notes)||!input.notes.every(validNote)||!Array.isArray(input.drafts)||!input.drafts.every(validDraft))throw new Error('Invalid notes backup. Existing annotations were kept.');
    if(new Set(input.notes.map(n=>n.id)).size!==input.notes.length||new Set(input.drafts.map(d=>d.key)).size!==input.drafts.length)throw new Error('Backup has duplicate identifiers. Existing annotations were kept.');
    for(const d of input.drafts){const n=input.notes.find(n=>n.id===d.editingId)||notes.find(n=>n.id===d.editingId);if(n&&n.target!==d.target)throw new Error('Draft target does not match its annotation. Existing annotations were kept.');}
    const renamed=new Map();
    for(const n of input.notes){const prior=notes.find(x=>x.id===n.id);if(!prior)notes.push(n);else if(JSON.stringify(prior)!==JSON.stringify(n)){const id=newId();renamed.set(n.id,id);notes.push({...n,id})}}
    for(const original of input.drafts){const edited=renamed.get(original.editingId),d=edited?{...original,editingId:edited,key:'edit:'+edited}:original;const prior=drafts.get(d.key);if(!prior)drafts.set(d.key,d);else if(JSON.stringify(prior)!==JSON.stringify(d)){const name=d.key+':import:'+newId();drafts.set(name,{...d,key:name})}}
    persist();renderNotes();toast('Backup restored. Conflicting versions were retained as separate entries.');
  }
  function mount(){
    try{localStorage.setItem(key+':probe','1');localStorage.removeItem(key+':probe');available=true;const saved=JSON.parse(localStorage.getItem(key)||'[]');if(Array.isArray(saved))notes=saved.filter(validNote);const pending=JSON.parse(localStorage.getItem(key+':drafts')||'[]');if(Array.isArray(pending))drafts=new Map(pending.filter(validDraft).map(d=>[d.key,d]))}catch{available=false}
    document.body.insertAdjacentHTML('beforeend',`<dialog class="dossier-dialog" id="evidence-dialog" aria-labelledby="source-title"><header><h2 id="source-title">Source</h2><button type="button" class="ui-button" data-close-dialog>Close reader ×</button></header><div class="dialog-content"><label for="source-select">Source document</label><select id="source-select">${Object.values(D.sources).map(s=>`<option value="${escape(s.id)}">${escape(s.path)}</option>`).join('')}</select><p class="source-meta" id="source-meta"></p><pre class="source-text" id="source-text"></pre></div></dialog><dialog class="dossier-dialog" id="annotation-dialog" aria-labelledby="note-heading"><header><h2 id="note-heading">Add annotation</h2><button type="button" class="ui-button" data-close-dialog>Close ×</button></header><form class="dialog-content" id="annotation-form"><p class="source-meta" id="note-target"></p><p class="dialog-help" id="note-context-status"></p><label for="note-type">Comment type</label><select id="note-type">${types.map(t=>`<option>${t}</option>`).join('')}</select><label for="note-text">Your comment</label><textarea id="note-text" required placeholder="What should the researcher investigate, clarify, or change?"></textarea><p class="dialog-help">Your wording and original source context are preserved. Notes do not change the recorded research assessment.</p><p id="note-error" role="alert" hidden>Please enter a comment.</p><div class="dialog-actions"><button type="submit" class="ui-button">Save annotation</button><button type="button" class="ui-button" data-close-dialog>Cancel</button><span data-storage-status class="dialog-help"></span></div></form></dialog><dialog class="dossier-dialog" id="notes-dialog" aria-labelledby="notes-heading"><header><h2 id="notes-heading">Review notes <span data-note-count>0</span></h2><button type="button" class="ui-button" data-close-dialog>Close notes ×</button></header><div class="dialog-content"><p class="feedback-separation">Human feedback, separate from the scientific record. Export feedback for the agent; use a JSON backup to move notes between browsers or file locations.</p><div id="notes-list"></div><div id="draft-list"></div><div class="dialog-actions">${exportButton()}<button type="button" class="ui-button" data-export-backup>Back up notes</button><button type="button" class="ui-button" data-import-backup>Restore notes</button><input type="file" id="notes-import" accept="application/json,.json" hidden></div><p class="dialog-help" data-storage-status></p><p id="import-error" role="alert" hidden></p></div></dialog><div class="dossier-toast" id="dossier-toast" role="status" hidden></div>`);
    document.addEventListener('click',event=>{
      const el=event.target.closest('button,a');if(!el)return;
      if(el.hasAttribute('data-evidence'))showEvidence(el.dataset.evidence);
      else if(el.hasAttribute('data-annotate'))annotate(el.dataset.annotate);
      else if(el.hasAttribute('data-show-notes'))showNotes();
      else if(el.hasAttribute('data-export-feedback'))exportFeedback();
      else if(el.hasAttribute('data-close-dialog'))el.closest('dialog').close();
      else if(el.hasAttribute('data-edit-note')){const n=notes.find(n=>n.id===el.dataset.editNote);if(n)annotate(n.target,n.id)}
      else if(el.hasAttribute('data-delete-note')){const id=el.dataset.deleteNote;notes=notes.filter(n=>n.id!==id);drafts.delete('edit:'+id);persist();renderNotes()}
      else if(el.hasAttribute('data-resume-draft')){const d=drafts.get(el.dataset.resumeDraft);if(d)annotate(d.target,d.editingId,d.key)}
      else if(el.hasAttribute('data-delete-draft')){drafts.delete(el.dataset.deleteDraft);persist();renderNotes()}
      else if(el.hasAttribute('data-export-backup'))exportBackup();
      else if(el.hasAttribute('data-import-backup'))document.getElementById('notes-import').click();
      if(el.hasAttribute('data-issue'))window.dispatchEvent(new CustomEvent('dossier:issue',{detail:{id:el.dataset.issue}}));
    });
    document.getElementById('source-select').addEventListener('change',e=>showEvidence(e.target.value));
    document.getElementById('note-text').addEventListener('input',saveDraft);document.getElementById('note-type').addEventListener('change',saveDraft);
    document.getElementById('annotation-form').addEventListener('submit',event=>{event.preventDefault();const value=document.getElementById('note-text').value;if(!value.trim()){document.getElementById('note-error').hidden=false;return}const prior=notes.find(n=>n.id===active.editingId),now=new Date().toISOString(),n={id:prior?.id||newId(),target:active.target,type:document.getElementById('note-type').value,text:value,context:active.context,createdAt:prior?.createdAt||now,updatedAt:now};notes=prior?notes.map(x=>x.id===prior.id?n:x):[...notes,n];drafts.delete(active.key);persist();document.getElementById('annotation-dialog').close();toast(available?'Annotation saved in this browser.':'Annotation saved for this session. Export to keep it.')});
    document.getElementById('notes-import').addEventListener('change',async event=>{const file=event.target.files[0],error=document.getElementById('import-error');if(!file)return;try{restore(JSON.parse(await file.text()));error.hidden=true}catch(e){error.textContent=e.message;error.hidden=false}finally{event.target.value=''}});
    status();setTimeout(status,0);
  }
  return {escape,sourceButton,noteButton,notesButton,exportButton,mount,showEvidence,annotate,showNotes,markdown,exportFeedback,exportBackup,backup,restore,status};
})();
