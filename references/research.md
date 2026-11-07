# Scientific discovery and complete-paper contract

## Literature-grounded discovery

Investigate foundational papers, recent top-conference papers, relevant journals,
recent preprints, concurrent work, closest competitors and adjacent disciplines.
Search by problem, mechanism, mathematical formulation, assumptions and synonyms.
Record every query/provider/date, coverage category, result and access failure.
Abstract-only reads cannot establish that a mechanism is absent from prior work.

Each important paper records its primary URL, version/location inspected, problem,
main insight, methodology, assumptions, results, limitations, relation to the
proposal and exact contribution difference. Separate established knowledge,
underexplored existing approaches, evidenced research gaps and unvalidated
hypotheses. Build a literature map and closely compare the strongest competitors.
Do not pad a paper count or treat no direct search match as proof of novelty.
Prior-art PASS requires successful closest/concurrent searches and full-text
inspection of the closest registered work. Adversaries can add discovered papers
with the same evidence contract.

## Insight-driven composition

Every idea develops these connected arguments, not disconnected checklist labels:

1. Important problem and why solving it would matter.
2. Fundamental limitation in current paradigms and the assumptions causing it.
3. Overlooked, non-obvious observation with evidence or a testable conjecture.
4. Key scientific insight and why it changes the research direction.
5. Falsifiable hypothesis with a decisive negative outcome.
6. Novel mechanism arising from the insight.
7. Precise difference from the closest methods and equivalent formulations.
8. Expected scientific contribution, scope and possible new capability/understanding.
9. Experimental/theoretical validation and explicit failure conditions.

Compare substantively different candidates, including the strongest objection to
each. The engine requires at least two alternatives to the selected candidate.
Classify contribution as **1 engineering**, **2 incremental**, **3 significant
research**, or **4 potentially paradigm-shifting**. Pursue 3–4 primarily. A lower
level requires an explicit scientific case under the venue/type standards. An
ambitious name, useful implementation, familiar-technique combination, new dataset
or small benchmark gain does not establish a deeper contribution by itself.
Legitimate incremental/negative/theory/concept contributions must be assessed
using their actual venue category, not a universal leaderboard expectation.

## Complete paper before every review

The author supplies a precise title plus these thirteen developed body sections.
The prose must be coherent enough for an expert to evaluate the contribution;
section outlines, task lists and prose-length checks alone do not establish quality.

| Section | Scientific content |
| --- | --- |
| Abstract | Problem, motivation, insight, mechanism, hypothetical expected results and contribution |
| Introduction | Importance, limitation, non-obvious insight, hypothesis and precise claims |
| Related Work | Research directions and exact closest-work comparisons, with references |
| Problem Formulation | Variables, inputs/outputs, assumptions, objectives, constraints and mathematical formulation where appropriate |
| Key Insight and Research Hypothesis | Scientific reasoning and falsifiable propositions |
| Proposed Method | Mechanism and why it addresses the limitation |
| Technical Design | Architecture, algorithms, equations/objectives, training/inference, complexity and resources |
| Theoretical Analysis | Relevant derivations, propositions, complexity or reason formal theory is inapplicable; no invented theorems |
| Experimental Design | Questions, datasets, baselines, metrics, protocols, ablations, robustness, statistics and reproducibility |
| Expected Results and Quantitative Predictions | Mandatory hypothetical estimates, rationale, uncertainty, assumptions and failure conditions |
| Expected Contributions | Methodological novelty, theory, empirical insight and practical value distinguished |
| Limitations and Risks | Scientific uncertainty, implementation risk, alternative explanations and validity boundaries |
| Conclusion | Research thesis and expected significance, qualified to the evidence |

Use academic paragraphs, consistent notation, equations, diagrams when useful and
tables for comparisons/configuration. The Markdown export and UI include prediction
tables and the actual evidence bibliography. Do not conflate the 14-part paper
architecture with a 14-item writing plan.

## Predictions and falsification

For each experiment, record a stable ID and falsifiable hypothesis, data/split,
closest/strong/simple baselines, fairness controls, metrics/units, protocol,
ablations, robustness/generalization, statistical analysis, reproducibility,
resource assumptions and falsification criterion. Choose decision criteria before
observing outcomes and explain why they test the central mechanism.

Every experiment has an expected outcome. Predictions must use `kind: hypothetical`,
state an estimated baseline, metric, numerical range/units where reasonable,
assumptions, calibration rationale, evidence IDs and failure condition. If an
estimate lacks source support, explicitly warn that it is speculative. If a
quantitative forecast is unreasonable, explain why and give a decisive qualitative
outcome instead. Conservative/expected/optimistic scenarios may be added when
useful, but finite uncertainty ranges and negative possibilities are essential.

Never convert a prediction into an observed effect. Recalibrate implausible
forecasts instead of treating ambition as evidence. Reviewers must ask whether the
planned experiments can distinguish the mechanism from simpler alternatives and
whether even favorable results would substantiate the scientific contribution.

The engine is proposal-stage: it does not execute real experiments or certify
completed empirical papers. Existing external measurements need separately
verified run artifacts, code/data versions and uncertainty; do not smuggle them
into hypothetical prediction records. The legacy report can still display actual
sourced experiment artifacts when they exist.
