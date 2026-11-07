#!/usr/bin/env python3
"""Render final/review.html from a research workspace and its sourced display index."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import uuid

ASSETS = Path(__file__).resolve().parents[1] / 'assets' / 'review'
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z')
MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 20 * 1024 * 1024
STATUSES = {s.lower(): s for s in ('Open', 'Partially resolved', 'Pending experiment', 'Resolved', 'Rejected with justification')}
SEVERITIES = {s.lower(): s for s in ('Critical', 'Major', 'Moderate', 'Minor')}


class ReviewError(ValueError):
    """A review input that cannot be represented faithfully."""


def fail(message):
    raise ReviewError(message)


def text(value, label, default=None):
    if value is None and default is not None:
        return default
    if not isinstance(value, str) or not value.strip():
        fail(f'{label} must be a nonempty string')
    return value.strip()


def identifier(value, label):
    if not isinstance(value, str) or not ID.fullmatch(value):
        fail(f'{label} must be a stable identifier of 1-128 letters, digits, dots, hyphens, colons, or underscores (starting with a letter or digit)')
    return value


def number(value, label, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        fail(f'{label} must be an integer from {minimum} to {maximum}')
    return value


def mapping(value, label):
    if not isinstance(value, dict):
        fail(f'{label} must be an object')
    return value


def array(value, label):
    if not isinstance(value, list):
        fail(f'{label} must be an array')
    return value


def inside(root, relative, must_exist=True):
    if not isinstance(relative, str) or '\\' in relative or ':' in relative:
        fail(f'Use a workspace-relative path with forward slashes: {relative!r}')
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        fail(f'Path must stay inside the research workspace: {relative}')
    resolved = (root / Path(*path.parts)).resolve()
    if not resolved.is_relative_to(root):
        fail(f'Path escapes the research workspace: {relative}')
    if must_exist and not resolved.is_file():
        fail(f'Missing source artifact: {relative}')
    return resolved


def read_json(path, label):
    try:
        return mapping(json.loads(path.read_text(encoding='utf-8')), label)
    except (json.JSONDecodeError, UnicodeError) as error:
        fail(f'Cannot read {label}: {error}')


def source_refs(value, sources, label):
    refs = array(value, label)
    if not refs:
        fail(f'{label} needs at least one source')
    for ref in refs:
        if not isinstance(ref, str) or ref not in sources:
            fail(f'{label} references an unknown source: {ref!r}')
    return list(dict.fromkeys(refs))


def load_workspace(root):
    state = read_json(inside(root, 'state.json'), 'state.json')
    index_path = inside(root, 'final/review-data.json')
    index = read_json(index_path, 'final/review-data.json')
    if type(index.get('schema_version')) is not int or index['schema_version'] != 1:
        fail('Unsupported review-data schema_version; expected 1')
    slug = text(state.get('slug'), 'state.slug')
    topic = text(state.get('topic'), 'state.topic')
    stage = state.get('review_stage')
    if stage not in ('proposal', 'implementation', 'paper'):
        fail('state.review_stage must be proposal, implementation, or paper')
    mode = state.get('execution_mode')
    if mode not in ('independent', 'external_review', 'single_agent', 'unselected'):
        fail('state.execution_mode must be independent, external_review, single_agent, or unselected')
    maximum = number(state.get('max_rounds'), 'state.max_rounds', 1, 100)
    current = number(state.get('current_round'), 'state.current_round', 0, maximum)
    last = state.get('last_completed_round')
    if last is not None:
        number(last, 'state.last_completed_round', 0, current)
    sources_config = dict(mapping(index.get('sources', {}), 'sources'))
    automatic = {'state': 'state.json', 'report': 'final/final_report.md'}
    if (root / 'issue_tracker.md').is_file():
        automatic['issues'] = 'issue_tracker.md'
    for key, path in automatic.items():
        if key in sources_config and sources_config[key] != path:
            fail(f'Source ID {key!r} is reserved for {path}')
        sources_config[key] = path
    display_paths = {(root / relative).resolve() for relative in ('final/review.html', 'final/review-data.json', 'final/review-manifest.json')}
    sources, total = {}, 0
    for key, relative in sources_config.items():
        identifier(key, 'source ID')
        source_path = inside(root, relative)
        if source_path in display_paths:
            fail(f'Display files cannot be used as research evidence: {relative}')
        size = source_path.stat().st_size
        if size > MAX_SOURCE_BYTES:
            fail(f'Source exceeds 2 MiB: {relative}; reference a bounded text artifact instead')
        raw = source_path.read_bytes()
        total += len(raw)
        if total > MAX_TOTAL_BYTES:
            fail('Bundled sources exceed 20 MiB; reference a bounded evidence set')
        try:
            contents = raw.decode('utf-8')
        except UnicodeError:
            fail(f'Source is not UTF-8 text: {relative}; reference its text evidence record instead')
        sources[key] = {'id': key, 'path': relative, 'title': PurePosixPath(relative).name,
                        'text': contents, 'sha256': hashlib.sha256(raw).hexdigest()}
    overview = mapping(index.get('overview'), 'overview')
    recommendation = overview.get('recommendation', 'Undetermined')
    if recommendation not in ('Proceed', 'Revise', 'Restart', 'Kill', 'Undetermined'):
        fail('overview.recommendation must be Proceed, Revise, Restart, Kill, or Undetermined')
    if state.get('recommendation') and state['recommendation'] != recommendation:
        fail('Recommendation conflicts with state.json; reconcile the actual assessment before rendering')
    assessor = overview.get('assessor', 'Author')
    if assessor not in ('Author', 'AC', 'SAC', 'Unassigned'):
        fail('overview.assessor must be Author, AC, SAC, or Unassigned')
    if assessor in ('AC', 'SAC') and mode not in ('independent', 'external_review'):
        fail('A chair assessment requires independent or external-review provenance; self-review cannot invent a chair')
    summary_sources = source_refs(overview.get('sources'), sources, 'overview.sources')
    project = {'slug': slug, 'title': text(overview.get('title'), 'overview.title', topic),
               'description': text(overview.get('description'), 'overview.description'),
               'version': text(state.get('proposal_version'), 'state.proposal_version', 'Unversioned'),
               'stage': stage, 'mode': mode, 'round': current, 'maxRounds': maximum,
               'lastCompletedRound': last, 'convergence': text(state.get('convergence'), 'state.convergence', 'not_assessed'),
               'status': text(state.get('status'), 'state.status', 'Not recorded'),
               'recommendation': recommendation, 'assessor': assessor,
               'rationale': text(overview.get('rationale'), 'overview.rationale'),
               'nextAction': text(overview.get('next_action', state.get('next_action')), 'overview.next_action'),
               'sources': summary_sources, 'testCase': index.get('test_case', False)}
    if type(project['testCase']) is not bool:
        fail('test_case must be a boolean')
    targets = {
        'section:decision': {'title': 'Research recommendation', 'sources': summary_sources},
        'section:overview': {'title': 'Research overview', 'sources': summary_sources},
        'section:reviews': {'title': 'Review history', 'sources': ['report']},
        'section:experiments': {'title': 'Experiment plan and evidence', 'sources': ['report']},
        'section:plan': {'title': 'Final research plan', 'sources': ['report']},
    }
    issues, aliases_seen = [], set()
    seen = set()
    for value in array(index.get('issues', []), 'issues'):
        item = dict(mapping(value, 'issue'))
        key = identifier(item.get('id'), 'issue.id')
        if key in seen:
            fail(f'Duplicate issue ID: {key}')
        seen.add(key)
        severity = SEVERITIES.get(str(item.get('severity', '')).lower())
        status = STATUSES.get(str(item.get('status', '')).lower())
        if not severity or not status:
            fail(f'Issue {key} needs a canonical severity and status; see references/review-report.md')
        aliases = item.get('aliases', [key])
        array(aliases, f'{key}.aliases')
        if key not in aliases:
            fail(f'{key}.aliases must retain the canonical issue ID')
        for alias in aliases:
            identifier(alias, 'original issue ID')
            if alias in aliases_seen:
                fail(f'Original issue ID belongs to more than one group: {alias}')
            aliases_seen.add(alias)
        discussion = []
        for entry in array(item.get('discussion', []), f'{key}.discussion'):
            entry = dict(mapping(entry, 'discussion entry'))
            source = source_refs([entry.get('source')], sources, 'discussion.source')[0]
            discussion.append({'author': text(entry.get('author'), 'discussion.author'),
                               'phase': text(entry.get('phase'), 'discussion.phase'),
                               'text': text(entry.get('text'), 'discussion.text'), 'source': source,
                               'round': number(entry.get('round', item.get('round', 0)), 'discussion.round', 0, maximum)})
        refs = item.get('sources') or list(dict.fromkeys([x['source'] for x in discussion] + (['issues'] if 'issues' in sources else [])))
        refs = source_refs(refs, sources, f'{key}.sources')
        normalized = {'id': key, 'title': text(item.get('title'), 'issue.title'), 'severity': severity,
                      'status': status, 'round': number(item.get('round', 0), 'issue.round', 0, maximum),
                      'aliases': aliases, 'criterion': text(item.get('criterion'), 'issue.criterion', 'Not recorded'),
                      'discussion': discussion, 'sources': refs}
        issues.append(normalized)
        targets['issue:' + key] = {'title': normalized['title'], 'sources': refs}
    claims, seen = [], set()
    for item in array(index.get('claims', []), 'claims'):
        mapping(item, 'claim')
        key = identifier(item.get('id'), 'claim.id')
        if key in seen:
            fail(f'Duplicate claim ID: {key}')
        seen.add(key)
        claim = {field: text(item.get(field), 'claim.' + field) for field in ('title', 'text', 'status')}
        claim.update(id=key, sources=source_refs(item.get('sources'), sources, f'{key}.sources'))
        claims.append(claim)
        targets['claim:' + key] = {'title': claim['title'], 'sources': claim['sources']}
    reviewers, seen = [], set()
    for item in array(index.get('reviewers', []), 'reviewers'):
        mapping(item, 'reviewer')
        key = identifier(item.get('id'), 'reviewer.id')
        round_id = number(item.get('round'), 'reviewer.round', 1, maximum)
        if (key, round_id) in seen:
            fail(f'Duplicate reviewer/round: {key}, {round_id}')
        seen.add((key, round_id))
        reviewer = {'id': key, 'round': round_id,
                    'focus': text(item.get('focus'), 'reviewer.focus', 'Not recorded'),
                    'stage': text(item.get('stage'), 'reviewer.stage', 'Not recorded'),
                    'rubric': text(item.get('rubric'), 'reviewer.rubric', 'Not recorded'),
                    'confidence': text(item.get('confidence'), 'reviewer.confidence', 'Not recorded')}
        for phase in ('initial', 'final'):
            score = item.get(phase)
            if score is None:
                reviewer[phase] = None
            else:
                mapping(score, 'reviewer.' + phase)
                if type(score.get('score')) not in (str, int, float) or not str(score['score']).strip():
                    fail('Reviewer scores must be their recorded string or number; use null for missing reviews')
                reviewer[phase] = {'score': str(score['score']), 'source': source_refs([score.get('source')], sources, 'reviewer source')[0]}
        reviewers.append(reviewer)
    if reviewers and mode not in ('independent', 'external_review'):
        fail('Recorded independent reviewers require independent or external_review mode')
    timeline, seen = [], set()
    for item in array(index.get('timeline', []), 'timeline'):
        mapping(item, 'timeline entry')
        key = identifier(item.get('id'), 'timeline.id')
        if key in seen:
            fail(f'Duplicate timeline ID: {key}')
        seen.add(key)
        row = {field: text(item.get(field), 'timeline.' + field) for field in ('label', 'role', 'summary')}
        row.update(id=key, round=number(item.get('round', 0), 'timeline.round', 0, maximum),
                   source=source_refs([item.get('source')], sources, 'timeline.source')[0])
        timeline.append(row)
    experiments, seen = [], set()
    for item in array(index.get('experiments', []), 'experiments'):
        mapping(item, 'experiment')
        key = identifier(item.get('id'), 'experiment.id')
        if key in seen:
            fail(f'Duplicate experiment ID: {key}')
        seen.add(key)
        row = {field: text(item.get(field), 'experiment.' + field) for field in ('title', 'kind', 'status', 'summary')}
        row.update(id=key, source=source_refs([item.get('source')], sources, 'experiment.source')[0])
        row['sources'] = source_refs([row['source']] + array(item.get('sources', []), 'experiment.sources'), sources, 'experiment.sources')
        for field in ('hypothesis', 'setup', 'data', 'baselines', 'metrics', 'controls',
                      'success', 'failure', 'resources', 'result'):
            row[field] = text(item[field], 'experiment.' + field) if field in item else None
        experiments.append(row)
        targets['experiment:' + key] = {'title': row['title'], 'sources': row['sources']}
    rounds, seen = [], set()
    for item in array(index.get('rounds', []), 'rounds'):
        mapping(item, 'round snapshot')
        n = number(item.get('round'), 'rounds.round', 1, current)
        if n in seen:
            fail(f'Duplicate round snapshot: {n}')
        seen.add(n)
        row = {'round': n, 'version': text(item.get('version'), 'rounds.version', 'Not recorded'),
               'status': text(item.get('status'), 'rounds.status', 'Not recorded'),
               'stage': text(item.get('stage'), 'rounds.stage', 'Not recorded')}
        if row['stage'] not in ('proposal', 'implementation', 'paper', 'Not recorded'):
            fail('rounds.stage must be proposal, implementation, or paper when recorded')
        refs = []
        for field in ('idea', 'changes', 'outcome'):
            value = item.get(field)
            row[field] = None
            if value is not None:
                mapping(value, 'rounds.' + field)
                row[field] = {'text': text(value.get('text'), 'rounds.' + field + '.text'),
                              'sources': source_refs(value.get('sources'), sources, 'rounds.' + field + '.sources')}
                refs.extend(row[field]['sources'])
        if not refs:
            fail(f'Round {n} needs at least one sourced idea, change, or outcome')
        targets['round:' + str(n)] = {'title': f'Round {n} idea and review',
                                     'sources': list(dict.fromkeys(refs)),
                                     'round': n, 'version': row['version'], 'stage': row['stage']}
        rounds.append(row)
    rounds.sort(key=lambda row: row['round'])
    plan_input = mapping(index.get('plan', {}), 'plan')
    plan = {}
    experiment_ids = {row['id'] for row in experiments}
    for collection, fields in {'idea': ('text',), 'story': ('text',),
                               'paper': ('goal', 'design', 'evidence'),
                               'roadmap': ('task', 'dependencies', 'artifact', 'estimate')}.items():
        plan[collection], seen = [], set()
        for item in array(plan_input.get(collection, []), 'plan.' + collection):
            mapping(item, 'plan.' + collection + ' entry')
            key = identifier(item.get('id'), 'plan.' + collection + '.id')
            if key in seen:
                fail(f'Duplicate plan.{collection} ID: {key}')
            seen.add(key)
            row = {'id': key, 'title': text(item.get('title'), 'plan.' + collection + '.title'),
                   'sources': source_refs(item.get('sources'), sources, 'plan.' + collection + '.sources')}
            for field in fields:
                row[field] = text(item.get(field), 'plan.' + collection + '.' + field)
            if collection == 'paper':
                refs = array(item.get('experiments', []), 'plan.paper.experiments')
                if any(not isinstance(ref, str) or ref not in experiment_ids for ref in refs):
                    fail('plan.paper.experiments references an unknown experiment ID')
                row['experiments'] = list(dict.fromkeys(refs))
            plan[collection].append(row)
            targets['plan:' + collection + ':' + key] = {'title': row['title'], 'sources': row['sources']}
    targets['section:reviews']['sources'] = list(dict.fromkeys([x['source'] for x in timeline] + ['report']))
    targets['section:experiments']['sources'] = list(dict.fromkeys([ref for x in experiments for ref in x['sources']] + ['report']))
    targets['section:plan']['sources'] = list(dict.fromkeys(
        [ref for rows in plan.values() for row in rows for ref in row['sources']]
        + [ref for x in experiments for ref in x['sources']] + ['report']))
    return {'schema_version': 1, 'project': project, 'issues': issues, 'claims': claims,
            'reviewers': reviewers, 'timeline': timeline, 'experiments': experiments,
            'rounds': rounds, 'plan': plan, 'sources': sources, 'targets': targets}, hashlib.sha256(index_path.read_bytes()).hexdigest()


def identity(root, slug):
    manifest_path = inside(root, 'final/review-manifest.json', must_exist=False)
    if manifest_path.exists():
        manifest = read_json(manifest_path, 'review-manifest.json')
        if type(manifest.get('schema_version')) is not int or manifest['schema_version'] != 1 or manifest.get('slug') != slug:
            fail('Existing review manifest belongs to a different or unsupported workspace; preserve annotations before repairing it')
        value = manifest.get('workspace_id')
    else:
        html_path = inside(root, 'final/review.html', must_exist=False)
        if html_path.exists():
            match = re.search(r'<script id="review-data" type="application/json">(.*?)</script>', html_path.read_text(encoding='utf-8'), re.S)
            try:
                prior = json.loads(match.group(1)) if match else {}
                if prior.get('project', {}).get('slug') != slug:
                    fail('Existing review.html is not a generated report for this workspace; preserve it before rendering')
                value = prior['project']['workspaceId']
            except (KeyError, TypeError, json.JSONDecodeError):
                fail('Cannot recover the existing report identity; restore review-manifest.json before regenerating')
        else:
            value = str(uuid.uuid4())
    try:
        uuid.UUID(value)
    except (ValueError, TypeError, AttributeError):
        fail('Invalid review workspace_id; restore the manifest to retain annotation identity')
    return value


def compile_html(data):
    template = (ASSETS / 'template.html').read_text(encoding='utf-8')
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    payload = payload.replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    replacements = {
        '<!-- REVIEW_CSS -->': '<style>' + (ASSETS / 'styles.css').read_text(encoding='utf-8') + '</style>',
        '<!-- REVIEW_DATA -->': '<script id="review-data" type="application/json">' + payload + '</script>',
        '<!-- REVIEW_RUNTIME -->': '<script>' + (ASSETS / 'runtime.js').read_text(encoding='utf-8') + '</script>',
        '<!-- REVIEW_APP -->': '<script>' + (ASSETS / 'app.js').read_text(encoding='utf-8') + '</script>',
    }
    for marker, replacement in replacements.items():
        if template.count(marker) != 1:
            fail(f'Review template has an invalid embed marker: {marker}')
        template = template.replace(marker, replacement)
    return template


def atomic_write(path, contents):
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=path.parent, delete=False) as handle:
            name = handle.name
            handle.write(contents)
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def render(root, check=False):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        fail('Research workspace does not exist')
    data, input_hash = load_workspace(root)
    workspace_id = identity(root, data['project']['slug'])
    data['project']['workspaceId'] = workspace_id
    generated_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    data['project']['generatedAt'] = generated_at
    html = compile_html(data)
    output = inside(root, 'final/review.html', must_exist=False)
    if not check:
        manifest = {'schema_version': 1, 'workspace_id': workspace_id, 'slug': data['project']['slug'],
                    'generated_at': generated_at, 'input_sha256': input_hash,
                    'html_sha256': hashlib.sha256(html.encode()).hexdigest(),
                    'sources': {key: {'path': source['path'], 'sha256': source['sha256']} for key, source in data['sources'].items()}}
        atomic_write(inside(root, 'final/review-manifest.json', must_exist=False), json.dumps(manifest, indent=2) + '\n')
        atomic_write(output, html)
    return {'output': str(output), 'checked_only': check, 'sources': len(data['sources']),
            'issues': len(data['issues']), 'workspace_id': workspace_id}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workspace', type=Path, help='research/<slug>, not the installed skill directory')
    parser.add_argument('--check', action='store_true', help='validate inputs and compile without writing files')
    args = parser.parse_args()
    try:
        result = render(args.workspace, args.check)
    except (ReviewError, OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
