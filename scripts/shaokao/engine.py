"""Append-only research workflow and role-scoped work queue.

Each commit is one atomically linked event. Replaying events recovers all state;
project.json is only a convenience checkpoint, never the source of truth.
"""
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import uuid

from . import contracts as C
from .conference import validate_rubric


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as f:
            temp = f.name
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if temp and os.path.exists(temp):
            os.unlink(temp)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def current(project):
    return project['rounds'][-1]


def attempt(project):
    return current(project)['iterations'][-1]


def start_round(project, at):
    n = len(project['rounds']) + 1
    project['rounds'].append({'id': f'round-{n:02}', 'number': n,
        'predecessor': f'round-{n-1:02}' if n > 1 else None,
        'rubric_id': C.digest(project['rubric']), 'rubric': deepcopy(project['rubric']),
        'contribution_type': project['config'].get('contribution_type'),
        'created_at': at, 'phase': 'revision' if n > 1 else 'literature',
        'iterations': [], 'reviews': {}, 'discussion': {}, 'final_reviews': {}, 'exchanges': [],
        'reviewer_profiles': {f'R{i+1}': {'id': f'R{i+1}', 'expertise': C.REVIEW_ROLES[i], 'initial_context': 'fresh_blind'}
                              for i in range(project['config']['reviewers'])}})
    project['status'] = 'in_progress'


def all_concerns(round_data, include_stress=True):
    rows = []
    if include_stress and round_data['iterations']:
        for report in round_data['iterations'][-1].get('stress', {}).values():
            rows += report['result']['concerns']
    for collection in ('reviews', 'discussion', 'final_reviews'):
        for report in round_data[collection].values():
            rows += report['result']['concerns']
    for chair_role in ('ac', 'sac'):
        if round_data.get(chair_role):
            rows += round_data[chair_role]['result'].get('concerns', [])
    for exchange in round_data.get('exchanges', []):
        for role, report in exchange['responses'].items():
            if role != 'author':
                rows += report['result'].get('concerns', [])
    for report in round_data.get('active_exchange', {}).values():
        rows += report['result'].get('concerns', [])
    # A follow-up may carry the same issue; the identity remains stable.
    result = {}
    for row in rows:
        if row['id'] in result:
            C.require(row == result[row['id']], 'a carried concern must retain its original content and severity')
        result[row['id']] = row
    return result


def major(rows):
    return {key: row for key, row in rows.items() if row['severity'] in ('critical', 'major')}


def task_id(project, role):
    r = current(project)
    return f'{r["id"]}.n{len(r["iterations"]):02}.{r["phase"]}.{role}'


def pending(project):
    if project['status'] in ('accepted_simulation', 'budget_exhausted', 'abandoned'):
        return []
    if not project.get('rubric'):
        return [{'id': 'conference-rubric', 'role': 'conference_investigator', 'stage': 'rubric'}]
    if not project['rounds']:
        return []
    r, roles = current(project), []
    phase = r['phase']
    if phase == 'stress':
        roles = [role for role in C.STRESS_ROLES if role not in attempt(project)['stress']]
    elif phase == 'review':
        roles = [f'R{n+1}' for n in range(project['config']['reviewers']) if f'R{n+1}' not in r['reviews']]
    elif phase in ('discussion', 'final_reviews'):
        collection = r[phase]
        roles = [key for key in r['reviews'] if key not in collection]
    elif phase == 'exchange':
        exchange = r['rubric']['procedures']['exchanges'][r['exchange_index']]
        if exchange['role'] == 'author':
            roles = ['author']
        else:
            roles = [key for key in r['reviews'] if key not in r.get('active_exchange', {})]
    else:
        roles = [dict(literature='literature_investigator', idea='idea_composer', paper='author',
                      novelty_response='author', rebuttal='author', revision='author', ac='ac', sac='sac')[phase]]
    return [{'id': task_id(project, role), 'role': role, 'stage': phase, 'round': r['id'],
             'paper_id': attempt(project).get('paper_id') if r['iterations'] else None} for role in roles]


def rubric_context(rubric):
    """Official definitions and provenance, without irrelevant raw page markup."""
    result = {key: deepcopy(value) for key, value in rubric.items() if key != 'sources'}
    result['sources'] = [{key: row[key] for key in ('id', 'kind', 'url', 'year', 'track', 'retrieved_at', 'status', 'sha256', 'error') if key in row}
                         for row in rubric['sources']]
    return result


