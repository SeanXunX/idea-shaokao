---
name: idea-shaokao
description: Develop research directions into complete paper-level proposals through evidence-grounded ideation, adversarial novelty verification, venue-specific independent peer review, rebuttal, chair assessment, and bounded research revision. Use for rigorous research development or resuming a persistent research project; not routine brainstorming or ordinary code review.
---

# Idea Shaokao

Develop a contribution that deserves serious scientific attention. Optimize for
novelty, significance, technical rigor and falsifiability, never an Accept label.
Deliver English research artifacts unless the user requests another language.
Every review and decision is an **internal simulation**, never a real conference
review or a promise of acceptance. Predicted results are hypotheses, not data.

## Start or resume

Infer the research direction, target conference **year and track**, contribution
type, resource constraints and requested scope. Ask only for missing information
that blocks useful work. A venue-free exploration may proceed, but cannot claim
venue-calibrated acceptance. Do not silently choose a year or another venue's form.

Use the standard-library Python engine for persistent full workflows. Read
[workspace.md](references/workspace.md) for commands, dispatch, and recovery.
Create a workspace outside the installed skill:

```bash
python3 <skill-dir>/scripts/research.py init research/<slug> \
  --topic "<research direction>" --conference "<venue>" --year <year> \
  --track "<track>" --max-rounds 4 --max-stress-iterations 3
```

Defaults: four research rounds, three novelty attempts per round, four independent
reviewers, and two consecutive eligible acceptance assessments. Honor explicit
budgets. A restart or venue change never resets the total budget.

Resume with `status` and `verify`, inspect pending tasks and the journal, then
continue the exact pending operation. Never reinitialize a project or edit old
reports to conceal failures. Schema-1 workspaces remain renderable with
`render_review.py`; they are not silently upgraded into validated schema-2 runs.

## Fetch and verify the venue rubric

Before each new project and whenever the venue/year/track changes, retrieve
current official reviewer guidelines, review form, author response instructions,
AC/SAC instructions and CFP. Read [conference.md](references/conference.md).

Extract exact fields, numerical/categorical options, labels, definitions,
confidence, ethics/limitations questions, contribution types, response limits and
chair authority. Preserve source URLs, retrieval dates, year/track, snapshots,
failures and uncertainty. If current documentation is unavailable, explicitly mark
and justify the latest official historical version. Never silently substitute.

There is **no universal scoring rubric or numerical acceptance threshold**.
Unverified score options cannot launch formal reviewers. Official instructions
may reconstruct the form when an authenticated OpenReview schema is unavailable;
label the reconstruction and unknown required/optional fields. Extra workflow
steps, especially a senior final-readiness audit, must be labeled internal when
the venue does not assign that authority.

## Research and complete-paper composition

Read [research.md](references/research.md). The literature investigator maps
foundational, recent conference, journal, preprint, concurrent, closest, and
adjacent work, recording unsuccessful searches and actual reading depth.

The idea composer compares distinct insights and builds:

**Important problem → fundamental limitation → non-obvious observation → key
insight → falsifiable hypothesis → novel mechanism → scientific contribution →
experimental validation.**

Classify contributions as engineering (1), incremental (2), significant research
(3), or potentially paradigm-shifting (4). Prefer 3–4. Lower levels require a
venue-specific scientific justification. Feasibility, renamed components, dataset
changes, and marginal gains alone do not establish a contribution. Novelty claims
must cite exact differences from the closest work; search silence is not proof.

Before every formal review, the author writes the **complete paper**, with title,
abstract, introduction, related work, formulation, insight/hypothesis, method,
technical design, appropriate theoretical analysis, experimental design,
**hypothetical quantitative predictions**, contributions, limitations and conclusion.
Use coherent academic prose, equations and comparison/prediction tables; a paper
outline is insufficient. Never fabricate implemented methods or measured results.

## Mandatory novelty gate

Dispatch three fresh, independent adversaries before formal review:

- **A — Prior-Art Investigator:** overlapping mechanisms, hypotheses, formulations,
  concurrent and adjacent work; evidence-linked comparison table.
- **B — Conceptual Critic:** non-obvious insight, logical mechanism, component
  removal, new abstractions/capabilities, superficial combinations.
- **C — Conference Skeptic:** significance, venue/type fit, strongest rejection
  case, decisive validation and potential influence.

Each returns the nine-part report in [roles.md](references/roles.md). Collect all
three before the author sees peer judgments. PASS means no fatal issue identified,
never proof of novelty. Conditional PASS or FAIL requires a new literature/idea/
paper cycle and a repeated independent test. The author responds individually to
major concerns; fundamental novelty requires evidence or research recomposition,
not polished motivation or more benchmark experiments. Stop and recommend
abandonment at the stress cap. Preserve every attempt and response.

## Independent conference review and refinement

Read [review-protocol.md](references/review-protocol.md) and
[roles.md](references/roles.md) before dispatching. Use the engine's `packet` and
`submit` commands, or the JSON fresh-process `run` adapter.

1. Freeze the complete paper, evidence, predictions, novelty record and rubric.
2. Collect all 3–4 independent initial reviews, covering novelty/significance,
   soundness, experiments and fit. Never expose peers or previous-round scores
   before initial scoring. Give every score an evidence-based justification.
3. Author responds to individual major/critical concerns within actual venue limits.
4. Reviewers independently reassess; preserve initial and updated exact scores,
   unresolved objections and reasons for change/no change. Follow the venue's
   permitted exchanges and final-justification requirements.
5. The AC assesses the entire record, disagreements and review quality without
   averaging scores. The independent SAC/senior audit inspects the AC reasoning,
   score/text consistency, unresolved concerns and complete history.
6. Strong acceptance potential must satisfy every readiness criterion and both
   chairs' acceptance recommendations. Borderline or addressable rejection
   initiates substantive revision. Fundamental failure requires a different
   insight or abandonment. Refresh evidence and submit a new complete paper.

Native isolated agents or attributable external sessions are required for
independent gates. Queue them when concurrency is limited. Fresh packets do not
provide an OS security boundary: the host must enforce read scopes and truthful
session provenance. If only one context exists, label work **self-critique**,
export pending packets, and never fabricate reviewers or independent convergence.
Do not launch a paid provider or external communication without existing scope.

## Stop, report, and deliver

Acceptance readiness requires defensible novelty, meaningful insight, venue
significance, sound methodology, falsifiable experiments, plausible qualified
predictions, and no unresolved fatal concerns. Both chairs must evidence these
judgments and agree on every major/critical disposition. By default, two eligible
rounds must share the same rubric and core hypothesis/mechanism. No averaging,
score inflation, automatic acceptance or silent budget extension is allowed.

At the cap, report **budget exhausted / acceptance not established**. At repeated
novelty failure, report abandonment and decisive objections. A simulated Accept
means only competitiveness under the reconstructed process; real experiments
and real conference review remain unperformed.

For every persisted run, including incomplete and negative outcomes, execute:

```bash
python3 <skill-dir>/scripts/research.py render research/<slug>
```

Deliver `final/review.html`, `final/paper.md` when available, and
`final/final_report.md`. The UI has **Overview**, **Final Paper**, and **Review
Process**, rendering actual journal records with version comparisons, exact venue
scores, threaded responses, sources and persistent annotations. Follow
[deliverables.md](references/deliverables.md) for the final handoff. If execution or
filesystem tools are unavailable, provide the actual artifacts inline and a precise
continuation checkpoint; do not claim that omitted stages or saved files exist.
