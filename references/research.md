# Research and design contracts

## Literature discovery

Start with the user's material and search outward through citations, competing
methods, official proceedings, preprints, and implementation repositories. Include
foundational results, representative work from the last two to three years, and
new work that could invalidate novelty. Search by problem, mechanism, and adjacent
terminology so renaming an existing technique cannot look like novelty.

Record search date, queries, sources searched, coverage boundaries, and access
failures in `literature/search_log.md`. If a source is inaccessible, record that
limitation and use the accessible evidence at its actual depth. An abstract-only
read cannot establish that a paper lacks a particular mechanism.

Keep a source ledger in `literature/papers.md`:

| ID | Title, authors, year | DOI or primary URL | Version / access date | Sections inspected | Relevant finding | Evidence limits |
| --- | --- | --- | --- | --- | --- | --- |

Verify bibliographic details and claim support against the source. Distinguish
peer-reviewed work from preprints and implementation claims from measured results.
Use exact page, section, equation, or repository locations for important disputes.
Treat a claimed absence of prior work as a bounded search conclusion, not proof.

In `literature/research_landscape.md`, explain the problem families, technical
approaches, bottlenecks, questionable assumptions, saturated directions, and
underexplored design space. Identify the current leading methods only for a
specified task, metric, evaluation setup, and date.

Build `literature/related_work_matrix.md`:

| Source ID | Problem | Mechanism | Assumptions | Evidence | Strengths | Limitations | Exact overlap / difference |
| --- | --- | --- | --- | --- | --- | --- | --- |

Deeply compare the closest five to ten works when that many are relevant and
accessible. A smaller well-supported set is preferable to unrelated filler.
Separate a missing evaluation from a demonstrated failure of the prior method.

## Candidate discovery and selection

For open-ended research, write at least three distinct candidates to
`ideation/candidate_ideas.md`. Each needs a motivation, gap, core insight, problem
formulation, mechanism, closest work, concrete novelty claim, feasibility, potential
impact, and a falsifying experiment. Include the strongest objection to each.

Favor a new problem formulation, mechanism, abstraction, objective, or explanatory
insight over a combination of fashionable components without a testable benefit.
Do not manufacture alternatives merely to replace a user's selected idea; for that
scope, compare the idea with close work and simpler alternatives instead.

Compare candidates on novelty, significance, technical risk, falsifiability,
resource needs, and time to the first decisive result. Explain the tradeoff in
`ideation/idea_selection.md`; an arbitrary weighted score cannot establish novelty.
If none is credible, identify what evidence or new direction is needed and honor
the research budget before searching again.

## Technical submission

In `proposal/v01/proposal.md` (then `v02`, etc.), include:

- Title, abstract, motivation, and expected contribution at the current evidence stage.
- Problem variables, objective, constraints, assumptions, and scope of validity.
- Core insight and a causal explanation of why it might help.
- Method, architecture, component interactions, data/execution flow, and pseudocode
  or equations sufficient to guide implementation.
- A direct comparison with the closest method and a credible simple alternative.
- Technical stack, modules, dependencies, implementation order, compute/memory
  needs, and development estimates with stated assumptions.
- Relevant complexity, latency/throughput, scalability, stability, or generalization
  analysis; distinguish derivations from conjectures.
- Failure conditions, limitations, references, and unresolved claims.

Keep the corresponding experiment plan and evidence inventory in the same version
directory. If actual code exists, identify its revision and the tests inspected.
Freeze these files when reviewed; write changes into the next version, not over
the submitted record. Use `changes.md` to connect edits to issue IDs and evidence.

## Research story and paper design

For a developed proposal, save `proposal/vNN/paper_plan.md` alongside the method
and experiment plan. Explain the complete narrative: problem, gap in the closest
work, core insight, mechanism, evidence chain, intended contribution, and limits.
Make clear which links are hypotheses and which have evidence.

Design the manuscript section by section rather than listing generic headings:

| Section | Purpose | Concrete design | Evidence / figures | Linked hypotheses / experiments |
| --- | --- | --- | --- | --- |

Specify the argument, method details, analysis, comparisons, tables, and figures
each section needs. Link stable experiment IDs to the claims they would test.
Keep planned figures and expected observations distinct from completed results.
Cover the abstract, introduction, related work, formulation/method, experimental
design/results, analysis, limitations, and conclusion as appropriate to the work.
Record unfinished literature, unperformed experiments, and missing decisions.
Freeze the writing plan with the submitted version and retain its provenance in
`proposal/final/`. For a killed or narrowly scoped review, preserve the actual
story and explain why a manuscript design was not produced; do not invent one.

## Experiment design and execution

Give hypotheses and experiments stable identifiers (`H01`, `E01`). For each planned
experiment in `proposal/vNN/experiments.md`, record:

| Field | Required decision |
| --- | --- |
| Hypothesis / claim | What would the result support or falsify? |
| Priority | Essential, Core, Supporting, or Optional |
| Setup | Dataset/workload version, split, model/configuration, hardware, seeds |
| Comparators | Closest work, strong baseline, and a simple baseline |
| Fairness | Equal tuning/compute budgets, preprocessing, access to information |
| Measurements | Primary metric, units, uncertainty, success/kill threshold |
| Controls | Ablations, confounders, leakage checks, mechanism checks |
| Coverage | Scaling, distribution shift, stress tests, failure boundaries |
| Interpretation | Expected observation, negative result, alternative explanation |
| Execution | Command or implementation task, dependencies, resource/time estimate |

Choose thresholds before looking at results and justify them from the research
claim. Do not invent benchmark numbers as factual baselines. Use repeated runs,
confidence intervals, or other uncertainty estimates appropriate to the claim;
state when cost prevents them. Tune all methods fairly and preserve held-out data.

Prioritize the cheapest decisive test, then the evidence needed for the central
claim, then supplementary coverage. Name exactly three essential experiments in
the final recommendation; they may test the mechanism, closest/simple baseline,
and robustness boundary. If fewer are scientifically warranted for a narrow
task, explain why rather than add filler.

For actual runs, save `experiments/<run-id>/` with command, code revision or content
identifier, environment/dependencies, data version, seed/config, raw logs,
measurements, resource use, and outcome (including failures). Do not declare a
run complete without its outputs. Keep planned, running, failed, and completed
experiments distinct. A local toy test supports only its tested setting.

Refresh the novelty search each review round and whenever the method changes.
If browsing is unavailable, carry forward the explicit novelty uncertainty.
