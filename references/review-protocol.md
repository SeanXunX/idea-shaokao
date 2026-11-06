# Conference-inspired review protocol

Read this when preparing or conducting a review round. This is a research decision
process, not an actual conference decision or a prediction of acceptance.

## Establish the review stage

| Stage | Material to inspect | Meaning of a favorable recommendation |
| --- | --- | --- |
| Proposal | Question, closest prior art, method, assumptions, falsifiable hypotheses, executable experiment plan, resource estimates | Worth testing; novelty and expected benefits remain provisional |
| Implementation | Proposal plus actual code, revision identifier, environment, tests, run records, known gaps | The implementation supports the stated design within tested limits |
| Paper | Manuscript plus reproducible experiment records, baselines, uncertainty, analyses, limitations | Observed evidence supports the scoped claims; no real acceptance is implied |

Do not advance stages because scores improve. Implementation requires actual code
and verification; paper review requires actual results. Missing empirical evidence
in a proposal can be a planned validation requirement rather than an automatic
rejection, but a plan never resolves a claim that an effect has been demonstrated.

## Freeze the submission

Create `reviews/round-01/submission-manifest.md` for the first round, incrementing
the number thereafter. Record the idea/version, review stage, evidence cutoff,
reviewer roster and coverage, rubric, constraints, and exact packet file paths.
Use immutable snapshots or content hashes to identify what was reviewed. Include
the proposal, references and evidence ledger, experiment plan, limitations, and
any code/results appropriate to the stage. Mark unavailable material explicitly.

Do not edit this packet during the round. Place rebuttal additions in separate,
versioned evidence files and make them available to every reviewer. A material
method or claim change becomes the next submission version and round, not a
silent replacement. Start each new round by checking for newly relevant work.

## Round sequence

1. **Independent review.** Dispatch three or four separate reviewers using
   [roles.md](roles.md). Collect every initial report before sharing any of them.
   Preserve incomplete or failed assignments; retry within budget or disclose
   that the round is incomplete. The author must not fabricate missing reports.
2. **AC discussion before rebuttal.** The independent AC reads the reports,
   reconciles duplicate concerns without erasing their origins, and identifies
   decisive disagreements. Reviewers answer targeted questions and may revise
   positions with reasons. Save actual exchanges in
   `discussion-before-rebuttal.md`, including a provisional AC synthesis.
3. **Author rebuttal.** Save `rebuttals/round-01.md`. Respond to every critical
   and major concern, including disagreement introduced during discussion. Use
   the table below; acknowledge missing evidence and reject unsupported demands
   with reasons. Proposed experiments are not completed experiments.
4. **Discussion after rebuttal.** Send the complete rebuttal and new evidence
   to all reviewers. Each writes `reviewer-R1-final.md` (and equivalents), listing
   resolved and unresolved concerns, evidence assessed, final scores, confidence,
   and reasons for each score change or unchanged decisive objection. The AC
   directs a focused exchange about remaining conflicts; save actual replies in
   `discussion-after-rebuttal.md`. Disagreement may remain.
5. **AC meta-review.** Write `ac-meta-review.md`: contribution and strengths,
   decisive weaknesses, agreements, minority objections, rebuttal assessment,
   remaining issues, and a reasoned recommendation. Explain any difference from
   reviewer scores; never substitute a numerical average for judgment.
6. **SAC assessment.** A separate SAC inspects the full record, audits review
   quality and unresolved flaws, and writes `sac-assessment.md`. Record whether
   the process was complete, whether the AC handled disputes fairly, the current
   stage, critical remaining issues, confidence, decision, and next action.
7. **Revision or termination.** Apply the SAC decision and evidence-based issue
   updates. Save a new proposal version and change log before another round.
   Preserve reports and score history; do not rewrite earlier judgments.

Files other than the rebuttal above live under the current `reviews/round-NN/`.

## Reviewer report contract

Every initial report states role, round, version, stage, rubric, and evidence
actually inspected. Include:

- Summary of the problem, mechanism, and claimed contribution.
- Strengths; critical/major weaknesses; moderate/minor concerns.
- Novelty against named closest work, technical soundness, experimental adequacy,
  significance, and clarity, with depth guided by the assigned role.
- Questions for the author and required changes or decisive experiments.
- Stable issue IDs, severity, supporting sources or reasoning, and a concrete
  resolution criterion. Distinguish an observed contradiction from uncertainty.
- Scores, recommendation, confidence, remaining uncertainty, and what evidence
  would change the recommendation.

Use IDs such as `R01-R2-01` (round 1, reviewer 2, concern 1). A carried concern
keeps its original ID; link duplicates rather than silently deleting them.
Assign AC/SAC/red-team findings similarly, for example `R01-SAC-01`.

