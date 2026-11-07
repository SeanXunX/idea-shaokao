# Research-to-acceptance redesign

## Repository audit

The repository is an installable, provider-neutral Agent Skill. `SKILL.md` routes
to six prose contracts. `init_research.py` creates a schema-1 checkpoint but does
not execute research. `render_review.py` validates a manually written display
index, embeds source text/hashes, and builds an offline HTML report. The frontend
has good source inspection, annotations, and responsive navigation. Design demos
are explicitly illustrative; they are not a workflow backend. Existing Python
and browser tests exercise initialization and report fidelity.

The scientific weaknesses come from optional prior-art adversaries, a universal
internal scoring fallback, no complete-paper requirement, no predictions contract,
and unenforced transitions. Context isolation is described but dispatch is not
implemented. Manual state and display indices can disagree. Convergence describes
investigation readiness rather than an evidenced simulated acceptance assessment.

## Implementation plan

1. Preserve the portable skill and offline report; add a standard-library Python
   engine rather than a provider-specific server. An append-only, hash-linked
   event journal is authoritative; checkpoints are recoverable caches.
2. Fetch official conference sources into versioned snapshots. Extract structured
   OpenReview forms or heading-based HTML fields, validate exact options against
   source evidence, retain historical provenance, and block unavailable criteria.
   Never ship one conference's scores as the universal default.
3. Add contracts for insight chains, structured literature, complete 14-section
   papers, hypothetical quantitative predictions, three independent novelty
   reports/responses, 3–4 blind reviewers, rebuttal, discussion, AC and SAC.
4. Generate role-specific context packets and validate returned outputs. Support
   native-host packet/submit operation and a fresh-process JSON command adapter
   for unattended execution. Failures remain resumable; missing roles cannot pass.
5. Enforce novelty retries, substantive revisions, evidence-linked concern
   dispositions, bounded rounds, and explicit readiness criteria. Preserve dissent
   and unfavorable decisions. Additional chairs are labeled internal when needed.
6. Render structured engine history directly: concise final overview, academic
   prose paper with prediction tables, threaded submission/review cycles, exact
   venue scores, rebuttals, chair decisions, and version comparisons. Retain the
   legacy renderer for existing workspaces and annotation identities.
7. Validate with a real official conference form and deterministic, clearly labeled
   synthetic agent responses. Exercise multi-round success, scientific failures,
   rubric failures, interruption/replay, and browser rendering. Distinguish these
   software checks from a live scientific-quality/model evaluation.
8. Update skill contracts and usage documentation, record limitations and checks,
   then commit and push the reviewed working tree.

## Verification boundaries

Structural validation cannot prove novelty or technical correctness. Independent
packets plus fresh processes enforce dispatch boundaries, not provider cognition
or filesystem security. No real experiments, academic submissions, or external
messages are part of this repository implementation task. A simulated acceptance
must remain explicitly hypothetical and cannot substitute for measured evidence.
