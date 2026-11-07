# Enforced conference-style research review

Every assessment is simulated and proposal-stage. Hypothetical quantitative
predictions never establish an empirical result. Formal review requires a complete
paper, a passed independent novelty gate, and a verified exact venue rubric.

## State transitions

```text
verified official rubric
  → literature investigation
  → insight-driven idea composition
  → complete paper and hypothetical predictions
  → three independent novelty adversaries
  → author novelty response
      ├─ conditional/fail: refresh literature → recompose → new paper → repeat
      ├─ cap/abandonment: stop honestly
      └─ three PASS verdicts: freeze formal submission
  → 3–4 blind initial reviews (all must return)
  → individual author rebuttal
  → independent reviewer reassessment
  → additional venue-authorized exchanges, if applicable
  → final justification when the configured exchanges require it
  → independent AC meta-review
  → independent SAC or labeled internal senior audit
      ├─ eligible acceptance streak: simulated acceptance readiness
      ├─ round cap: budget exhausted, acceptance not established
      └─ research revision → next complete round
```

Each round contains the complete paper architecture, predictions, evidence,
novelty reports and response, formal reviews, rebuttal, discussion, chairs and
research transition. Failed novelty attempts are retained inside that round;
formal review cannot run early. Failure does not become a hidden positive vote.

## Scientific contribution and submission

Prefer level-3/4 scientific contributions. Record the entire insight chain,
precise closest-work differences and conditions that would falsify the proposal.
A complete submission includes all sections in [research.md](research.md), a
hypothesis-linked experiment design and plausible, qualified predictions. Do not
review an abstract or substitute a section-writing plan for the actual paper.

Freeze a content-addressed version after the novelty response. Reviews and
rebuttals reference that version. New derivations/evidence may be discussed, but
material mechanism or claim changes belong in the next immutable submission.
Initial reviewers receive the common frozen packet without peers or old scores.

## Exact official review form

Read [conference.md](conference.md). Required official dimensions, score options,
labels, confidence and questions come from the source-linked rubric. No universal
internal scoring fallback exists. A categorical recommendation need not be a
number; numeric scales can be noncontiguous and have arbitrary ranges.

Every answered choice field needs an evidence-based justification. Initial and
updated scores remain distinct; do not normalize them or compute an overall
recommendation by averaging dimensions. A high confidence score does not replace
supporting evidence. Additional issue assessments are internal, not new official
scoring fields. Preserve exact score meanings across rounds and target changes.

## Rebuttal and discussion

Use stable concern IDs and one response per major/critical objection, including
carried novelty concerns. Each response records the answer, evidence, concrete
change, remaining uncertainty and research action. A fundamental objection cannot
be dismissed with revised motivation or additional benchmark plans. Acknowledge
valid limitations and preserve unresolved concerns.

Enforce the actual configured exchange/character limits. The engine separates
bounded discussion comments from updated official score forms. Author response
length includes its summary and individual response content. Do not use hidden
metadata to circumvent the venue's prose limits.

Reviewers individually reassess every original concern with evidence and reasons.
They may keep or change scores; favorable movement is never required. New concerns
are retained through later exchanges and chair adjudication. A proposed experiment
remains unperformed. Reviewers may inspect peer reports only after initial review
is complete. Batched initial reassessment packets remain fixed while peers return.

## Issue disposition and chair authority

Concern severity is `critical`, `major`, `moderate`, or `minor`; `fundamental`
marks an objection to central novelty/hypothesis/significance. Each records claim,
evidence and a concrete resolution criterion. Carry a concern's ID/content/severity
unchanged; create a linked new concern for a substantively different objection.

Authors propose responses. Reviewers and chairs assess resolution. Chairs must
adjudicate every concern, including major novelty concerns and later discussion
findings, as resolved/open/pending with evidence. They cannot ignore minority
objections or blindly average scores. The SAC audits the AC reasoning independently.

Decision labels and authority come from the verified procedure. Extra senior
readiness stages and their options are explicitly internal. An official final
conference decision is never made by this framework. Strong-acceptance cases must
agree with the chair's declared acceptance option, not a reject/revise verdict.
AC/SAC disagreement is preserved and prevents acceptance eligibility.

## Research-level revision

- **Strong acceptance potential:** every readiness criterion is evidenced, both
  chairs support acceptance, major/critical concerns are resolved consistently.
- **Borderline / weak acceptance:** identify the highest-impact unresolved issue
  and revise the scientific proposal.
- **Addressable rejection:** redesign methodology, theory, experiment strategy,
  predictions or positioning around the actual concern IDs.
- **Fundamental failure:** change the core insight/hypothesis, recompose, or abandon;
  do not keep polishing an already-known or invalid contribution.

Revision records describe insight/method changes, removed claims, changed
predictions, motivating concern IDs and surviving uncertainty. A verification-only
round is allowed only after a fully acceptance-eligible assessment. Literature,
complete paper, novelty and formal review still repeat. It does not manufacture
scientific changes to satisfy a round counter.

## Convergence and honest stopping

Both chairs must substantiate each criterion: defensible novelty, meaningful
insight, venue significance, technical soundness, falsifiable experiments,
plausible predictions and no fatal concerns. Both must resolve all major/critical
concerns with evidence and support acceptance. No dimension-score threshold is
used. By default, require two consecutive eligible rounds with the same rubric
and core insight/hypothesis/mechanism; configure this explicitly in the budget.

Repeated novelty failure stops at the configured stress cap. Unresolved critical
issues, incomplete roles, contradictory chair decisions and unavailable official
scales cannot converge. At the research-round cap, stop with `budget_exhausted`
and explain unresolved scientific weaknesses. A new target or restart cannot
reset the budget. Preserve all rejected versions and reusable lessons.

A simulated Accept means competitiveness under the reconstructed process, not
experimental validation, real submission readiness, or guaranteed acceptance.