## Rubric and score history

Default to **idea-shaokao internal rubric v1** below and label it unofficial.
When the user requests venue-specific assessment or it materially helps the task,
use the venue's official rubric only after verifying the venue/year and current
public instructions. Save the source, access date, scale anchors, and applicable
stage. If unavailable, retain the internal rubric and disclose the gap. Do not
infer a current venue scale from memory.

| Dimension | Internal scale |
| --- | --- |
| Novelty, technical quality, experimental quality, significance, clarity | 1: serious deficiency; 2: weak; 3: mixed; 4: strong; 5: exceptional |
| Overall recommendation | 1–2: strongly unfavorable; 3–4: unfavorable; 5–6: borderline; 7–8: favorable; 9–10: strongly favorable |
| Reviewer confidence | 1: little relevant evidence/expertise; 2: limited; 3: moderate; 4: substantial; 5: deep and directly supported |

At proposal stage, experimental quality measures the plan, not obtained results;
overall favorability means worth investigating. A high-confidence review still
requires supporting evidence. Use `not assessable` rather than a fabricated score
when material is missing. Do not compare numeric scores across different rubrics
or stages as if their meanings were unchanged.

Track reviewer, round, stage, rubric, initial score, final score, confidence, and
reason for change in `reviews/score-history.md`. Score movement is diagnostic,
not an optimization target or convergence criterion.

## Rebuttal and issue closure

Rebuttal table:

| Issue ID / reviewer | Concern | Author response | Evidence | Change made or planned | Remaining uncertainty |
| --- | --- | --- | --- | --- | --- |

Maintain `issue_tracker.md` with ID, source, claim, severity, resolution criterion,
owner, response, evidence path/source, status, and reviewer/chair disposition.

| Severity | Meaning |
| --- | --- |
| Critical | Threatens the core novelty, validity, feasibility, or ability to test the idea |
| Major | Substantially weakens contribution, correctness, or evidential credibility |
| Moderate | Material improvement that does not invalidate the central contribution |
| Minor | Presentation or local detail |

Use statuses `Open`, `Partially resolved`, `Pending experiment`, `Resolved`, or
`Rejected with justification`. Closure requires the resolution criterion to be
met and reviewer or chair verification. Rejecting a concern requires a recorded
reason and AC/SAC assessment, not the author's unilateral dismissal. A promised
experiment remains pending; an inaccessible source cannot close a novelty dispute.
Do not downgrade severity or narrow claims merely to hide a surviving fatal flaw.
Legitimate scope changes must be explicit and re-reviewed.

## Convergence and stopping

The default ceiling is four full rounds for one idea; honor a smaller user budget.
Rebuttal and discussion are parts of a round, not extra review rounds. A single
round can support a preliminary next step, but cannot establish convergence.

Declare **converged at the stated stage** only when all are true:

- Two consecutive completed independent rounds on the same core idea and stage
  produced no new critical issue. A fundamental redesign resets this streak.
- No critical issue remains unresolved, partially resolved, or pending experiment;
  AC and SAC substantiate that no fatal novelty or technical flaw remains.
- Core claims are scoped to the available evidence, hypotheses have decisive
  tests, the essential experiments are adequate, and implementation is feasible.
- Major objections have evidence-based dispositions; remaining uncertainties and
  disagreements are preserved with owners and next actions.

At proposal stage, empirical unknowns can remain explicitly unvalidated when they
do not prevent a sound research plan. Their existence still limits any claim of
paper readiness. Convergence does not require unanimous favorable scores.

The SAC chooses a recommendation after each round:

| Recommendation | Consequence |
| --- | --- |
| Proceed | Advance to the next concrete stage or experiment, with remaining conditions; state whether convergence was actually met |
| Revise | Address identified flaws within the remaining budget; specify the substantive change needed |
| Restart | The current formulation lacks a defensible path; preserve rejected candidates and recommend a new ideation cycle, without automatically starting it |
| Kill | Stop this idea, record the decisive evidence and reusable lessons |

Consider early Restart/Kill when prior work covers the contribution, an essential
assumption fails, feasibility or compute requirements defeat the constraints, no
experiment can test the claim, or substantive revisions do not remove fatal flaws.
Do not spend remaining rounds to manufacture agreement.

At the round/resource ceiling, finish with a candid verdict and unresolved issues.
If unconverged, record `not_converged` and specify a fundamental revision, Restart,
or Kill. A fundamental revision is a proposed next action, not permission to silently reset the budget
and continue indefinitely. If tools or evidence prevent completion, report the
incomplete stage and resumable next step without inventing a SAC assessment.
