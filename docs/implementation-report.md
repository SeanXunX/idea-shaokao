# Research-to-acceptance implementation report

Implemented and validated on 2026-11-07. This is a software redesign of the skill,
not a claim that a model has discovered a novel, acceptance-level research result.

## Repository architecture and original weaknesses

The original repository was a provider-neutral Agent Skill, a workspace initializer,
a sourced offline report renderer, and design examples. Research orchestration was
entirely prose. Existing source inspection, immutable-source hashes, annotations,
responsive navigation and legacy tests were useful and have been retained.

The audit found that adversarial novelty was optional, the default review rubric
was universal/unofficial, a paper outline could substitute for a complete paper,
predictions had no required structure, and manual checkpoints/display indices
could not enforce missing stages or independent-role barriers. Convergence meant
investigation readiness, not evidenced simulated competitiveness. The old overview
also emphasized process and metadata, while the final plan was a writing outline.
The pre-implementation audit and plan are in [redesign-plan.md](redesign-plan.md).

## Architectural decisions and modified components

| Component | Files | Behavior |
| --- | --- | --- |
| Portable entrypoint | `SKILL.md`, `README.md`, `references/*` | Routes full research through the engine and role-specific contracts; removes universal rubric fallback; documents capability limits and legacy compatibility |
| CLI / unattended driver | `scripts/research.py` | Init, status, replay/verify, packet, submit, fresh-process run, target/category selection, official-source acquisition, rubric extraction/build/install, render |
| Artifact contracts | `scripts/shaokao/contracts.py` | Literature/evidence, insight chain and contribution levels, complete paper, hypothetical forecasts, novelty reports, official reviews, rebuttals, concerns and chair readiness |
| Official venue configuration | `scripts/shaokao/conference.py`, `examples/icml2026-*` | Versioned HTTPS sources, exact-domain allowlist, failed requests, raw/text hashes, HTML/OpenReview form extraction, exact option validation, explicit historical uncertainty and authority |
| Workflow / persistence | `scripts/shaokao/engine.py` | Append-only atomic journal, replayable state, immutable task/paper hashes, independent-role session checks, barriers, novelty retries, research revision, bounded convergence and honest stopping |
| Agent briefs | `scripts/shaokao/prompts.py` | Distinct investigator, composer, author, three adversaries, four reviewer specialties, discussion, AC and senior-audit prompts and output contracts |
| Derived paper/report | `scripts/shaokao/report.py`, `scripts/render_review.py` | Actual journal-to-HTML normalization, complete Markdown paper with bibliography/prediction tables, summary/report, stable annotation identity; legacy renderer remains available |
| Frontend | `assets/review/research.js`, `styles.css` | Concise Overview, academic Final Paper, threaded Review Process, exact scores, complete submissions, comparisons, source reader, notes and honest missing stages |
| Offline mathematics | `assets/review/vendor/katex/*` | Pinned KaTeX 0.19.1 runtime, WOFF2 fonts, MIT license and integrity manifest embedded into standalone reports; no CDN requests |
| Software validation | `tests/test_research_engine.py`, `engine_fixture.py`, `fixture_agent.py`, `verify_research_browser.cjs`, official-source fixture | Multi-round orchestration and scientific/error invariants with explicitly synthetic agent responses; retains all legacy tests |
| Reviewable example | `design-demos/research-workspace.html`, `src/build_workspace_demo.py` | Generated through the actual engine using clearly labeled synthetic data; archived design explorations remain separate |

A standard-library engine preserves installation portability and avoids a
provider-specific service. A native host executes isolated agent packets with its
own tools; an optional JSON stdin/stdout command adapter supports unattended use.
No model provider, paid inference, credentials or runtime agent CLI is assumed.

## Research composition, novelty and complete papers

Ideas record the complete problem → limitation → observation → insight →
hypothesis → mechanism → contribution → validation chain, exact prior-work
differences and falsification conditions. Four contribution levels distinguish
engineering, incremental, significant and potentially paradigm-shifting work;
lower levels require venue-specific justification.

The investigator records seven literature categories, queries, failures, primary
references, bibliographic metadata, access depth and structured comparisons.
Closest/concurrent investigation and full-text closest-work inspection are required
for prior-art PASS. Adversaries can register newly discovered papers rather than
being restricted to the author's original evidence ledger.

Every paper has a title and thirteen developed body sections, detailed experimental
contracts and explicitly hypothetical outcomes for every experiment. Forecasts
include finite ranges/units where reasonable, estimated baselines, evidence or
unsupported-estimate warnings, assumptions, rationale and failure conditions.
Theoretical analysis may explain inapplicability; no theorem is fabricated.
Structural checks reject empty outlines but do not pretend to evaluate prose merit.

Three fresh novelty adversaries return separate reports and verdicts. Only three
PASS reports plus an individual author response allow formal submission. Conditional
or failed verdicts repeat investigation, composition, the complete paper and all
adversaries. Repeated failures stop at the configured cap. Fundamental criticism
requires evidence or changed research, not polished motivation or extra benchmarks.
Every attempt survives in the journal and interface.

## Conference-specific review and iteration

Official configuration includes the exact conference/year/track, source retrievals,
field names/options/definitions, confidence, questions, response exchanges/limits,
chair authority, historical status and uncertainty. Optional contribution categories
can be evidence-linked and must be selected before installing a categorized rubric.
Review packets freeze that choice per round. There is no universal scale or numeric
acceptance cutoff; categorical and noncontiguous numeric choices are supported.

