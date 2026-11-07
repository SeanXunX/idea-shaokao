"""Scientific artifact contracts; scores are supplied only by a verified rubric."""
import hashlib
import json
import math
import re
from urllib.parse import urlparse


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def obj(value, name):
    require(isinstance(value, dict), f'{name} must be an object')
    return value


def text(value, name):
    require(isinstance(value, str) and bool(value.strip()), f'{name} must be nonempty text')
    return value


def items(value, name, minimum=0):
    require(isinstance(value, list) and len(value) >= minimum, f'{name} needs at least {minimum} entries')
    return value


def fields(value, names, name):
    obj(value, name)
    for key in names:
        text(value.get(key), f'{name}.{key}')
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def url(value, name):
    text(value, name)
    parsed = urlparse(value)
    require(parsed.scheme == 'https' and bool(parsed.hostname), f'{name} must be an HTTPS primary-source URL')
    return value


def unique(rows, name):
    ids = [text(obj(row, name).get('id'), name + '.id') for row in rows]
    require(len(ids) == len(set(ids)), f'{name} has duplicate IDs')
    return ids


INSIGHT = ('important_problem', 'fundamental_limitation', 'nonobvious_observation',
           'key_insight', 'falsifiable_hypothesis', 'novel_mechanism',
           'scientific_contribution', 'validation', 'closest_work_difference', 'failure_conditions')
SECTIONS = ('abstract', 'introduction', 'related_work', 'problem_formulation',
            'insight_hypothesis', 'proposed_method', 'technical_design', 'theoretical_analysis',
            'experimental_design', 'expected_results', 'expected_contributions', 'limitations', 'conclusion')
SECTION_TITLES = ('Abstract', 'Introduction', 'Related Work', 'Problem Formulation',
                  'Key Insight and Research Hypothesis', 'Proposed Method', 'Technical Design',
                  'Theoretical Analysis', 'Experimental Design', 'Expected Results and Quantitative Predictions',
                  'Expected Contributions', 'Limitations and Risks', 'Conclusion')
COVERAGE = ('foundational', 'recent_conference', 'journal', 'preprint', 'concurrent', 'closest', 'adjacent')
READINESS = ('defensible_novelty', 'meaningful_insight', 'venue_significance', 'technical_soundness',
             'falsifiable_experiments', 'plausible_predictions', 'no_fatal_concerns')
STRESS_ROLES = ('prior_art', 'conceptual', 'significance')
REVIEW_ROLES = ('novelty', 'soundness', 'experiments', 'fit')


def literature(data):
    fields(data, ('summary', 'cutoff'), 'literature')
    searches = items(data.get('searches'), 'searches', 1)
    coverage = set()
    for row in searches:
        fields(row, ('id', 'query', 'provider', 'at', 'status', 'coverage'), 'search')
        require(row['coverage'] in COVERAGE, 'unknown literature search coverage')
        require(row['status'] in ('ok', 'failed', 'unavailable'), 'unknown search status')
        if row['status'] != 'ok':
            text(row.get('error'), 'search.error')
        coverage.add(row['coverage'])
    require(coverage == set(COVERAGE), 'record every literature category, including unsuccessful searches')
    papers = items(data.get('papers'), 'papers', 1)
    paper_ids = unique(papers, 'papers')
    for row in papers:
        paper_evidence(row)
    closest = items(data.get('closest_ids'), 'closest_ids', 1)
    require(set(closest) <= set(paper_ids), 'unknown closest-work evidence')
    items(data.get('gaps'), 'literature.gaps', 1)
    return data


def paper_evidence(row):
    fields(row, ('id', 'title', 'authors', 'version', 'retrieved_at', 'problem', 'insight', 'methodology', 'assumptions', 'results',
                 'limitations', 'relationship', 'contribution_difference', 'locator', 'access_depth'), 'paper evidence')
    url(row.get('url'), 'paper.url')
    require(type(row.get('year')) is int and row['year'] > 0, 'paper publication/preprint year must be recorded')
    require(row['access_depth'] in ('full_text', 'abstract', 'metadata'), 'invalid paper access depth')
    require(row.get('knowledge_status') in ('established', 'underexplored', 'gap', 'hypothesis'), 'classify literature knowledge status')
    return row