def approved_context(project, task):
    """Fresh reviewers receive exactly the frozen common packet, never peer scores."""
    r = current(project)
    phase, role = task['stage'], task['role']
    base = {'project': {'id': project['id'], 'topic': project['topic'], 'conference': project['conference'],
                        'constraints': project['config']['constraints'], 'contribution_type': r.get('contribution_type')}, 'task': task,
            'rubric': rubric_context(r['rubric']), 'simulation': True, 'evidence_stage': project['config']['evidence_stage']}
    if phase == 'revision':
        base['previous_round'] = deepcopy(project['rounds'][-2])
        base['previous_round']['rubric'] = rubric_context(base['previous_round']['rubric'])
    if phase in ('literature', 'idea', 'paper'):
        base['revision'] = r.get('revision')
        if len(project['rounds']) > 1:
            previous = project['rounds'][-2]
            base['previous_paper'] = previous['iterations'][-1]['paper']
            base['previous_assessment'] = previous['sac']
        if 'literature' in r:
            base['literature'] = r['literature']
        if r['iterations']:
            base['idea'] = attempt(project).get('idea')
            if len(r['iterations']) > 1:
                base['previous_novelty_attempt'] = r['iterations'][-2]
    if phase == 'stress':
        base.update(literature=r['literature'], idea=attempt(project)['idea'],
                    paper=attempt(project)['paper'], paper_sha256=attempt(project)['paper_sha256'])
    elif phase == 'review':
        base['submission'] = deepcopy(r['submission'])
        base['reviewer_profile'] = r['reviewer_profiles'][role]
    elif phase in ('novelty_response', 'rebuttal', 'discussion', 'exchange', 'final_reviews', 'ac', 'sac'):
        if phase == 'novelty_response':
            base.update(paper=attempt(project)['paper'], literature=r['literature'], idea=attempt(project)['idea'])
            base['novelty_reports'] = attempt(project)['stress']
        else:
            base.update(submission=r['submission'], initial_reviews=r['reviews'], rebuttal=r.get('rebuttal'))
            if phase != 'rebuttal':
                base.update(reviewer_discussion={} if phase == 'discussion' else r['discussion'], exchanges=r['exchanges'])
            if phase in ('ac', 'sac'):
                base['final_reviews'] = r['final_reviews']
            if phase == 'sac':
                base['ac_meta_review'] = r['ac']
    return base


def envelope(project, task):
    from .prompts import prompt_for, output_contract
    context = approved_context(project, task)
    return {'schema_version': 2, 'task': task, 'context_sha256': C.digest(context),
            'context': context, 'instruction': prompt_for(task), 'output_contract': output_contract(task),
            'return_envelope': {'task_id': task['id'], 'context_sha256': C.digest(context),
                'session_id': 'unique isolated host session identifier', 'independent': True, 'result': {}}}


def check_session(project, task, response):
    C.fields(response, ('session_id',), 'response provenance')
    isolated = task['stage'] in ('stress', 'review', 'ac', 'sac')
    if task['stage'] in ('discussion', 'final_reviews') or task['stage'] == 'exchange' and task['role'] != 'author':
        C.require(response.get('independent') is True, 'reviewer reassessment requires independent provenance')
        own = current(project)['reviews'][task['role']]['session_id']
        lineage = current(project).get('reviewer_sessions', {}).get(task['role'], [own])
        C.require(response['session_id'] in lineage or response['session_id'] not in project.get('sessions', []), 'reviewer reassessment cannot reuse an author or another reviewer session')
    if isolated:
        C.require(response.get('independent') is True, 'independent role requires a fresh isolated context')
        C.require(project['config']['execution_mode'] in ('independent', 'external_review'), 'self-review cannot satisfy independent gates')
        session = response['session_id']
        previous = project.get('sessions', [])
        C.require(session not in previous, 'initial reviewers, adversaries, and chairs must use separate sessions')


