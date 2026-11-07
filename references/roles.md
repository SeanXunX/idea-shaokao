# Role contracts and context boundaries

The executable briefs live in `scripts/shaokao/prompts.py`; validators live in
`contracts.py`. Native packets carry the brief, relevant context and output schema.
The author cannot set reviewers' scores or make a chair ratify acceptance.

## Research roles

**Literature Investigator** searches seven evidence categories, records queries,
dates, provider failures, reading depth and a structured map. Every important
paper records problem, insight, methodology, assumptions, results, limitations,
relationship and exact contribution difference, with primary URL and locator.

**Idea Composer** compares distinct insights, classifies contribution levels and
constructs the complete insight-to-validation chain. Scientific significance and
novelty outrank convenience. Lower-level contributions require venue justification.

**Author** writes a complete paper before review, with detailed technical design,
falsifiable hypotheses and explicitly hypothetical quantitative predictions. It
responds individually by concern ID and substantially revises the research when
criticism is valid. It cannot close issues by declaration or change frozen papers.

## Mandatory independent novelty adversaries

Give each the same paper, idea, evidence map and venue rubric in a fresh context.
No adversary receives peers' verdicts before submitting.

| Role | Required challenge |
| --- | --- |
| A: Prior-Art Investigator | Existing/concurrent/adjacent equivalent mechanisms, formulations and claims; rebranding, recombination and incremental overlap |
| B: Conceptual Novelty Critic | Non-obviousness, falsifiable insight, hypothesis-to-mechanism logic, component removal and new capability/understanding |
| C: Top-Conference Skeptic | Problem importance, contribution magnitude, venue/type fit, decisive experiments, future influence and strongest rejection case |

Each report contains claim summary, claimed novelty, closest work, overlap
evidence, insight weaknesses, significance weaknesses, rejection arguments,
required defensive evidence, rationale and PASS / CONDITIONAL PASS / FAIL.
A also provides a prior-art comparison table with registered evidence IDs and
exact locations. Newly discovered papers may be supplied as `discovered_papers`
with the complete evidence schema; do not discard discoveries because they were
absent from the author's ledger. Prior-art PASS requires successful closest and
concurrent searches and full-text inspection of the closest registered work.

Major concerns retain stable IDs. Fundamental overlap must receive evidence or a
changed hypothesis/mechanism/scope, not rewritten motivation. Only three PASS
verdicts permit submission after the author's response. Conditional/fail repeats
investigation, idea composition, paper and all adversaries, within the stress cap.

## Formal reviewers

Dispatch 3–4 separate initial contexts from the same frozen submission packet.
They do not receive private author reasoning, prior-round scores or peer reports.
With three reviewers, significance/fit is assigned to R1 and R3 explicitly.

| Role | Expertise and priority |
| --- | --- |
| R1 | Precise novelty, close prior art, non-obvious insight and research significance |
| R2 | Technical correctness, assumptions, mathematics, mechanisms, complexity and counterexamples |
| R3 | Experimental rigor, fair/strong/simple baselines, statistics, reproducibility, prediction plausibility and significance |
| R4 | Overall contribution, completeness, narrative, venue/type fit, limitations and broader effects |

Follow only actual official review fields/options. Supplementary scientific
concerns and evidence justifications are labeled internal. Every choice score
needs evidence; overall recommendation is an independent judgment, never an
average. Reject unsubstantiated ambition, superficial combinations and implausible
predictions. Do not demand favorable scores or force reviewers to change them.

After the rebuttal, each reviewer reassesses every original concern, returns exact
updated scores, explains changes/no changes, and retains uncertainty. Reuse that
reviewer's own session or a documented fresh replacement; never an author or peer
session. Expose shared reports only after the initial-review barrier.

## Chairs

**AC** inspects the complete paper, all initial/final reviews, rebuttal, exchanges,
major novelty issues, disagreements and evidence. It assesses review quality,
rebuts unsupported reviewer objections, adjudicates each concern and provides an
independent meta-review and venue-authorized recommendation. No score averaging.

**SAC / internal senior audit** receives the full record and AC meta-review in a
fresh context. It audits reasoning, score/text consistency, missing evidence,
borderline cases, dissent and readiness. It can disagree with the AC. The extra
per-paper final-readiness audit is internal if the actual venue does not assign
that authority. Use actual official decision options only when verified.

Both chairs must supply evidence for each readiness criterion and disposition of
all concerns, including major novelty objections and new discussion issues.
A strong-acceptance case cannot accompany a reject/revise recommendation.
Unresolved major/critical concerns or chair disagreement prevent convergence.

## Host isolation

Fresh processes/packets enforce context selection, not filesystem security or
truthfulness of session IDs. The host must enforce read scopes. Do not fork the
author conversation into adversaries or reviewers. Batching/sequential scheduling
of isolated contexts is valid; impersonating several roles in one context is not.
Unavailable independent roles remain pending. `single_agent` is honest self-critique
and cannot produce an independent acceptance-readiness outcome.