Three or four initial reviewers receive the same frozen submission and their
own specialty, without peer reports or prior-round scores. The complete-review
barrier precedes rebuttal. Individual responses reference stable concerns; reviewers
reassess independently with unchanged or updated official scores and reasons.
Configured author/reviewer exchanges and final justifications are preserved.
Both chairs assess the complete record and all concerns, including novelty,
discussion and chair-originated issues. Dissent and unfavorable assessments survive.

Strong acceptance eligibility requires both chair recommendations to agree with
an acceptance option, all readiness criteria to have evidence, and consistent
resolution of every major/critical concern. A new senior concern without AC coverage
cannot pass. Consecutive eligible rounds must share the rubric and core insight,
hypothesis and mechanism. Borderline/addressable/fundamental cases drive research
revision or recomposition within the unchanged total budget. The default is four
research rounds, three novelty attempts, four reviewers and two eligible rounds.

## Versioned data and recovery

The journal stores Research Project, frozen Conference Configuration, Research
Idea, Literature Evidence, Novelty Attempts, Paper Versions/Submissions, Reviewer
Profiles, initial/final Reports and Scores, individual Rebuttals, Discussions,
AC Meta-Reviews, SAC Assessments, Round predecessors and final selected proposal.
Each role output carries round/task/paper/context identity, session and timestamp.
Predictions, simulated reviews and real conference decisions are not conflated.
The engine's evidence stage is proposal; it does not manufacture measured results.

One complete event is fsynced and exclusively linked into its sequence name.
The entire transition and concern invariants are preflighted before that write.
A competing commit is rejected. Journal replay rebuilds missing/corrupt checkpoints;
hash/sequence corruption blocks recovery with an explicit error. Interrupted roles
remain pending. Finished outputs cannot be overwritten, and unreviewed new drafts
cannot silently replace the selected submitted paper on the final overview.

## Verification results

- **59 Python tests passed**, including all 26 retained legacy cases and 33 new
  engine/conference tests. These cover complete two-round execution, three/four
  reviewers, exact scores, hypothetical estimates, novelty recomposition/caps,
  individual responses/limits, fatal overlap, implausible forecasts flagged by a
  reviewer, disagreement, chair contradictions, category/target changes, source
  failures, new chair concerns, immutable versions, replay and concurrency.
- **Fresh-process adapter passed** a complete two-round workflow after an injected
  command failure. Native packet/submit was also independently exercised.
- **Both Playwright suites passed.** The new interface checks all three views,
  thirteen complete body sections plus title/references, math/MathML, prediction
  ranges, actual venue labels, threaded responses, source hashes, side-by-side
  versions, annotations and safe escaped content. Routes were checked at 1440,
  1024, 768 and 390 pixels, offline, with no browser errors or HTTP requests.
  Desktop and mobile screenshots were visually inspected and mobile controls fixed.
- **Live official-source integration passed** in a newly initialized ICML 2026
  Main Track project: reviewer/form instructions, AC, SAC, author and CFP pages
  fetched successfully; the OpenReview invitation returned HTTP 403 and its failure
  was preserved. The source-linked rubric built, installed, and advanced only to
  the pending literature task. No research or review was invented in that project.
- **Independent forward testing** found five original issues and two additional
  recovery issues. Regressions cover chair-label contradictions, dropped novelty
  concerns, follow-up session reuse, mutable batched contexts, cross-target streaks,
  new senior concerns and changed carried IDs. The independent agent rechecked all
  five original fixes and confirmed both recovery fixes separately.
- **Skill validation passed** using the skill-creator validator; Python compilation,
  JavaScript syntax and `git diff --check` passed.

The cached official-source fixture preserves exact retrieved pages and the HTTP
403 failure. All agent judgments, research interpretations and estimates in the
software fixtures are synthetic and visibly labeled. They are not evidence of
live model research quality or a competitive scientific contribution.

Reproduce:

```bash
python3 -m unittest discover -s tests -v
PLAYWRIGHT_MODULE=/path/to/playwright node tests/verify_review_browser.cjs
PLAYWRIGHT_MODULE=/path/to/playwright node tests/verify_research_browser.cjs
python3 design-demos/src/build_workspace_demo.py
```

## Remaining limitations and recommended next steps

1. Structural contracts cannot prove novelty, technical correctness, significance
   or prediction plausibility. The next quality evaluation should run real research
   directions through a browsing-capable model host, followed by domain-expert audit
   of citations, close-work equivalence, complete-paper coherence and review severity.
2. Packets, fresh processes and session IDs enforce dispatch/provenance rules but
   do not provide an OS sandbox or prove independent cognition. The chosen host
   must enforce read scopes and real independent sessions. No provider adapter is
   bundled; the native-host route is ready and the command protocol is tested.
3. OpenReview's authenticated ICML schema was inaccessible. The test rubric is
   reconstructed from official form instructions. Official optional flags and
   unnumbered nested ethics subfields remain explicit uncertainties, with internally
   required headings. Never describe this as an authenticated form schema.
4. HTML/OpenReview parsers cover the tested structures, not every conference portal
   or PDF. Unsupported layouts need a tested parser extension and official evidence;
   missing exact score options must remain blocked. Historical/current-source
   judgment still needs the host researcher to discover the appropriate sources.
5. Actual experiments, empirical-paper audits, real conference submissions and
   real decisions are outside this proposal engine. Existing legacy reports can
   still display sourced actual experiments. Acceptance readiness remains simulated.
6. Persistence assumes one coordinating process on a filesystem supporting atomic
   links/renames. The hash chain detects accidental modification; it is not a signed
   audit log against a party who can rewrite the entire workspace. Very large
   journals replay linearly per operation; database indexing can follow real usage.
7. New projects use schema 2. Existing schema-1 reports remain supported with their
   provenance and annotations; automated conversion of unstructured historical
   scientific judgments is intentionally not claimed.