def idea(data, evidence):
    fields(data, ('title', 'selection_rationale', 'level_rationale', 'venue_fit'), 'idea')
    fields(data.get('insight_chain'), INSIGHT, 'insight_chain')
    require(type(data.get('contribution_level')) is int and 1 <= data['contribution_level'] <= 4, 'contribution_level must be 1–4')
    if data['contribution_level'] < 3:
        text(data.get('incremental_justification'), 'incremental work needs venue-calibrated justification')
    candidates = items(data.get('alternatives'), 'alternatives', 2)
    for row in candidates:
        fields(row, ('title', 'insight', 'strongest_objection', 'selection_reason'), 'alternative')
    claims = items(data.get('novelty_claims'), 'novelty_claims', 1)
    unique(claims, 'novelty_claims')
    known = {p['id'] for p in evidence['papers']}
    for claim in claims:
        fields(claim, ('claim', 'difference', 'uncertainty'), 'novelty claim')
        require(set(items(claim.get('evidence_ids'), 'claim.evidence_ids', 1)) <= known, 'novelty claim references unknown literature')
    return data


def paper(data, research, evidence):
    fields(data, ('title', 'summary', 'core_insight', 'main_novelty', 'high_level_method', 'key_validation'), 'paper')
    contributions = items(data.get('contributions'), 'contributions', 1)
    for entry in contributions:
        text(entry, 'contribution')
    sections = obj(data.get('sections'), 'sections')
    for key in SECTIONS:
        prose = text(sections.get(key), 'sections.' + key)
        # Detect empty headings/outlines without pretending to judge academic merit.
        require(len(prose.split()) >= 25, f'{key} needs developed prose, not a section placeholder')
        lines = [line for line in prose.splitlines() if line.strip()]
        require(any(not re.match(r'^\s*(?:[-*#]|\d+[.)])\s', line) for line in lines), f'{key} cannot contain only outline bullets')
    experiments = items(data.get('experiments'), 'experiments', 1)
    experiment_ids = unique(experiments, 'experiments')
    for row in experiments:
        fields(row, ('hypothesis', 'data', 'baselines', 'metrics', 'protocol', 'ablations',
                     'robustness', 'statistics', 'reproducibility', 'falsification', 'resources'), 'experiment')
    predictions = items(data.get('predictions'), 'predictions', 1)
    unique(predictions, 'predictions')
    for row in predictions:
        fields(row, ('experiment_id', 'metric', 'baseline', 'assumptions', 'rationale', 'failure_condition'), 'prediction')
        require(row['experiment_id'] in experiment_ids, 'prediction references unknown experiment')
        require(row.get('kind') == 'hypothetical', 'predictions must be labeled hypothetical, never observed')
        if row.get('estimate') is None:
            text(row.get('nonquantitative_reason'), 'explain why a quantitative prediction is unreasonable')
        else:
            interval = items(row['estimate'], 'prediction.estimate', 2)
            require(len(interval) == 2 and all(type(x) in (int, float) and math.isfinite(x) for x in interval)
                    and interval[0] <= interval[1], 'prediction estimate must be a finite ordered range')
            text(row.get('unit'), 'prediction.unit')
        known = {p['id'] for p in evidence['papers']}
        require(set(items(row.get('evidence_ids'), 'prediction.evidence_ids')) <= known, 'prediction cites unknown evidence')
        if not row['evidence_ids']:
            text(row.get('unsupported_estimate_warning'), 'unsupported predictions need an explicit warning')
    require(set(experiment_ids) <= {p['experiment_id'] for p in predictions}, 'every experiment needs an expected outcome or justified nonquantitative prediction')
    fields(data.get('prediction_audit'), ('plausibility', 'calibration_basis', 'alternative_outcomes'), 'prediction_audit')
    return data


def concerns(data, evidence_ids=None):
    rows = items(data, 'concerns')
    unique(rows, 'concerns')
    for row in rows:
        fields(row, ('claim', 'evidence', 'resolution_criterion'), 'concern')
        require(row.get('severity') in ('critical', 'major', 'moderate', 'minor'), 'unknown concern severity')
        require(type(row.get('fundamental')) is bool, 'concern.fundamental must be boolean')
    return rows


def stress(data, role):
    fields(data, ('claim_summary', 'claimed_novelty', 'closest_work', 'overlap_evidence',
                  'insight_weaknesses', 'significance_weaknesses', 'rejection_arguments', 'required_evidence', 'rationale'), 'novelty report')
    concerns(data.get('concerns'))
    discovered = items(data.get('discovered_papers', []), 'discovered_papers')
    unique(discovered, 'discovered_papers')
    for row in discovered:
        paper_evidence(row)
    require(data.get('verdict') in ('PASS', 'CONDITIONAL PASS', 'FAIL'), 'unknown novelty verdict')
    require(not (data['verdict'] == 'PASS' and any(c['severity'] == 'critical' for c in data['concerns'])), 'PASS cannot retain a critical novelty concern')
    if role == 'prior_art':
        for row in items(data.get('comparison_table'), 'prior-art comparison_table', 1):
            fields(row, ('paper_id', 'overlapping_claim', 'mechanism_comparison', 'precise_difference', 'evidence_locator'), 'prior-art comparison')
    return data


