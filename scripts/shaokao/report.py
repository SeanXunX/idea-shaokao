"""Render the actual event journal as an offline, OpenReview-style research record."""
import hashlib
import json
from pathlib import Path

from . import contracts as C
from .engine import atomic, pending


def paper_markdown(paper, literature=None):
    output = '# ' + paper['title'] + '\n\n**Research proposal. Predictions are hypothetical; no completed experiments are implied.**\n\n'
    for key, title in zip(C.SECTIONS, C.SECTION_TITLES):
        output += f'## {title}\n\n{paper["sections"][key]}\n\n'
        if key == 'expected_results':
            output += '| Experiment | Metric | Estimated baseline | Hypothetical prediction | Assumptions and rationale | Failure condition |\n| --- | --- | --- | --- | --- | --- |\n'
            for row in paper['predictions']:
                estimate = f'{row["estimate"][0]}–{row["estimate"][1]} {row["unit"]}' if row.get('estimate') is not None else row['nonquantitative_reason']
                cells = (row['experiment_id'], row['metric'], row['baseline'], estimate, row['assumptions'] + ' ' + row['rationale'], row['failure_condition'])
                output += '| ' + ' | '.join(str(x).replace('|', '\\|').replace('\n', ' ') for x in cells) + ' |\n'
            output += '\n'
    if literature:
        output += '## References and evidence limits\n\n'
        for row in literature['papers']:
            output += f'- [{row["id"]}] {row["authors"]} ({row["year"]}). [{row["title"]}]({row["url"]}). Inspected: {row["access_depth"]}; {row["locator"]}.\n'
        output += '\n'
    return output


def related_papers(attempt):
    """Use the selected version's evidence, including independent discoveries."""
    if not attempt:
        return []
    records = [(row, attempt['literature']['source_id'], 'Literature investigation')
               for row in attempt['literature']['result']['papers']]
    for role, report in attempt['stress'].items():
        records += [(row, report['source_id'], role.replace('_', ' ').title())
                    for row in report['result'].get('discovered_papers', [])]
    catalog = {}
    closest = set(attempt['literature']['result']['closest_ids'])
    for row, source_id, origin in records:
        key = (row['url'], row['version'])
        entry = catalog.setdefault(key, dict(row, ids=[], sources=[], origins=[]))
        if row['id'] not in entry['ids']:
            entry['ids'].append(row['id'])
        if source_id not in entry['sources']:
            entry['sources'].append(source_id)
        entry['origins'].append({'role': origin, 'source_id': source_id, 'evidence_id': row['id']})
    for entry in catalog.values():
        ids = set(entry['ids'])
        entry['closest'] = bool(ids & closest)
        entry['claim_ids'] = [row['id'] for row in attempt['idea']['result']['novelty_claims']
                              if ids.intersection(row['evidence_ids'])]
        entry['prediction_ids'] = [row['id'] for row in attempt['paper']['result']['predictions']
                                   if ids.intersection(row['evidence_ids'])]
        entry['target_id'] = 'literature:' + attempt['paper_id'] + ':' + C.digest([entry['url'], entry['version']])[:16]
    return sorted(catalog.values(), key=lambda row: (not row['closest'], -row['year'], row['title']))


