# Agent roles and dispatch contracts

Read this when assigning independent review work. The author coordinates execution;
reviewers and chairs own their judgments. None is rewarded for getting an idea accepted.

## Context boundaries

- Use a fresh, separate agent context for each initial reviewer, AC, and SAC. Do not
  fork the author's private reasoning, preferred verdict, or other reviews into it.
- Give initial reviewers the same frozen submission packet, the relevant role below,
  the review stage, rubric, resource limits, and their own output destination. Let
  each independently retrieve sources when tools permit.
- Initial reviewers must not read other review files, discussion files, or private
  author notes before submitting. A shared filesystem does not provide isolation;
  use explicit read scopes and separate writable destinations. State any limitations.
- The AC receives all initial reports only after every reviewer has submitted.
  The SAC receives the full record after the AC meta-review. Neither receives
  instructions to ratify the author's or another chair's preferred decision.
- Reuse a reviewer's own context for discussion. If it is unavailable, give a fresh
  agent the role, packet, its predecessor's report, and discussion so far; record
  the replacement. Do not silently treat the author's reconstruction as a review.
- With limited concurrency, run fresh reviewers in batches, then AC, then SAC.
  Sequential scheduling of independent contexts preserves initial independence;
  role-playing all agents inside one context does not.

If the host cannot create independent contexts, complete research and explicitly
label any critique **single-agent self-review**. Do not create fictitious reviewer
identities, chair assessments, or an independent-review convergence claim. Save
dispatch packets so a capable host or real reviewers can complete the process.

## Role assignments

| Role | Decision preference | Required investigation | Authority |
| --- | --- | --- | --- |
| Author | A useful, falsifiable contribution | Literature, competing ideas, design, experiments, implementation when in scope | Select and revise the idea; accept or rebut criticism with evidence |
| R1: novelty | Distinct contributions over combinations with new names | Closest prior art, recent preprints, equivalent formulations, missing citations | Challenge novelty; specify the exact overlapping claim and supporting source |
| R2: technical soundness | Valid assumptions and mechanisms over plausible narratives | Counterexamples, boundary conditions, derivations, complexity, simpler alternatives | Identify invalid assumptions and define a decisive technical check |
| R3: experimental rigor | Identifiable evidence over favorable metrics | Strong and simple baselines, equal budgets, leakage, controls, uncertainty, causal alternatives | Identify which experiments are necessary for the claimed conclusion |
| R4: significance | A meaningful problem and transferable value over benchmark increments | Real bottlenecks, beneficiaries, scalability, generalization, costs, broader effects | Challenge importance and scope; identify conditions under which value disappears |
| AC | Contribution relative to evidenced weaknesses | Conflicts, unsupported objections, misunderstandings, minority concerns, rebuttal adequacy | Direct discussion and recommend; never decide by averaging scores |
| SAC | Reliable process and defensible conclusions | Review independence, source quality, missed fatal flaws, AC treatment of disagreement | Uphold or overturn the AC recommendation; require focused re-examination; decide next action |

Use four reviewers when resources allow, and at least three for a complete
independent round. With three, explicitly assign significance and broader-impact
coverage to R1 and R3; do not silently drop that perspective. Preferences guide
attention, not predetermined negative verdicts. All reviewers may raise any material issue.

The optional **red team** does not score or vote. It tries to falsify the central
claim through an overlooked equivalent paper, a counterexample, an unnecessary
component, or a simpler baseline. Preserve unsuccessful falsification attempts as
inconclusive, not confirmation. Deliver findings with sources or reproductions to
the author and AC; disclose them to all reviewers during discussion, or include
them in the next frozen packet. Do not selectively seed initial reviewers.

## Initial reviewer dispatch

Adapt this brief to the host's delegation API; file paths are relative to the run:

```text
Act as R2, the technical-soundness reviewer, for round 01.
Stage: proposal. You are evaluating whether the idea merits implementation.
Read the frozen packet listed in reviews/round-01/submission-manifest.md,
your role in roles.md, and the reporting contract in review-protocol.md.
You may retrieve primary sources within the stated resource limits.
Do not read other reviews, discussions, or private author notes before submission.
Evaluate independently; acceptance is not your objective. Identify evidence and
counterexamples, distinguish untested hypotheses from observed results, and state
what would change your judgment.
Write only reviews/round-01/reviewer-R2-initial.md, then report completion.
```

Include the actual skill resource paths, packet file list, deadline or tool budget,
rubric identifier, and allowed evidence access when dispatching. Never assume a
child inherits the skill or can resolve the parent's relative paths.

## Chair dispatch

For the **AC**, provide the submission packet and all initial reports. First ask
for a bounded discussion agenda: issue ID, disputed proposition, reviewer asked,
and evidence needed. Relay questions to reviewers and preserve their actual
replies. After rebuttal and reassessment, ask for the final meta-review.

For the **SAC**, provide the same packet plus initial and final reports, both
discussion records, rebuttal, issue tracker, and AC meta-review. Ask for an
independent process audit and stage-specific recommendation. The SAC may require
one focused clarification pass on a material omission; if evidence remains absent,
record uncertainty and decide without creating an unbounded discussion loop.

Reviewers and chairs do not edit the submission or another participant's report.
The author owns the aggregate issue tracker and version transitions, while retaining
each participant's original evidence, objections, and decisions.