def validate_result(project, task, response):
    C.obj(response, 'agent response')
    C.require(response.get('task_id') == task['id'], 'response references a stale or incorrect task')
    expected = envelope(project, task)
    C.require(response.get('context_sha256') == expected['context_sha256'], 'response references a different paper/context snapshot')
    check_session(project, task, response)
    data = C.obj(response.get('result'), 'agent result')
    r, phase, role = current(project), task['stage'], task['role']
    if phase == 'literature':
        C.literature(data)
    elif phase == 'idea':
        C.idea(data, r['literature']['result'])
    elif phase == 'paper':
        C.paper(data, attempt(project)['idea']['result'], r['literature']['result'])
    elif phase == 'stress':
        C.stress(data, role)
        known = {row['id'] for row in r['literature']['result']['papers']}
        known.update(row['id'] for row in data.get('discovered_papers', []))
        if role == 'prior_art' and data['verdict'] == 'PASS':
            searches = r['literature']['result']['searches']
            C.require(all(any(s['coverage'] == category and s['status'] == 'ok' for s in searches) for category in ('closest', 'concurrent')), 'a prior-art PASS requires successful closest and concurrent searches')
            papers = {row['id']: row for row in r['literature']['result']['papers']}
            C.require(all(papers[key]['access_depth'] == 'full_text' for key in r['literature']['result']['closest_ids']), 'a prior-art PASS requires full-text inspection of closest work')
        for row in data.get('comparison_table', []):
            C.require(row['paper_id'] in known, 'prior-art comparison must link registered evidence')
        peers = {c['id'] for report in attempt(project)['stress'].values() for c in report['result']['concerns']}
        C.require(not peers.intersection(c['id'] for c in data['concerns']), 'independent novelty concerns need unique IDs')
    elif phase == 'novelty_response':
        C.responses(data, major(all_concerns(r, include_stress=True)))
    elif phase == 'review':
        C.review(data, r['rubric'])
        C.require(not set(c['id'] for c in data['concerns']).intersection(all_concerns(r)), 'independent reviews need unique concern IDs')
    elif phase == 'rebuttal':
        C.responses(data, major(all_concerns(r)), r['rubric']['procedures']['exchanges'][0].get('max_chars'))
    elif phase in ('discussion', 'final_reviews') or (phase == 'exchange' and role != 'author'):
        C.review(data, r['rubric'], 'final')
        existing = all_concerns(r)
        for row in data['concerns']:
            C.require(row['id'] not in existing or row == existing[row['id']], 'a carried concern must retain its original content and severity')
        own = {row['id'] for row in r['reviews'][role]['result']['concerns']}
        C.require(own <= set(data['concern_status']), 'reviewer must individually reassess every original concern')
        C.require(set(data['concern_status']) <= set(all_concerns(r)) | {c['id'] for c in data['concerns']}, 'reassessment references an unknown concern')
        index = 1 if phase == 'discussion' else r.get('exchange_index', 1)
        limit = r['rubric']['procedures']['exchanges'][index].get('max_chars') if phase != 'final_reviews' else None
        if limit:
            C.require(len(review_text(data, r['rubric'])) <= limit, 'reviewer discussion exceeds official character limit')
    elif phase == 'exchange':
        C.responses(data, major(all_concerns(r)), r['rubric']['procedures']['exchanges'][r['exchange_index']].get('max_chars'))
    elif phase in ('ac', 'sac'):
        known = all_concerns(r)
        C.chair(data, phase, known, r['rubric'])
        C.require(data['decision_scope'] == r['rubric']['procedures'][phase]['scope'], 'chair authority does not match the venue procedure')
    elif phase == 'revision':
        C.fields(data, ('summary', 'insight_change', 'method_change', 'prediction_change', 'claims_removed', 'remaining_concerns'), 'research revision')
        C.require(data.get('kind') in ('mechanism', 'hypothesis', 'formulation', 'theory', 'experimental_design', 'prediction_calibration', 'positioning', 'verification'), 'revision must make a substantive research change')
        previous = project['rounds'][-2]
        C.require(data.get('kind') != 'verification' or previous.get('acceptance_eligible'), 'verification-only rounds require an eligible prior assessment')
        addressed = C.items(data.get('concern_ids'), 'revision.concern_ids', 0 if previous.get('acceptance_eligible') else 1)
        C.require(set(addressed) <= set(all_concerns(previous)), 'revision must reference actual prior-round concerns')
    if phase in ('novelty_response', 'rebuttal') or phase == 'exchange' and role == 'author':
        C.require({row['concern_id'] for row in data['responses']} <= set(all_concerns(r)), 'author response references an unknown concern')
    return data


def review_text(data, rubric):
    # The discussion comment is bounded; structured scores/metadata are separate form fields.
    return data['assessment'] + '\n' + data.get('change_reason', '') + '\n' + '\n'.join(
        row['reason'] + '\n' + row['evidence'] for row in data.get('concern_status', {}).values())


