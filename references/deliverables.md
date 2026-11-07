# Final report contract

Write `final/final_report.md` as an English report with a short decision at the top,
then the sections below. Link detailed artifacts rather than copying every review
into the report. The linked history must remain available. For a scoped review,
retain the relevant sections and mark unperformed phases explicitly.

## Decision header

State the idea, review stage, execution mode, recommendation (Proceed / Revise /
Restart / Kill), convergence status, rounds completed / allowed, source coverage
date, and the most important unresolved uncertainty. A budget stop is not success.

## A. Research discovery

Executive summary; landscape; verified literature review and related-work matrix;
research gaps; distinct candidates if ideation was in scope; selection rationale
and strongest competing explanation. Explain what is known and what was inferred.

## B. Final proposal

Title, abstract, introduction/motivation, precise problem, core insight, proposed
method, architecture/algorithm, relevant theoretical or systems analysis, closest
work comparison, and limitations. Link `proposal/final/` to the selected immutable
version or copy that version with its identity recorded. Do not label an unreviewed
last-minute edit as the reviewed final proposal.

## C. Experimental plan and evidence

Hypotheses, data/workloads, baselines, metrics, main experiments, ablations,
scalability/stress tests, and essential experiments. Explain expected observations,
negative outcomes, and alternative interpretations. Separate the planned work
from completed runs; link raw evidence for any experimentally validated claim.

## D. Complete review history

Link each initial report, AC discussion, author rebuttal, post-rebuttal response,
AC meta-review, and SAC assessment. Include a compact score-evolution table with
rubric/stage, reviewer, round, initial score, final score, and reason for change.
Include review provenance, major issue resolutions and evidence, pending
experiments, dissent, and missing roles. Never fabricate history to fill a table.

## E. Implementation roadmap

| Stage | Task | Dependencies | Priority | Expected artifact | Effort / resource estimate |
| --- | --- | --- | --- | --- | --- |

Cover prototype, core implementation, baselines, main experiments, ablations,
analysis, and writing as relevant. State first-week priorities, the first component
to implement, decisive go/no-go experiments, tasks that can run in parallel, and
the leading engineering/research risks. Estimates are assumptions, not guarantees.

## F. Final SAC verdict

If an independent SAC participated, preserve its recommendation and reasoning
without rewriting an unfavorable assessment. Otherwise title this section
**Author assessment — no independent SAC**. Answer:

1. **Final idea:** What precisely is being proposed?
2. **Core novelty:** What mechanism or insight is new, and with what confidence?
3. **Why now:** Which evidence or enabling change makes the work timely?
4. **Why not existing work:** What is the closest overlap and substantive difference?
5. **Conference potential:** What is plausible at this stage, and what evidence is missing?
6. **Biggest rejection risk:** What is most likely to defeat the central claim?
7. **Three essential experiments:** What tests most directly decide whether to continue?
8. **First implementation step:** What concrete task should begin next?
9. **Final recommendation:** Proceed, Revise, Restart, or Kill, with rationale and confidence.

## Interactive review report

After saving the real research artifacts and checkpoint, follow
[review-report.md](review-report.md) to write the sourced display index and run
the bundled renderer. Every persisted run delivers `final/review.html` alongside
this Markdown report, including negative and incomplete outcomes. Use the approved
GitHub Issues-style assets, with actual issue discussions, all recorded rounds,
source documents, and honest missing-data states. Preserve the report manifest
for stable annotations and feedback export on later versions.

## Delivery check

Before handing off, verify that important references resolve, factual claims have
support, expectations are not presented as measurements, scores have identifiable
authors, and unresolved critical issues remain visible. Check that the stated
convergence follows the actual history and budget. Ensure the checkpoint matches
the delivered artifacts and records the exact next action, even after Kill or a
budget stop. Link `final/review.html`, this report, and the workspace in the
final user-facing response. If HTML generation is unavailable, report it as pending
rather than declaring the full delivery complete.
