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


def add_research_design(root, index):
    """Sourced, explicitly synthetic content for the complete interface example."""
    root = Path(root)
    def entry(key, title, text, sources):
        return dict(id=key, title=title, text=text, sources=sources)
    index['overview']['description'] = ('Illustrative software test fixture: adapt cache eviction to changing workloads, '
        'then test whether it lowers miss rate under the same memory and tuning budget. No experiments have run.')
    index['rounds'] = [
        dict(round=1, version='v01', stage='proposal', status='Initial assessment',
             idea=dict(text='Adapt the eviction policy to recent access patterns. The proposed benefit is a lower miss rate under a fixed cache budget.', sources=['proposal']),
             changes=dict(text='Initial submission. A fair comparison and the intended workload split still need to be specified.', sources=['initial']),
             outcome=dict(text='R2 requests a fair baseline before the cost claim can be assessed. Initial score: 5/8; no post-rebuttal score is recorded in this round.', sources=['initial'])),
        dict(round=2, version='v01', stage='proposal', status='Plan reassessment',
             idea=dict(text='Keep the adaptive eviction hypothesis and test it against an exact LRU baseline under matched workloads, memory, and tuning budgets.', sources=['proposal','plan']),
             changes=dict(text='The author specifies a held-out workload split and a matched-budget feasibility test. The proposal stays at v01; no replacement submission or measured result is claimed.', sources=['response','plan']),
             outcome=dict(text='Proceed to the feasibility test at proposal stage. The plan improves to a recorded 6/8; the effect remains unmeasured.', sources=['final','sac']))]
    experiment = index['experiments'][0]
    experiment.update(
        hypothesis='H-cost: adapting eviction to workload changes reduces misses at the same cache memory budget.',
        setup='Compare adaptive eviction with LRU on the same replay harness. Hold cache capacity fixed at 64 MiB and include adaptation state in that budget.',
        data='Synthetic access traces: stationary, abrupt working-set switch, and gradual drift. Separate tuning traces from held-out evaluation traces.',
        baselines='Exact LRU as the primary comparator; FIFO as a simple control. Use identical trace order and capacity for every policy.',
        metrics='Miss rate (misses / requests), processing time per request, and peak resident memory. Report per-workload values and variability across five trace seeds.',
        controls='Disable adaptation to isolate its contribution. Match warm-up, capacity, access sequence, tuning trials, and measurement boundaries.',
        success='Advance only if held-out miss rate improves over LRU without exceeding the total memory budget. Predefine a practical effect size and time-overhead limit before running.',
        failure='Stop if the apparent gain disappears with matched memory, or if it depends on tuning on held-out traces. Do not claim a latency benefit from miss rate alone.',
        resources='First build a CPU trace-replay harness and verify identical accounting. A single workstation is the assumed starting point; runtime and engineering estimates remain to be established.',
        result='Not run. No measured miss rate, speedup, confidence interval, or successful outcome exists.')
    index['plan'] = {
        'idea': [
            entry('problem','Research question','Can an eviction policy respond to workload drift and reduce cache misses without extra memory or unequal tuning?', ['proposal']),
            entry('method','Method design','Track recent access patterns, update the eviction preference on a fixed schedule, and choose a victim within the same total cache budget. Keep the replay harness and trace input shared with the baselines.', ['proposal']),
            entry('positioning','Contribution & boundaries','The proposed contribution is adaptation under a matched total resource budget. Novelty against external prior work is not established by this fixture; neither cache-miss improvements nor lower latency have been measured.', ['proposal','plan'])],
        'story': [
            entry('problem','Problem → gap','Workload changes can make a fixed eviction rule a poor fit. The research question is whether adaptation helps once the cost of its own state and tuning is included.', ['proposal']),
            entry('insight','Insight → mechanism','Use recent workload behavior to change eviction preferences. The causal claim is about responding to drift; the no-adaptation control must isolate that mechanism.', ['proposal','plan']),
            entry('evidence','Evidence → conclusion','First establish a fair replay protocol, then test the main effect, and finally disable adaptation. A paper can claim a benefit only if held-out traces support it within the same resource budget.', ['plan']),
            entry('limits','Limits of the story','Synthetic traces alone would not establish production relevance. Report regressions, workload-specific effects, and policy overhead. The current artifact is an experiment plan, not a result.', ['plan'])],
        'paper': [
            dict(id='abstract', title='Abstract', goal='Summarize the research question, mechanism, evidence stage, and supported contribution.', design='Use one sentence each for the problem, adaptive policy, fair evaluation, and evidence-limited conclusion. Replace planned outcomes with measured findings only after execution.', evidence='The present proposal can describe a testable hypothesis and protocol; it has no result numbers to report.', experiments=['E-early'], sources=['proposal','plan']),
            dict(id='introduction', title='Introduction', goal='Establish why adaptation under a fixed resource budget is the research question.', design='Open with workload drift, state the limitation of a fixed eviction rule, then describe the proposed mechanism and falsifiable contribution. Keep claims conditional until experiments run.', evidence='A workload-shift illustration and a concise statement of H-cost. No fabricated headline improvement.', experiments=[], sources=['proposal']),
            dict(id='related-work', title='Related work', goal='Position the mechanism against the closest eviction and adaptive-policy methods.', design='Compare the information each policy observes, adaptation schedule, tuning allowance, and memory overhead. Explain the substantive difference after a verified literature search.', evidence='A sourced comparison matrix is required; external novelty is currently unestablished.', experiments=[], sources=['proposal']),
            dict(id='method', title='Method', goal='Make the proposed policy implementable and its resource accounting auditable.', design='Define access events, state, update schedule, victim selection, and total memory accounting. Give pseudocode and analyze per-request overhead.', evidence='One policy-flow figure and pseudocode; report adaptation-state memory alongside cached objects.', experiments=[], sources=['proposal']),
            dict(id='experiments', title='Experimental design & results', goal='Decide whether the mechanism improves the primary metric under fair conditions.', design='Describe held-out traces and the matched-budget protocol first. Compare with LRU and FIFO, then remove adaptation. Present per-workload outcomes, overhead, variability, and failures after execution.', evidence='Planned main comparison table, workload-shift curve, and adaptation ablation. All results remain pending.', experiments=['E-early'], sources=['plan']),
            dict(id='analysis', title='Mechanism analysis & ablations', goal='Separate the adaptation mechanism from extra state, tuning, and incidental workload effects.', design='Compare the adaptive policy with adaptation disabled under the same budget. Analyze stationary, abrupt-switch, and gradual-drift traces separately; account for processing-time and memory overhead.', evidence='A planned no-adaptation ablation and per-workload effect/overhead plots. Outcomes remain pending.', experiments=['E-early'], sources=['plan']),
            dict(id='discussion', title='Discussion & limitations', goal='Explain when the mechanism helps, when it fails, and the limits of generalization.', design='Relate any effect to drift and policy overhead. Discuss synthetic-trace coverage, tuning sensitivity, and production workloads that have not been evaluated.', evidence='Negative outcomes and resource regressions belong in the analysis. No production claim follows from this fixture.', experiments=['E-early'], sources=['plan']),
            dict(id='conclusion', title='Conclusion', goal='Answer the original research question at the evidence stage actually reached.', design='State the supported finding and scope, then the most consequential next test. If the test fails, explain what was falsified rather than restating the intended contribution.', evidence='Only completed, reproducible evidence can support a final performance claim.', experiments=['E-early'], sources=['plan'])],
        'roadmap': [
            dict(id='harness', title='Build the shared replay harness', task='Implement trace replay, LRU, FIFO, and consistent memory accounting before adding the adaptive policy.', dependencies='Freeze the workload split and measurement protocol.', artifact='A reproducible harness, trace manifests, and accounting checks.', estimate='CPU workstation assumed; engineering effort has not been estimated.', sources=['plan']),
            dict(id='gate', title='Run the decisive feasibility test', task='Execute E-early on held-out traces with matched budgets; report all workload outcomes and the no-adaptation control.', dependencies='Verified harness, frozen thresholds, and a policy implementation.', artifact='Raw logs, configuration, memory accounting, and a per-workload comparison table.', estimate='Five trace seeds planned; wall-clock cost is unknown until a pilot run.', sources=['plan']),
            dict(id='write', title='Write from the evidence', task='Build the paper around the supported mechanism and its failure boundaries. Revisit the contribution if the matched-budget effect fails.', dependencies='Completed feasibility evidence and verified related work.', artifact='Section-by-section manuscript with traceable figures and limitations.', estimate='Writing effort depends on the outcome; no submission readiness is implied.', sources=['plan'])]}
    # The synthetic source documents explicitly contain every display decision.
    (root / 'proposal/v01/proposal.md').write_text('# Synthetic proposal v01\n\n' +
        '\n\n'.join(x['text'] for x in index['plan']['idea']) + '\n\n' +
        '\n\n'.join(x['text'] for x in index['plan']['story'][:2]) + '\n\n' +
        '\n\n'.join(json.dumps(x) for x in index['plan']['paper'] if 'proposal' in x['sources']) + '\n')
    (root / 'proposal/v01/experiments.md').write_text('# Synthetic experiment and writing plan — no runs\n\n' +
        json.dumps(experiment, indent=2) + '\n\n' + json.dumps(index['plan'], indent=2) + '\n')
    (root / 'rebuttals/round-01.md').write_text('# Synthetic author response\n\n' + index['rounds'][1]['changes']['text'] + '\n')
    # Keep actual fixture phase provenance rather than synthesizing missing roles.
    index['timeline'].insert(1, dict(id='rebuttal', round=1, role='Author', label='Author response',
        summary='Specify the held-out split and matched-budget test; measurements remain pending.', source='response'))
    write_index(root, index)
    return index