def next_exchange(r):
    index = r.get('exchange_index', 1) + 1
    if index < len(r['rubric']['procedures']['exchanges']):
        r.update(phase='exchange', exchange_index=index, active_exchange={})
    else:
        r['phase'] = 'final_reviews' if len(r['rubric']['procedures']['exchanges']) > 2 else 'ac'
        if r['phase'] == 'ac':
            r['final_reviews'] = deepcopy(r['discussion'])


def finish(project, at):
    r = current(project)
    ac, sac = r['ac']['result'], r['sac']['result']
    known = all_concerns(r)
    critical_open = [key for key, c in known.items() if c['severity'] == 'critical' and sac['concern_status'][key]['status'] != 'resolved']
    r['outcome'] = sac['case']
    eligible = ac['case'] == sac['case'] == 'strong_acceptance' and not critical_open
    eligible = eligible and all(ac['readiness'][key]['met'] and sac['readiness'][key]['met'] for key in C.READINESS)
    # Acceptance also requires agreement on every major concern disposition.
    eligible = eligible and all(ac['concern_status'].get(key, {}).get('status') == sac['concern_status'][key]['status'] == 'resolved'
                                for key, concern in known.items() if concern['severity'] in ('critical', 'major'))
    if ac['case'] != sac['case']:
        r['chair_disagreement'] = {'ac': ac['case'], 'sac': sac['case'], 'rationale': sac['ac_reasoning_assessment']}
    r['acceptance_eligible'] = bool(eligible)
    r['phase'] = 'complete'
    r['completed_at'] = at
    chain = r['submission']['idea']['insight_chain']
    r['research_identity'] = C.digest({key: chain[key] for key in ('key_insight', 'falsifiable_hypothesis', 'novel_mechanism')})
    streak = 0
    for history in reversed(project['rounds']):
        if not history.get('acceptance_eligible') or history['rubric_id'] != r['rubric_id'] or history.get('research_identity') != r['research_identity']:
            break
        streak += 1
    if eligible and streak >= project['config']['acceptance_rounds']:
        project['status'] = 'accepted_simulation'
        project['final_paper_id'] = r['submission']['paper_id']
    elif len(project['rounds']) >= project['config']['max_rounds']:
        project['status'] = 'budget_exhausted'
    else:
        start_round(project, at)


def apply_result(project, event):
    task, response = event['task'], event['response']
    r, phase, role = current(project), task['stage'], task['role']
    record = dict(response, at=event['at'], paper_id=task.get('paper_id'), round_id=r['id'])
    if response['session_id'] not in project['sessions']:
        project['sessions'].append(response['session_id'])
    if role.startswith('R') and phase in ('review', 'discussion', 'exchange', 'final_reviews'):
        r.setdefault('reviewer_sessions', {}).setdefault(role, []).append(response['session_id'])
    if phase in ('stress', 'review', 'ac', 'sac'):
        project['independent_sessions'].append(response['session_id'])
    if phase == 'revision':
        r.update(revision=record, phase='literature')
    elif phase == 'literature':
        r.update(literature=record, phase='idea')
    elif phase == 'idea':
        r['iterations'].append({'number': len(r['iterations']) + 1, 'idea': record, 'literature': deepcopy(r['literature']), 'stress': {}})
        r['phase'] = 'paper'
    elif phase == 'paper':
        a = attempt(project)
        a.update(paper=record, paper_id=f'{r["id"]}.paper-{a["number"]:02}',
                 paper_sha256=C.digest(response['result']))
        r['phase'] = 'stress'
    elif phase == 'stress':
        attempt(project)['stress'][role] = record
        if len(attempt(project)['stress']) == 3:
            r['phase'] = 'novelty_response'
    elif phase == 'novelty_response':
        a = attempt(project)
        a['response'] = record
        verdicts = [v['result']['verdict'] for v in a['stress'].values()]
        if all(v == 'PASS' for v in verdicts):
            a['gate'] = 'PASS'
            r['submission'] = {'paper_id': a['paper_id'], 'paper_sha256': a['paper_sha256'],
                'paper': deepcopy(a['paper']['result']), 'idea': deepcopy(a['idea']['result']),
                'literature': deepcopy(r['literature']['result']), 'novelty': deepcopy(a['stress']),
                'rubric_id': r['rubric_id'], 'contribution_type': r.get('contribution_type'), 'submitted_at': event['at'], 'simulation': True}
            r['phase'] = 'review'
        else:
            a['gate'] = 'FAIL' if 'FAIL' in verdicts else 'CONDITIONAL PASS'
            if len(r['iterations']) >= project['config']['max_stress_iterations'] or any(x['action'] == 'abandon' for x in response['result']['responses']):
                project['status'] = 'abandoned'
                r.update(phase='novelty_failed', outcome='fundamental_failure')
            else:
                r['phase'] = 'literature'
    elif phase == 'review':
        r['reviews'][role] = record
        if len(r['reviews']) == project['config']['reviewers']:
            r['phase'] = 'rebuttal'
    elif phase == 'rebuttal':
        r.update(rebuttal=record, phase='discussion', exchange_index=1)
    elif phase == 'discussion':
        r['discussion'][role] = record
        if len(r['discussion']) == len(r['reviews']):
            next_exchange(r)
    elif phase == 'exchange':
        exchange = r['rubric']['procedures']['exchanges'][r['exchange_index']]
        if role == 'author':
            r['exchanges'].append({'index': r['exchange_index'], 'procedure': exchange, 'responses': {'author': record}})
            next_exchange(r)
        else:
            r['active_exchange'][role] = record
            if len(r['active_exchange']) == len(r['reviews']):
                r['exchanges'].append({'index': r['exchange_index'], 'procedure': exchange, 'responses': r['active_exchange']})
                next_exchange(r)
    elif phase == 'final_reviews':
        r['final_reviews'][role] = record
        if len(r['final_reviews']) == len(r['reviews']):
            r['phase'] = 'ac'
    elif phase == 'ac':
        r.update(ac=record, phase='sac')
    elif phase == 'sac':
        r['sac'] = record
        finish(project, event['at'])