def responses(data, required, limit=None):
    fields(data, ('summary',), 'author response')
    rows = items(data.get('responses'), 'responses')
    unique_ids = [row.get('concern_id') for row in rows]
    require(len(set(unique_ids)) == len(unique_ids), 'duplicate response concern IDs')
    require(set(required) <= set(unique_ids), 'every major/critical concern needs an individual author response')
    for row in rows:
        fields(row, ('concern_id', 'response', 'evidence', 'change', 'remaining_uncertainty'), 'response')
        require(row.get('action') in ('clarify', 'evidence', 'mechanism', 'hypothesis', 'scope', 'abandon', 'acknowledge'), 'unknown research response action')
        if required.get(row['concern_id'], {}).get('fundamental'):
            require(row['action'] in ('evidence', 'mechanism', 'hypothesis', 'scope', 'abandon'), 'a fundamental novelty concern cannot be answered by prose or extra experiments alone')
    if limit:
        require(len(response_text(data)) <= limit, f'author response exceeds the official {limit}-character limit')
    return data


def response_text(data):
    return data['summary'] + '\n' + '\n'.join('\n'.join(str(v) for v in row.values()) for row in data.get('responses', []))


def review(data, rubric, phase='initial'):
    from .conference import validate_answers
    validate_answers(rubric, data.get('fields'), phase)
    justifications = obj(data.get('score_justifications'), 'score_justifications')
    for field in rubric['fields']:
        if field['kind'] in ('choice', 'multi_choice') and field['id'] in data['fields']:
            text(justifications.get(field['id']), 'evidence-based justification for ' + field['id'])
    concerns(data.get('concerns'))
    text(data.get('assessment'), 'assessment')
    if phase == 'final':
        fields(data, ('change_reason',), 'reviewer reassessment')
        obj(data.get('concern_status'), 'concern_status')
        for key, row in data['concern_status'].items():
            fields(row, ('evidence', 'reason'), 'concern disposition')
            require(row.get('status') in ('resolved', 'open', 'pending'), 'unknown concern disposition')
    return data


def chair(data, role, known_concerns, rubric):
    fields(data, ('summary', 'agreement_analysis', 'rebuttal_assessment', 'unresolved_issues',
                  'contribution_assessment', 'rationale', 'recommendation'), role)
    require(data.get('case') in ('strong_acceptance', 'borderline', 'addressable_rejection', 'fundamental_failure'), 'invalid round outcome case')
    readiness = obj(data.get('readiness'), 'readiness')
    for key in READINESS:
        row = fields(readiness.get(key), ('evidence',), 'readiness.' + key)
        require(type(row.get('met')) is bool, 'readiness criterion needs a boolean judgment')
    new_concerns = concerns(data.get('concerns', []))
    known_concerns = dict(known_concerns)
    for row in new_concerns:
        require(row['id'] not in known_concerns or known_concerns[row['id']] == row, 'chair cannot silently rewrite an existing concern')
        known_concerns[row['id']] = row
    if data['case'] != 'strong_acceptance':
        require(bool(known_concerns), 'an unfavorable chair assessment needs a structured, traceable concern')
    dispositions = obj(data.get('concern_status'), 'chair.concern_status')
    require(set(dispositions) == set(known_concerns), 'chair must adjudicate every concern, including dissent')
    for row in dispositions.values():
        fields(row, ('reason', 'evidence'), 'chair disposition')
        require(row.get('status') in ('resolved', 'open', 'pending'), 'invalid chair disposition')
    require(data.get('decision_scope') in ('official_simulation', 'internal_simulation'), 'chair scope must be explicit')
    options = rubric['procedures'][role].get('decision_options', [])
    if data['decision_scope'] == 'official_simulation':
        require(bool(options) and data['recommendation'] in options, 'chair decision is not an official option; label internal when unavailable')
    internal_options = rubric['procedures'][role].get('internal_decision_options', [])
    if data['decision_scope'] == 'internal_simulation':
        require(data['recommendation'] in internal_options, 'unknown internal chair decision option')
    if data['case'] == 'strong_acceptance':
        require(data['recommendation'] in rubric['procedures'][role].get('acceptance_options', []), 'strong acceptance case conflicts with the chair recommendation')
    if role == 'sac':
        fields(data, ('ac_reasoning_assessment', 'score_text_consistency', 'dissent', 'next_action'), 'sac')
    return data
