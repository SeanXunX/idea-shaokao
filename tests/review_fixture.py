"""Explicit synthetic research artifacts for renderer and browser behavior checks."""
import json
from pathlib import Path


def write_index(root, index):
    (Path(root) / 'final/review-data.json').write_text(json.dumps(index, indent=2), encoding='utf-8')


def make_workspace(root, slug='adaptive-cache', mode='independent'):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    sources = {
        'final/final_report.md': '# Adaptive cache study\n\nSoftware test fixture. Proposal only; no measured result. Proceed to an essential feasibility test.\n',
        'issue_tracker.md': '# Issues\nI-1: Critical, Pending experiment. I-2: Moderate, Resolved.\n',
        'proposal/v01/proposal.md': '# Method\nHypothesis H-cost: adaptive eviction may reduce cache misses. This is untested.\n',
        'reviews/round-01/reviewer-R2-initial.md': '# R2 initial\nRound 1. Cost claim needs a fair baseline. Score: 5/8.\n',
        'rebuttals/round-01.md': '# Author response\nThe baseline test is planned, not performed.\n',
        'reviews/round-02/reviewer-R2-final.md': '# R2 reassessment\nRound 2. Experimental plan improved. Cost remains unmeasured. Score: 6/8.\n',
        'reviews/round-02/sac-assessment.md': '# SAC\nProceed to the feasibility experiment at proposal stage; this is not a validated paper.\n',
        'proposal/v01/experiments.md': '# E-early\nPlanned experiment: match tuning and workload budgets against the baseline. No run has occurred.\n',
    }
    for path, contents in sources.items():
        output = root / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(contents, encoding='utf-8')
    state = dict(schema_version=1, slug=slug, topic='Adaptive cache eviction', venue='Unspecified',
                 review_stage='proposal', execution_mode=mode, current_round=2, max_rounds=4,
                 status='completed', next_action='Run the essential baseline test.',
                 proposal_version='v01', convergence='not_converged', recommendation='Proceed',
                 created_at='2026-11-07T00:00:00+00:00', updated_at='2026-11-07T01:00:00+00:00')
    (root / 'state.json').write_text(json.dumps(state), encoding='utf-8')
    index = {
        'schema_version': 1, 'test_case': True,
        'overview': dict(description='Study adaptive cache eviction under matched workload budgets.',
                         recommendation='Proceed', assessor='SAC' if mode == 'independent' else 'Author',
                         rationale='Proceed to a proposal-stage feasibility test; empirical claims remain pending.',
                         sources=['sac'] if mode == 'independent' else ['report']),
        'sources': {'proposal': 'proposal/v01/proposal.md', 'initial': 'reviews/round-01/reviewer-R2-initial.md',
                    'response': 'rebuttals/round-01.md', 'final': 'reviews/round-02/reviewer-R2-final.md',
                    'sac': 'reviews/round-02/sac-assessment.md', 'plan': 'proposal/v01/experiments.md'},
        'issues': [dict(id='I-1', aliases=['I-1', 'R01-R2-01'], title='Cost claim needs a fair baseline',
                        severity='Critical', status='Pending experiment', round=2,
                        criterion='Run the specified fair-baseline test.', discussion=[
                            dict(author='R2', phase='Initial review', round=1, text='Cost is unmeasured.', source='initial'),
                            dict(author='Author', phase='Rebuttal', round=1, text='The test is planned, not performed.', source='response'),
                            dict(author='R2', phase='Reassessment', round=2, text='The design is improved; the effect is still untested.', source='final')]),
                   dict(id='I-2', title='Document the workload split', severity='Moderate', status='Resolved', round=1,
                        criterion='Record the intended split in the plan.', sources=['plan'], discussion=[])],
        'claims': [dict(id='H-cost', title='Lower miss rate', text='Adaptive eviction may reduce misses.',
                        status='Hypothesis — untested', sources=['proposal'])],
        'reviewers': [dict(id='R2', round=1, stage='proposal', rubric='Fixture scale 1–8',
                           initial=dict(score='5/8', source='initial'), final=None),
                      dict(id='R2', round=2, stage='proposal', rubric='Fixture scale 1–8',
                           final=dict(score='6/8', source='final'), confidence='Limited empirical evidence')]
        if mode == 'independent' else [],
        'timeline': [dict(id='round-1', round=1, role='R2', label='Initial review', summary='A baseline was requested.', source='initial'),
                     dict(id='round-2', round=2, role='SAC' if mode == 'independent' else 'Author', label='Assessment',
                          summary='Proceed to a feasibility test, without empirical validation.', source='sac' if mode == 'independent' else 'report')],
        'experiments': [dict(id='E-early', title='Fair baseline', kind='Proposed experiment', status='Planned',
                             summary='Match budgets; no measurement is available.', source='plan')],
    }
    write_index(root, index)
    return state, index