def reduce_event(project, event):
    if event['type'] == 'init':
        return deepcopy(event['project'])
    if event['type'] == 'rubric':
        project['rubric'] = event['rubric']
        if not project['rounds'] or current(project)['phase'] == 'complete':
            start_round(project, event['at'])
        elif current(project)['phase'] == 'revision':
            current(project).update(rubric=deepcopy(event['rubric']), rubric_id=C.digest(event['rubric']), contribution_type=project['config'].get('contribution_type'))
    elif event['type'] == 'contribution_type_selected':
        project['config']['contribution_type'] = event['contribution_type']
    elif event['type'] == 'target_changed':
        project['conference'] = event['conference']
        project['rubric'] = None
        project['status'] = 'needs_rubric'
    elif event['type'] == 'result':
        apply_result(project, event)
    elif event['type'] == 'failure':
        project['failures'].append({key: event[key] for key in ('task_id', 'at', 'error')})
    project['updated_at'] = event['at']
    return project


class Store:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve()
        self.events = self.root / 'events'
        self.project, self.sequence, self.head = None, 0, None
        self.reload()

    @classmethod
    def create(cls, root, topic, conference, config=None):
        root = Path(root).expanduser().resolve()
        C.require(not root.exists(), 'workspace already exists; resume instead of reinitializing')
        C.fields(conference, ('name', 'track'), 'target conference')
        C.require(type(conference.get('year')) is int, 'target year is required')
        defaults = {'max_rounds': 4, 'max_stress_iterations': 3, 'reviewers': 4, 'acceptance_rounds': 2,
                    'execution_mode': 'independent', 'evidence_stage': 'proposal', 'constraints': '', 'test_mode': False, 'contribution_type': None}
        defaults.update(config or {})
        for key in ('max_rounds', 'max_stress_iterations', 'acceptance_rounds'):
            C.require(type(defaults[key]) is int and 1 <= defaults[key] <= 100, key + ' must be 1–100')
        C.require(defaults['reviewers'] in (3, 4), 'use three or four independent reviewers')
        C.require(defaults['execution_mode'] in ('independent', 'external_review', 'single_agent'), 'invalid execution mode')
        C.require(defaults['evidence_stage'] in ('proposal', 'implementation', 'paper'), 'invalid evidence stage')
        C.require(defaults['evidence_stage'] == 'proposal', 'this engine assesses paper-level proposals; measured implementation/paper stages require a separate evidence audit')
        C.require(type(defaults['test_mode']) is bool, 'test_mode must be boolean')
        project = {'schema_version': 2, 'id': str(uuid.uuid4()), 'slug': root.name,
                   'topic': C.text(topic, 'topic'), 'conference': conference, 'config': defaults,
                   'status': 'needs_rubric', 'rounds': [], 'rubric': None,
                   'independent_sessions': [], 'sessions': [], 'failures': [], 'created_at': now(), 'updated_at': now()}
        root.mkdir(parents=True)
        (root / 'events').mkdir()
        store = cls(root)
        store.commit({'type': 'init', 'project': project})
        return store

    def reload(self):
        self.project, self.sequence, self.head = None, 0, None
        if not self.events.exists():
            return
        for path in sorted(self.events.glob('*.json')):
            event = json.loads(path.read_text(encoding='utf-8'))
            signature = event.pop('sha256', None)
            C.require(event.get('sequence') == self.sequence + 1 and path.name == f'{self.sequence+1:06}.json', 'journal sequence is missing or reordered')
            C.require(event.get('previous') == self.head and signature == C.digest(event), 'journal hash chain is invalid; preserve files and inspect corruption')
            self.project = reduce_event(self.project, event)
            self.sequence, self.head = event['sequence'], signature
        return self.project

    def commit(self, event):
        seq, previous = self.sequence, self.head
        self.reload()
        C.require((seq, previous) == (self.sequence, self.head), 'workspace changed concurrently; reload the pending task')
        event = dict(event, at=now(), sequence=seq + 1, previous=previous)
        # Preflight the full reducer before committing. A valid role artifact must
        # never leave an unreplayable event if its transition exposes a bug.
        candidate = reduce_event(deepcopy(self.project), event)
        if candidate['rounds']:
            for round_data in candidate['rounds']:
                all_concerns(round_data)
        signature = C.digest(event)
        event['sha256'] = signature
        # Link a complete fsynced temp file to an exclusive sequence name. A crash
        # before linking leaves no event; a crash after linking is replayable.
        name = None
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=self.events, prefix='.pending-', delete=False) as f:
                name = f.name
                f.write(canonical(event) + '\n')
                f.flush()
                os.fsync(f.fileno())
            try:
                os.link(name, self.events / f'{seq+1:06}.json')
            except FileExistsError as error:
                raise C.ContractError('concurrent commit; reload and retry the exact pending task') from error
        finally:
            if name and os.path.exists(name):
                os.unlink(name)
        self.reload()
        self.checkpoint()

    def checkpoint(self):
        atomic(self.root / 'project.json', json.dumps(self.project, indent=2, ensure_ascii=False, allow_nan=False) + '\n')

    def install_rubric(self, rubric):
        C.require(self.project is not None, 'not an initialized engine workspace')
        validate_rubric(rubric, self.project['conference'])
        if not self.project['config']['test_mode']:
            created = datetime.fromisoformat(self.project['created_at'])
            C.require(all(datetime.fromisoformat(s['retrieved_at'].replace('Z', '+00:00')) >= created for s in rubric['sources']), 'fetch official sources for this project; a cached rubric from an earlier project is insufficient')
        categories = {row['id'] for row in rubric.get('contribution_types', [])}
        if categories:
            C.require(self.project['config'].get('contribution_type') in categories, 'select an official contribution type before installing this rubric: ' + ', '.join(sorted(categories)))
        C.require(not self.project.get('rubric'), 'rubric is already frozen for this project; change the target only at a round boundary')
        self.commit({'type': 'rubric', 'rubric': rubric})

    def select_contribution_type(self, contribution_type):
        C.require(not self.project.get('rubric'), 'select contribution type before rubric installation, at the project or venue-change boundary')
        C.text(contribution_type, 'contribution_type')
        self.commit({'type': 'contribution_type_selected', 'contribution_type': contribution_type})

    def change_target(self, conference):
        C.fields(conference, ('name', 'track'), 'target')
        C.require(type(conference.get('year')) is int, 'target year must be integer')
        C.require(self.project['rounds'] and current(self.project)['phase'] in ('complete', 'revision'), 'change venue only at a completed round boundary')
        C.require(len(self.project['rounds']) < self.project['config']['max_rounds'] or current(self.project)['phase'] == 'revision', 'venue change cannot reset the research budget')
        self.commit({'type': 'target_changed', 'conference': conference})

    def submit(self, response):
        tasks = pending(self.project)
        task = next((t for t in tasks if t['id'] == response.get('task_id')), None)
        C.require(task is not None and task['stage'] != 'rubric', 'no matching pending task; completed outputs are immutable')
        validate_result(self.project, task, response)
        self.commit({'type': 'result', 'task': task, 'response': response})
        return pending(self.project)

    def failure(self, task, error):
        self.commit({'type': 'failure', 'task_id': task['id'], 'error': str(error)[:4000]})
