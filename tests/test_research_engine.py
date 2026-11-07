"""End-to-end and failure checks of enforceable scientific workflow invariants."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from engine_fixture import create, drive, response_for, official_bundle, official_rubric, REPO
from shaokao import contracts as C
from shaokao.conference import fetch_sources, validate_rubric, validate_answers
from shaokao.engine import Store, pending, envelope, current, all_concerns
from shaokao.report import render, build_data


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'research'
        self.store = create(self.root)

    def advance(self, stage):
        drive(self.store, stop=stage)
        self.assertEqual(pending(self.store.project)[0]['stage'], stage)

    def test_full_two_round_research_to_acceptance_and_history(self):
        drive(self.store)
        p=self.store.project
        self.assertEqual(p['status'],'accepted_simulation')
        self.assertEqual(len(p['rounds']),2)
        a,b=p['rounds']
        self.assertEqual(b['predecessor'],a['id'])
        self.assertEqual(a['outcome'],'addressable_rejection')
        self.assertEqual(b['outcome'],'strong_acceptance')
        for r in p['rounds']:
            self.assertEqual(len(r['iterations'][-1]['stress']),3)
            self.assertTrue(r['iterations'][-1]['response'])
            self.assertEqual(len(r['reviews']),3)
            self.assertEqual(len(r['discussion']),3)
            self.assertEqual(len(r['exchanges']),1)
            self.assertEqual(len(r['final_reviews']),3)
            self.assertEqual(r['submission']['paper_sha256'],C.digest(r['submission']['paper']))
            self.assertEqual(set(r['submission']['paper']['sections']),set(C.SECTIONS))
            self.assertEqual(r['submission']['paper']['predictions'][0]['kind'],'hypothetical')
        self.assertEqual(b['revision']['result']['concern_ids'],list(all_concerns(a)))
        original=C.digest(a)
        resumed=Store(self.root)
        self.assertEqual(C.digest(resumed.project['rounds'][0]),original)
        self.assertEqual(resumed.project,p)
        self.assertEqual(p['final_paper_id'],b['submission']['paper_id'])

    def test_independent_initial_packets_remain_blind_and_stable(self):
        self.advance('review')
        tasks=pending(self.store.project)
        before={t['role']:envelope(self.store.project,t) for t in tasks}
        self.store.submit(response_for(self.store,tasks[0]))
        for task in tasks[1:]:
            after=envelope(self.store.project,task)
            self.assertEqual(before[task['role']]['context_sha256'],after['context_sha256'])
            context=after['context']
            self.assertNotIn('initial_reviews',context)
            self.assertNotIn('previous_assessment',context)
        # A missing reviewer leaves the stage pending; no positive default.
        self.assertEqual(current(self.store.project)['phase'],'review')
        self.assertEqual(len(pending(self.store.project)),2)

    def test_novelty_failure_requires_real_recomposition_and_stops_at_cap(self):
        self.store.project['config']['max_stress_iterations']=3
        self.advance('stress')
        for task in pending(self.store.project):
            self.store.submit(response_for(self.store,task,stress_verdict='FAIL'))
        bad=response_for(self.store)
        bad['result']['responses'][0]['action']='clarify'
        with self.assertRaises(C.ContractError):self.store.submit(bad)
        self.store.submit(response_for(self.store))
        self.assertEqual(pending(self.store.project)[0]['stage'],'literature')
        self.assertNotIn('submission',current(self.store.project))
        drive(self.store,stress_verdict='FAIL')
        self.assertEqual(self.store.project['status'],'abandoned')
        r=current(self.store.project)
        self.assertEqual(len(r['iterations']),3)
        self.assertFalse(r['reviews'])
        self.assertEqual(len({x['paper_id'] for x in r['iterations']}),3)
        self.assertIn('novelty gate',build_data(self.store)['project']['rationale'])

    def test_conditional_novelty_never_advances_directly_to_review(self):
        self.advance('stress')
        for task in pending(self.store.project):
            self.store.submit(response_for(self.store,task,stress_verdict='CONDITIONAL PASS'))
        self.store.submit(response_for(self.store))
        self.assertEqual(current(self.store.project)['phase'],'literature')
        self.assertNotIn('submission',current(self.store.project))

    def test_incomplete_paper_and_fabricated_predictions_are_rejected(self):
        self.advance('paper')
        good=response_for(self.store)
        for mutate in (
            lambda d:d['sections'].pop('related_work'),
            lambda d:d['sections'].__setitem__('technical_design','- build a model'),
            lambda d:d['predictions'][0].__setitem__('kind','observed'),
            lambda d:d['predictions'][0].__setitem__('estimate',[8,2]),
            lambda d:d['predictions'][0].__setitem__('estimate',[float('nan'),5]),
            lambda d:d['predictions'][0].__setitem__('experiment_id','missing'),
        ):
            bad=deepcopy(good);mutate(bad['result'])
            with self.assertRaises((C.ContractError,ValueError)):self.store.submit(bad)
        self.assertEqual(current(self.store.project)['phase'],'paper')

    def test_exact_scores_require_justification_and_do_not_get_normalized(self):
        self.advance('review')
        original=response_for(self.store)
        for mutate in (
            lambda d:d['fields'].__setitem__('overall_recommendation',10),
            lambda d:d['fields'].__setitem__('soundness',True),
            lambda d:d['fields'].__setitem__('novelty_score',5),
            lambda d:d['score_justifications'].pop('confidence'),
        ):
            bad=deepcopy(original);mutate(bad['result'])
            with self.assertRaises(C.ContractError):self.store.submit(bad)
        self.store.submit(original)
        self.assertEqual(current(self.store.project)['reviews']['R1']['result']['fields']['overall_recommendation'],5)

    def test_wrong_version_duplicate_report_and_reused_session_are_rejected(self):
        self.advance('review')
        good=response_for(self.store)
        bad=deepcopy(good);bad['context_sha256']='wrong-paper'
        with self.assertRaises(C.ContractError):self.store.submit(bad)
        self.store.submit(good)
        with self.assertRaises(C.ContractError):self.store.submit(good)
        bad=response_for(self.store);bad['session_id']=good['session_id']
        with self.assertRaises(C.ContractError):self.store.submit(bad)

    def test_rebuttal_missing_critical_response_and_official_limit_are_rejected(self):
        self.advance('rebuttal')
        bad=response_for(self.store);bad['result']['responses']=[]
        with self.assertRaises(C.ContractError):self.store.submit(bad)
        bad=response_for(self.store);bad['result']['summary']='x'*5001
        with self.assertRaises(C.ContractError):self.store.submit(bad)

    def test_failure_and_deleted_checkpoint_resume_only_pending_task(self):
        self.advance('review')
        self.store.submit(response_for(self.store))
        task=pending(self.store.project)[0]
        self.store.failure(task,'interrupted runner')
        (self.root/'project.json').write_text('{broken checkpoint')
        restored=Store(self.root)
        self.assertEqual(pending(restored.project)[0],task)
        self.assertIn('R1',current(restored.project)['reviews'])
        self.assertEqual(restored.project['failures'][-1]['error'],'interrupted runner')
        restored.checkpoint()
        self.assertEqual(json.loads((self.root/'project.json').read_text()),restored.project)

    def test_chain_corruption_and_concurrent_commit_do_not_replace_history(self):
        stale=Store(self.root)
        self.store.submit(response_for(self.store))
        with self.assertRaises(C.ContractError):stale.failure(pending(stale.project)[0],'race')
        event=self.root/'events/000002.json'
        content=json.loads(event.read_text());content['rubric']['version']='altered'
        event.write_text(json.dumps(content))
        with self.assertRaises(C.ContractError):Store(self.root)

    def test_fatal_overlap_and_failed_rebuttal_cannot_converge(self):
        self.advance('review')
        for task in pending(self.store.project):
            reply=response_for(self.store,task)
            reply['result']['concerns'][0].update(severity='critical',fundamental=True,claim='Fatal prior-art overlap remains.')
            self.store.submit(reply)
        self.advance('sac')
        reply=response_for(self.store,round_outcome='strong_acceptance')
        for value in reply['result']['concern_status'].values():value['status']='open'
        self.store.submit(reply)
        self.assertNotEqual(self.store.project['status'],'accepted_simulation')
        self.assertFalse(self.store.project['rounds'][0]['acceptance_eligible'])

    def test_reviewer_disagreement_and_ac_sac_disagreement_are_preserved(self):
        self.advance('review')
        for i,task in enumerate(pending(self.store.project)):
            reply=response_for(self.store,task)
            reply['result']['fields']['overall_recommendation']=1 if i==0 else 6
            self.store.submit(reply)
        self.advance('ac')
        self.store.submit(response_for(self.store,round_outcome='strong_acceptance'))
        self.store.submit(response_for(self.store,round_outcome='addressable_rejection'))
        r=self.store.project['rounds'][0]
        self.assertEqual([x['result']['fields']['overall_recommendation'] for x in r['reviews'].values()],[1,6,6])
        self.assertTrue(r['chair_disagreement'])
        self.assertFalse(r['acceptance_eligible'])

    def test_budget_exhaustion_and_consecutive_acceptance_requirements(self):
        drive(self.store,round_outcome='addressable_rejection')
        self.assertEqual(self.store.project['status'],'budget_exhausted')
        another=create(Path(self.temp.name)/'two-accepts',acceptance_rounds=2,max_rounds=2)
        drive(another,round_outcome='strong_acceptance')
        self.assertEqual(another.project['status'],'accepted_simulation')
        self.assertEqual(len(another.project['rounds']),2)

    def test_single_agent_cannot_satisfy_independent_gate(self):
        store=create(Path(self.temp.name)/'self',execution_mode='single_agent')
        drive(store,stop='stress')
        with self.assertRaises(C.ContractError):store.submit(response_for(store))

    def test_structured_report_contains_complete_real_event_history_and_paper(self):
        drive(self.store)
        data=build_data(self.store)
        self.assertEqual(data['schema_version'],2)
        self.assertEqual(len(data['research']['rounds']),2)
        for source in data['sources'].values():
            self.assertEqual(hashlib_sha((self.root/source['path']).read_bytes()),source['sha256'])
        result=render(self.store)
        self.assertTrue(Path(result['output']).is_file())
        paper=(self.root/'final/paper.md').read_text()
        self.assertIn('Expected Results and Quantitative Predictions',paper)
        self.assertIn('hypothetical',paper)
        self.assertIn('SOFTWARE TEST FIXTURE',(self.root/'final/final_report.md').read_text())
        identity=json.loads((self.root/'final/review-manifest.json').read_text())['workspace_id']
        render(Store(self.root))
        self.assertEqual(json.loads((self.root/'final/review-manifest.json').read_text())['workspace_id'],identity)


    def test_chair_recommendation_cannot_contradict_strong_acceptance_case(self):
        self.advance('ac')
        bad=response_for(self.store,round_outcome='strong_acceptance')
        bad['result']['recommendation']='reject'
        with self.assertRaises(C.ContractError):self.store.submit(bad)
        self.store.submit(response_for(self.store,round_outcome='strong_acceptance'))
        bad=response_for(self.store,round_outcome='strong_acceptance')
        bad['result']['recommendation']='Revise'
        with self.assertRaises(C.ContractError):self.store.submit(bad)

    def test_major_novelty_concerns_survive_into_chair_adjudication(self):
        self.advance('stress')
        first=pending(self.store.project)[0]
        reply=response_for(self.store,first)
        issue=dict(id='NOVELTY-MAJOR',severity='major',fundamental=True,
                   claim='The core mechanism might be an existing formulation.',
                   evidence='Synthetic prior-art overlap.',resolution_criterion='Defend the distinct insight.')
        reply['result']['concerns']=[issue]
        self.store.submit(reply)
        self.advance('ac')
        self.assertIn(issue['id'],all_concerns(current(self.store.project)))
        bad=response_for(self.store,round_outcome='strong_acceptance')
        bad['result']['concern_status'].pop(issue['id'])
        with self.assertRaises(C.ContractError):self.store.submit(bad)
        self.store.submit(response_for(self.store,round_outcome='strong_acceptance'))
        bad=response_for(self.store,round_outcome='strong_acceptance')
        bad['result']['concern_status'][issue['id']]['status']='open'
        self.store.submit(bad)
        self.assertFalse(self.store.project['rounds'][0]['acceptance_eligible'])

    def test_batched_discussion_packets_are_stable_and_provenance_is_required(self):
        self.advance('discussion')
        replies=[response_for(self.store,t) for t in pending(self.store.project)]
        author_session=current(self.store.project)['rebuttal']['session_id']
        bad=deepcopy(replies[0]);bad['independent']=False
        with self.assertRaises(C.ContractError):self.store.submit(bad)
        bad=deepcopy(replies[0]);bad['session_id']=author_session
        with self.assertRaises(C.ContractError):self.store.submit(bad)
        for reply in replies:self.store.submit(reply)
        self.assertEqual(current(self.store.project)['phase'],'exchange')

    def test_venue_change_resets_acceptance_streak_and_requires_a_new_rubric(self):
        store=create(Path(self.temp.name)/'venue-switch',acceptance_rounds=2,max_rounds=3)
        # Finish one eligible round, stopping at the next complete-round boundary.
        drive(store,stop='ac')
        store.submit(response_for(store,round_outcome='strong_acceptance'))
        store.submit(response_for(store,round_outcome='strong_acceptance'))
        self.assertEqual(current(store.project)['phase'],'revision')
        store.change_target(dict(name='ICML',year=2027,track='Main Track'))
        self.assertEqual(pending(store.project)[0]['stage'],'rubric')
        with self.assertRaises(C.ContractError):store.install_rubric(official_rubric())
        historical=official_rubric();historical['conference']['year']=2027
        historical.update(historical=True,historical_reason='Current-year form unavailable in this synthetic test.')
        store.install_rubric(historical)
        drive(store,stop='ac')
        store.submit(response_for(store,round_outcome='strong_acceptance'))
        store.submit(response_for(store,round_outcome='strong_acceptance'))
        self.assertNotEqual(store.project['status'],'accepted_simulation')
        self.assertEqual(store.project['rounds'][0]['rubric']['conference']['year'],2026)
        self.assertEqual(store.project['rounds'][1]['rubric']['conference']['year'],2027)

    def test_missing_closest_search_and_abstract_only_evidence_cannot_pass_prior_art(self):
        self.advance('literature')
        reply=response_for(self.store)
        for search in reply['result']['searches']:
            if search['coverage']=='concurrent':search.update(status='failed',error='Provider unavailable.')
        self.store.submit(reply)
        self.advance('stress')
        with self.assertRaises(C.ContractError):self.store.submit(response_for(self.store))

    def test_fresh_process_driver_and_resumption_after_failure(self):
        from research import run
        task=pending(self.store.project)[0]
        with self.assertRaises(C.ContractError):run(self.store,[sys.executable,'-c','raise SystemExit(2)'])
        self.assertEqual(pending(self.store.project)[0],task)
        result=run(Store(self.root),[sys.executable,str(REPO/'tests/fixture_agent.py')],max_steps=100)
        self.assertEqual(result['status'],'accepted_simulation')
        self.assertFalse(result['pending'])


    def test_new_chair_concerns_reach_senior_assessment_and_next_revision(self):
        self.advance('ac')
        reply=response_for(self.store)
        issue=dict(id='AC-NEW',severity='critical',fundamental=True,
                   claim='The mechanism depends on an invalid identifiability assumption.',
                   evidence='Synthetic counterexample identified by the chair.',resolution_criterion='Change the mechanism assumption.')
        reply['result']['concerns']=[issue]
        reply['result']['concern_status'][issue['id']]=dict(status='open',reason='The assumption is central.',evidence='Chair counterexample.')
        self.store.submit(reply)
        self.assertIn(issue['id'],all_concerns(current(self.store.project)))
        bad=response_for(self.store);bad['result']['concern_status'].pop(issue['id'])
        with self.assertRaises(C.ContractError):self.store.submit(bad)
        self.store.submit(response_for(self.store))
        revision=response_for(self.store)
        self.assertIn(issue['id'],revision['result']['concern_ids'])

    def test_implausible_predictions_flagged_by_reviewer_block_readiness(self):
        self.advance('review')
        for task in pending(self.store.project):
            reply=response_for(self.store,task)
            if task['role']=='R3':
                reply['result']['concerns'][0].update(severity='critical',claim='The expected improvement is implausible under the stated assumptions.')
            self.store.submit(reply)
        self.advance('sac')
        reply=response_for(self.store,round_outcome='strong_acceptance')
        reply['result']['readiness']['plausible_predictions']['met']=False
        reply['result']['concern_status']['round-01.R3.C01']['status']='pending'
        self.store.submit(reply)
        self.assertFalse(self.store.project['rounds'][0]['acceptance_eligible'])

    def test_newly_discovered_prior_art_can_be_registered_by_adversary(self):
        self.advance('stress')
        reply=response_for(self.store,stress_verdict='CONDITIONAL PASS')
        paper=deepcopy(current(self.store.project)['literature']['result']['papers'][0])
        paper.update(id='P-NEW',title='Concurrent equivalent formulation')
        reply['result']['discovered_papers']=[paper]
        reply['result']['comparison_table'][0]['paper_id']='P-NEW'
        self.store.submit(reply)
        stored=current(self.store.project)['iterations'][-1]['stress']['prior_art']['result']
        self.assertEqual(stored['discovered_papers'][0]['id'],'P-NEW')


    def test_check_only_render_writes_nothing_and_unsubmitted_edits_are_not_final(self):
        self.assertFalse((self.root/'final').exists())
        render(self.store,check=True)
        self.assertFalse((self.root/'final').exists())
        # After an unfavorable complete round, a new unreviewed draft cannot
        # silently become the final reviewed paper shown on the overview.
        self.advance('revision')
        first=self.store.project['rounds'][0]['submission']['paper_id']
        self.advance('stress')
        data=build_data(self.store)
        self.assertEqual(data['research']['selected_paper_id'],first)
        self.assertEqual(data['project']['paperStatus'],'Submitted proposal')

    def test_contribution_selection_is_frozen_and_invalid_categories_block_installation(self):
        store=Store.create(Path(self.temp.name)/'contribution-types','Software fixture',
                           dict(name='ICML',year=2026,track='Main Track'),dict(test_mode=True))
        rubric=official_rubric()
        # A category from the official form heading tests evidence-bound selection;
        # this is not a claim that ICML declares this as a contribution taxonomy.
        rubric['contribution_types']=[dict(id='fixture-main',label='Main Track',criteria='Software selection test.',
                                           source_id='reviewer',quote='Main Track Reviewer Form Instructions')]
        with self.assertRaises(C.ContractError):store.install_rubric(rubric)
        store.select_contribution_type('fixture-main')
        store.install_rubric(rubric)
        self.assertEqual(current(store.project)['contribution_type'],'fixture-main')
        self.assertEqual(envelope(store.project,pending(store.project)[0])['context']['project']['contribution_type'],'fixture-main')
        with self.assertRaises(C.ContractError):store.select_contribution_type('different')


    def test_four_reviewer_roster_and_individual_profiles_are_preserved(self):
        store=create(Path(self.temp.name)/'four-reviewers',reviewers=4,max_rounds=1)
        drive(store,round_outcome='strong_acceptance')
        r=current(store.project)
        self.assertEqual(set(r['reviews']),{'R1','R2','R3','R4'})
        self.assertEqual(r['reviewer_profiles']['R4']['expertise'],'fit')
        self.assertEqual(len(r['final_reviews']),4)


    def test_new_senior_concern_cannot_crash_replay_or_bypass_ac_adjudication(self):
        self.advance('ac')
        self.store.submit(response_for(self.store,round_outcome='strong_acceptance'))
        reply=response_for(self.store,round_outcome='strong_acceptance')
        issue=dict(id='SAC-NEW',severity='major',fundamental=False,
                   claim='A new alternative explanation needs investigation.',
                   evidence='Synthetic senior finding.',resolution_criterion='Both chairs must assess the new issue.')
        reply['result']['concerns']=[issue]
        reply['result']['concern_status'][issue['id']]=dict(status='resolved',reason='Senior assertion alone.',evidence='Synthetic supporting argument.')
        self.store.submit(reply)
        restored=Store(self.root)
        self.assertEqual(restored.project,self.store.project)
        self.assertFalse(restored.project['rounds'][0]['acceptance_eligible'])
        self.assertIn(issue['id'],all_concerns(restored.project['rounds'][0]))


    def test_changed_carried_concern_is_rejected_before_it_can_poison_history(self):
        self.advance('discussion')
        before=self.store.sequence
        reply=response_for(self.store)
        concern=deepcopy(current(self.store.project)['reviews']['R1']['result']['concerns'][0])
        concern['severity']='critical'
        reply['result']['concerns']=[concern]
        with self.assertRaises(C.ContractError):self.store.submit(reply)
        self.assertEqual(self.store.sequence,before)
        self.store.submit(response_for(self.store))
        self.assertEqual(Store(self.root).project,self.store.project)


def hashlib_sha(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()


class ConferenceTests(unittest.TestCase):
    def test_real_official_form_extraction_and_provenance(self):
        rubric=official_rubric()
        validate_rubric(rubric,rubric['conference'])
        fields={f['id']:f for f in rubric['fields']}
        self.assertEqual([x['value'] for x in fields['soundness']['options']],[4,3,2,1])
        self.assertEqual([x['value'] for x in fields['overall_recommendation']['options']],[6,5,4,3,2,1])
        self.assertEqual(len(fields),14)
        self.assertIsNone(fields['soundness']['official_required'])
        self.assertEqual(next(x for x in rubric['sources'] if x['id']=='openreview')['status'],'failed')
        self.assertEqual([x['max_chars'] for x in rubric['procedures']['exchanges']],[5000]*3)

    def test_missing_sources_tampered_options_wrong_venue_and_silent_historical_fallback_block(self):
        good=official_rubric()
        mutations=[
            lambda r:r['fields'][2]['options'][0].__setitem__('value',10),
            lambda r:r['fields'][2]['options'][0].__setitem__('label','Outstanding'),
            lambda r:r['fields'].pop(),
            lambda r:r['sources'][0].__setitem__('status','failed'),
            lambda r:r.__setitem__('status','draft'),
            lambda r:r['conference'].__setitem__('year',2027),
        ]
        for mutation in mutations:
            bad=deepcopy(good);mutation(bad)
            with self.assertRaises(C.ContractError):validate_rubric(bad)
        with self.assertRaises(C.ContractError):validate_rubric(good,dict(name='NeurIPS',year=2026,track='Main Track'))

    def test_all_fetch_failures_are_recorded_and_cannot_start_reviews(self):
        def unavailable(*args,**kwargs):raise OSError('offline')
        manifest=json.loads((REPO/'examples/icml2026-sources.json').read_text())
        bundle=fetch_sources(manifest,opener=unavailable)
        self.assertEqual(len(bundle['sources']),6)
        self.assertTrue(all(s['status']=='failed' and 'offline' in s['error'] for s in bundle['sources']))
        from shaokao.conference import extract_form
        with self.assertRaises(C.ContractError):extract_form(bundle,'reviewer','Main Track Reviewer Form Instructions')

    def test_arbitrary_categorical_and_noncontiguous_numerical_options(self):
        rubric={'fields':[dict(id='recommendation',kind='choice',phase='both',required=True,options=[{'value':2},{'value':7},{'value':13}]),
                          dict(id='category',kind='multi_choice',phase='both',required=False,options=[{'value':'Theory'},{'value':'Negative Results'}])]}
        validate_answers(rubric,{'recommendation':13,'category':['Theory']},'initial')
        with self.assertRaises(C.ContractError):validate_answers(rubric,{'recommendation':6},'initial')
        with self.assertRaises(C.ContractError):validate_answers(rubric,{'recommendation':True},'initial')


if __name__=='__main__':unittest.main()