def build_data(store):
    project = store.project
    sources, lookup = {}, {}
    for path in sorted(store.events.glob('*.json')):
        raw = path.read_bytes()
        event = json.loads(raw)
        key = 'event-' + path.stem
        sources[key] = {'id': key, 'path': 'events/' + path.name, 'title': f'{event["type"]} · {path.stem}',
                        'text': raw.decode(), 'sha256': hashlib.sha256(raw).hexdigest()}
        if event['type'] == 'result':
            lookup[event['task']['id']] = key
    rounds, targets = [], {}
    for original in project['rounds']:
        r = json.loads(json.dumps(original))
        # Repeated raw official source snapshots remain in journal sources; do not
        # multiply them across every UI round. Each round retains its rubric hash.
        r['rubric'] = {key: value for key, value in r['rubric'].items() if key != 'sources'}
        for a in r['iterations']:
            for key in ('idea', 'paper', 'literature', 'response'):
                if a.get(key):
                    a[key]['source_id'] = lookup[a[key]['task_id']]
            for record in a['stress'].values():
                record['source_id'] = lookup[record['task_id']]
        for key in ('literature', 'revision', 'rebuttal', 'ac', 'sac'):
            if r.get(key):
                r[key]['source_id'] = lookup[r[key]['task_id']]
        for key in ('reviews', 'discussion', 'final_reviews'):
            for record in r[key].values():
                record['source_id'] = lookup[record['task_id']]
        for exchange in r['exchanges']:
            for record in exchange['responses'].values():
                record['source_id'] = lookup[record['task_id']]
        rounds.append(r)
        ids = [lookup[record['task_id']] for a in r['iterations'] for record in [a.get('paper')] if record]
        if ids:
            targets['round:' + str(r['number'])] = {'title': r['id'], 'sources': ids, 'round': r['number'],
                                                   'version': r['iterations'][-1].get('paper_id', 'Unsubmitted'), 'stage': 'proposal'}
    papers = [(r, a) for r in rounds for a in r['iterations'] if a.get('paper')]
    submitted_ids = {r['submission']['paper_id'] for r in rounds if r.get('submission')}
    fallback = next(((r, a) for r, a in reversed(papers) if a.get('paper_id') in submitted_ids), papers[-1] if papers else (None, None))
    selected = next(((r, a) for r, a in reversed(papers) if a.get('paper_id') == project.get('final_paper_id')), fallback)
    selected_round, selected_attempt = selected
    latest_decision = next((r.get('sac') or r.get('ac') for r in reversed(rounds) if r.get('sac') or r.get('ac')), None)
    source_ids = [latest_decision['source_id']] if latest_decision else list(sources)[-1:]
    rationale = latest_decision['result']['rationale'] if latest_decision else 'Review remains incomplete.'
    if project['status'] == 'abandoned':
        last_attempt = rounds[-1]['iterations'][-1]
        objections = [f'{role}: {record["result"]["verdict"]} — {record["result"]["rationale"][:300]}' for role, record in last_attempt['stress'].items() if record['result']['verdict'] != 'PASS']
        rationale = 'The idea stopped at the novelty gate after the configured attempt limit or an explicit abandonment response. ' + ' '.join(objections)
    elif project['status'] == 'needs_rubric':
        rationale = 'Formal review is blocked until the exact official conference configuration is retrieved and verified.'
    p = {'slug': project['slug'], 'title': selected_attempt['paper']['result']['title'] if selected_attempt else project['topic'],
         'description': selected_attempt['paper']['result']['summary'] if selected_attempt else 'No complete paper has been produced.',
         'version': selected_attempt['paper_id'] if selected_attempt else 'Unsubmitted', 'stage': 'proposal',
         'mode': project['config']['execution_mode'], 'round': len(rounds), 'maxRounds': project['config']['max_rounds'],
         'status': project['status'], 'recommendation': latest_decision['result']['recommendation'] if latest_decision else 'Undetermined',
         'assessor': 'SAC' if latest_decision and latest_decision['task_id'].endswith('.sac') else 'AC' if latest_decision else 'Unassigned',
         'rationale': rationale,
         'convergence': 'converged' if project['status'] == 'accepted_simulation' else 'not_converged',
         'paperStatus': 'Submitted proposal' if selected_attempt and selected_attempt['paper_id'] in submitted_ids else 'Unsubmitted proposal',
         'sources': source_ids, 'testCase': project['config']['test_mode'], 'workspaceId': project['id'],
         'nextAction': ', '.join(t['id'] for t in pending(project)) or 'Review the final assessment and remaining scientific uncertainty.'}
    for key in ('overview', 'paper', 'process', 'experiments', 'literature'):
        targets['section:' + key] = {'title': key.title(), 'sources': source_ids}
    for r, a in papers:
        targets['paper:' + a['paper_id']] = {'title': a['paper']['result']['title'], 'sources': [a['paper']['source_id']],
                                            'version': a['paper_id'], 'round': r['number'], 'stage': 'proposal'}
    catalog = related_papers(selected_attempt)
    if selected_attempt:
        context = {'version': selected_attempt['paper_id'], 'round': selected_round['number'], 'stage': 'proposal'}
        targets['section:experiments'] = dict(context, title='Final experiment plan', sources=[selected_attempt['paper']['source_id']])
        for experiment in selected_attempt['paper']['result']['experiments']:
            targets['experiment:' + selected_attempt['paper_id'] + ':' + experiment['id']] = dict(
                context, title=experiment['id'] + ' · ' + experiment['hypothesis'], sources=[selected_attempt['paper']['source_id']])
        targets['section:literature'] = dict(context, title='Related papers', sources=list(dict.fromkeys(
            [selected_attempt['literature']['source_id']] + [ref for row in catalog for ref in row['sources']])))
        for row in catalog:
            targets[row['target_id']] = dict(context, title=row['title'], sources=row['sources'])
    rubric = project.get('rubric')
    return {'schema_version': 2, 'project': p, 'sources': sources, 'targets': targets,
            'research': {'conference': project['conference'], 'rounds': rounds,
                         'selected_paper_id': selected_attempt['paper_id'] if selected_attempt else None,
                         'related_papers': catalog,
                         'rubric': {key: value for key, value in rubric.items() if key != 'sources'} if rubric else None,
                         'failures': project['failures'], 'pending': pending(project), 'config': project['config']}}


