"""Deterministic SOFTWARE fixtures; never a scientific evaluation or model output."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scripts'))
from shaokao import contracts as C
from shaokao.conference import extract_form
from shaokao.engine import Store, current, envelope, pending, all_concerns


def official_bundle():
    return json.loads(gzip.decompress((REPO / 'tests/fixtures/icml2026-official-sources.json.gz').read_bytes()))


def official_rubric():
    bundle = official_bundle()
    spec = json.loads((REPO / 'examples/icml2026-rubric-spec.json').read_text())
    rubric = dict(bundle, **spec)
    extraction = spec['form_extraction']
    rubric['fields'] = extract_form(bundle, extraction['source_id'], extraction['start'], extraction['end'])
    return rubric


def create(root, **config):
    options = dict(test_mode=True, acceptance_rounds=1, reviewers=3, max_rounds=2)
    options.update(config)
    store = Store.create(root, 'SOFTWARE FIXTURE: falsifiable cache adaptation',
        {'name': 'ICML', 'year': 2026, 'track': 'Main Track'}, options)
    store.install_rubric(official_rubric())
    return store


PROSE = ('This software fixture proposes a falsifiable investigation of workload adaptation under a fixed resource budget. '
         'The hypothesis concerns generalization across held-out workload changes, rather than an observed improvement. '
         'Equal tuning budgets, matched capacity, and independent workload seeds would separate the proposed mechanism '
         'from simpler explanations. No measurements have been collected and the numerical ranges below are hypothetical. ')


def result_for(packet, *, round_outcome=None, stress_verdict='PASS'):
    task, context = packet['task'], packet['context']
    phase, role, n = task['stage'], task['role'], int(task['round'].split('-')[1])
    if phase == 'literature':
        return {'summary': PROSE, 'cutoff': '2026-11-07',
            'searches': [dict(id='search-'+key, query='software fixture recorded search '+key, provider='synthetic software adapter',
                at='2026-11-07T00:00:00Z', status='ok', coverage=key) for key in C.COVERAGE],
            'papers': [dict(id='P-LRU', title='The Working Set Model for Program Behavior',authors='Peter J. Denning',year=1968,version='Bibliographic software fixture; interpretation is synthetic.',retrieved_at='2026-11-07T00:00:00Z',
                url='https://dl.acm.org/doi/10.1145/363095.363141',
                **{key:'Software fixture interpretation, not a verified literature conclusion: '+key for key in ('problem','insight','methodology','assumptions','results','limitations','relationship','contribution_difference','locator')},
                access_depth='full_text', knowledge_status='established')],
            'closest_ids': ['P-LRU'], 'gaps': ['Synthetic gap used exclusively to test the software workflow.']}
    if phase == 'idea':
        return dict(title=f'Software Fixture: Adaptation with Identifiable Mechanisms v{n}', selection_rationale=PROSE,
            contribution_level=3, level_rationale='Synthetic mechanism-level claim for software validation.', venue_fit='Synthetic significance assessment.',
            insight_chain={key:PROSE for key in C.INSIGHT}, alternatives=[dict(title=f'Alternative {i}',insight=PROSE,strongest_objection=PROSE,selection_reason=PROSE) for i in range(2)],
            novelty_claims=[dict(id='H01',claim='Untested mechanism hypothesis.',difference='Software fixture difference.',uncertainty='Not a live novelty claim.',evidence_ids=['P-LRU'])])
    if phase == 'paper':
        return dict(title=f'Software Fixture: Identifying Adaptive Cache Mechanisms v{n}',summary=PROSE,core_insight='Test adaptation independently of resource changes.',
            main_novelty='Synthetic software-test claim; no actual novelty is asserted.',high_level_method='Control capacity, tune equally, hold out workload transitions.',
            key_validation='Mechanism removal under matched workloads.',contributions=['Falsifiable mechanism hypothesis; software fixture only.'],
            sections={key:PROSE+('The revised design adds a distinct held-out workload family.' if n>1 else '')+(r' The model uses \(H_0\) as the null hypothesis.'+'\n\n$$\n'+r'L(\theta) = \sum_{i=1}^{n} \ell_i(\theta)'+'\n$$' if key=='technical_design' else '') for key in C.SECTIONS},
            experiments=[dict(id='E01', **{key:PROSE for key in ('hypothesis','data','baselines','metrics','protocol','ablations','robustness','statistics','reproducibility','falsification','resources')})],
            predictions=[dict(id='P01',kind='hypothetical',experiment_id='E01',metric='relative miss-rate change',baseline='Estimated 20%; software test number, not a measurement.',estimate=[-2,5],unit='percentage points',assumptions='Workload changes remain identifiable.',rationale='Illustrative range for testing uncertainty display.',failure_condition='No held-out benefit after matching resources.',evidence_ids=[],unsupported_estimate_warning='Unsupported synthetic estimate; not literature-calibrated.')],
            prediction_audit=dict(plausibility='Not a scientific assessment.',calibration_basis='Synthetic software fixture.',alternative_outcomes='The mechanism may provide no benefit.'))
    if phase == 'stress':
        concern_id=f'{task["id"]}.C01'
        return dict(**{key:PROSE for key in ('claim_summary','claimed_novelty','closest_work','overlap_evidence','insight_weaknesses','significance_weaknesses','rejection_arguments','required_evidence','rationale')},
            verdict=stress_verdict,concerns=[] if stress_verdict=='PASS' else [dict(id=concern_id,severity='critical',fundamental=True,claim='The claimed mechanism overlaps a known formulation.',evidence='Synthetic prior-art overlap case.',resolution_criterion='Identify and defend a distinct scientific insight.')],
            comparison_table=[dict(paper_id='P-LRU',overlapping_claim='Software fixture overlap check.',mechanism_comparison=PROSE,precise_difference=PROSE,evidence_locator='Fixture locator; no verified novelty claim.')])
    if phase in ('novelty_response','rebuttal') or phase=='exchange' and role=='author':
        reports = dict(context.get('novelty_reports') or context.get('initial_reviews',{}))
        if 'submission' in context:
            reports.update(context['submission']['novelty'])
        concerns = {c['id']:c for report in reports.values() for c in report['result']['concerns'] if c['severity'] in ('major','critical')}
        return dict(summary='Software fixture author response; predictions remain unmeasured.',responses=[dict(concern_id=key,response='Acknowledge the concern and redesign the hypothesis.',evidence='Synthetic bounded test record.',change='Control the competing mechanism explicitly.',remaining_uncertainty='The effect remains unmeasured.',action='hypothesis') for key in concerns])
    if phase=='revision':
        previous=context['previous_round']
        ids=list(all_concerns(previous))
        return dict(summary='Add a mechanism-disambiguating held-out workload experiment.',insight_change='Narrow H01 to identifiable shifts.',method_change='Control adaptation state.',prediction_change='Widen uncertainty.',claims_removed='Remove universal superiority.',remaining_concerns='Actual efficacy remains unknown.',kind='experimental_design' if ids else 'verification',concern_ids=ids)
    if phase in ('review','discussion','final_reviews','exchange'):
        data = {'fields':{},'score_justifications':{},'assessment':'Synthetic independent judgment for software validation.', 'concerns':[]}
        rubric=context['rubric']
        for field in rubric['fields']:
            if field['phase']=='final' and phase=='review':
                continue
            value=field['options'][1]['value'] if field['kind']=='choice' else 'Software fixture assessment. No measured results or real conference assignment is asserted.'
            data['fields'][field['id']]=value
            if field['kind']=='choice':data['score_justifications'][field['id']]='Synthetic score backed only by fixture content; not a scientific review.'
        if phase=='review':
            data['concerns']=[dict(id=f'{task["round"]}.{role}.C01',severity='major',fundamental=False,claim='The workload split must identify the mechanism.',evidence='Synthetic experimental design concern.',resolution_criterion='Specify independent held-out workload families.')]
        else:
            own=context['initial_reviews'][role]['result']['concerns']
            data.update(change_reason='The response specifies the planned control; the actual effect remains hypothetical.',
                concern_status={c['id']:dict(status='resolved',reason='The design-level request is addressed; empirical efficacy is not established.',evidence='Fixture experimental protocol and response.') for c in own})
        return data
    if phase in ('ac','sac'):
        reports=list(context['initial_reviews'].values()) + list(context['submission']['novelty'].values())
        reports += list(context.get('reviewer_discussion', {}).values())
        reports += list(context.get('final_reviews', {}).values())
        if context.get('ac_meta_review'):
            reports += [context['ac_meta_review']]
        for exchange in context.get('exchanges', []):
            reports += [value for key, value in exchange['responses'].items() if key != 'author']
        concerns={c['id']:c for report in reports for c in report['result'].get('concerns', [])}
        case=round_outcome or ('addressable_rejection' if n==1 else 'strong_acceptance')
        return dict(**{key:PROSE for key in ('summary','agreement_analysis','rebuttal_assessment','unresolved_issues','contribution_assessment','rationale')},
            recommendation=('accept' if case=='strong_acceptance' else 'reject') if phase=='ac' else ('Accept' if case=='strong_acceptance' else 'Revise'),
            case=case,decision_scope=context['rubric']['procedures'][phase]['scope'],
            readiness={key:dict(met=case=='strong_acceptance',evidence='Synthetic assessment for software verification only.') for key in C.READINESS},
            concern_status={key:dict(status='resolved' if case=='strong_acceptance' else 'open',reason='Synthetic chair disposition.',evidence='Fixture round history.') for key in concerns},
            ac_reasoning_assessment='Independent software-fixture audit; not a real SAC decision.',score_text_consistency='Fixture scores intentionally remain distinct from the decision.',dissent='Retained in the record.',next_action='Implement the falsification study if authorized.')
    raise AssertionError(phase)


def response_for(store, task=None, **options):
    task=task or pending(store.project)[0]
    packet=envelope(store.project,task)
    return dict(task_id=task['id'],context_sha256=packet['context_sha256'],session_id='fixture-isolated-'+task['id'],
                independent=True,result=result_for(packet,**options))


def drive(store, stop=None, **options):
    for _ in range(150):
        tasks=pending(store.project)
        if not tasks or stop and tasks[0]['stage']==stop:
            break
        store.submit(response_for(store,**options))
    else:
        raise AssertionError('workflow did not terminate')
    return store