def render(store, check=False):
    from render_review import compile_html, identity
    data = build_data(store)
    root = store.root
    if not check:
        (root / 'final').mkdir(exist_ok=True)
    manifest_path = root / 'final/review-manifest.json'
    # Reuse annotation identity on regeneration; use the engine ID on first render.
    if manifest_path.exists() or (root / 'final/review.html').exists():
        data['project']['workspaceId'] = identity(root, store.project['slug'])
    payload = compile_html(data)
    p, research = data['project'], data['research']
    output = root / 'final/review.html'
    if not check:
        manifest = {'schema_version': 1, 'slug': p['slug'], 'workspace_id': p['workspaceId'],
                    'head_sha256': store.head, 'html_sha256': hashlib.sha256(payload.encode()).hexdigest(),
                    'sources': {key: {'path': value['path'], 'sha256': value['sha256']} for key, value in data['sources'].items()}}
        selected = next((a for r in research['rounds'] for a in r['iterations'] if a.get('paper_id') == research['selected_paper_id']), None)
        report = f'# {p["title"]}\n\nStatus: **{p["status"]}**. Evidence stage: proposal.\n\n{p["rationale"]}\n\n'
        report += 'This is a simulated review of a research proposal, not experimental validation or a real conference decision. Simulated acceptance indicates competitiveness under the reconstructed process and does not guarantee acceptance.\n\n'
        if p['testCase']:
            report += '**SOFTWARE TEST FIXTURE: agent judgments are synthetic. This is not a live scientific evaluation.**\n\n'
        target = research['conference']
        report += f'Target: {target["name"]} {target["year"]}, {target["track"]}. Execution: {p["mode"]}. Rounds: {p["round"]}/{p["maxRounds"]}.\n\n'
        if selected:
            paper = selected['paper']['result']
            report += f'## Final research contribution\n\n{paper["summary"]}\n\n**Core insight.** {paper["core_insight"]}\n\n**Novelty claim.** {paper["main_novelty"]}\n\n'
            report += '**Expected contributions.** ' + ' '.join(paper['contributions']) + '\n\n'
            report += f'**Method.** {paper["high_level_method"]}\n\n**Decisive validation.** {paper["key_validation"]}\n\n'
            report += '**Prediction status.** All prediction records are hypothetical, not observed measurements.\n\n'
        report += '## Review history\n\n'
        for r in research['rounds']:
            report += f'- {r["id"]}: {r.get("outcome", r["phase"])}; {len(r["reviews"])} initial reviews; rubric `{r["rubric_id"]}`.\n'
        last_decision = next((r for r in reversed(research['rounds']) if r.get('sac')), None)
        if last_decision:
            decision = last_decision['sac']['result']
            report += f'\n## Senior assessment ({last_decision["id"]})\n\n{decision["summary"]}\n\n{decision["ac_reasoning_assessment"]}\n\n'
            report += f'**Unresolved issues.** {decision["unresolved_issues"]}\n\n**Dissent.** {decision["dissent"]}\n\n'
            report += f'**Research next step.** {decision["next_action"]}\n\n'
        report += f'\nNext action: {p["nextAction"]}\n\n[Complete interactive history](review.html)\n'
        if selected:
            atomic(root / 'final/paper.md', paper_markdown(selected['paper']['result'], selected['literature']['result']))
            report += '\n[Complete paper proposal](paper.md)\n'
        atomic(root / 'final/final_report.md', report)
        atomic(manifest_path, json.dumps(manifest, indent=2) + '\n')
        atomic(output, payload)
    return {'output': str(output), 'status': p['status'], 'rounds': len(research['rounds']),
            'sources': len(data['sources']), 'checked_only': check}
