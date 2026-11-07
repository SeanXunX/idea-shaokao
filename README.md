# Idea Shaokao

<p align="center"><img src="assets/logo.png" alt="Idea Shaokao" width="300"></p>

Develop a research direction into a complete, literature-grounded paper proposal,
challenge it with independent novelty adversaries, and iteratively review it under
the target conference's actual criteria. The objective is work that merits a
strong assessment, with honest abandonment when it does not.

This repository is a portable Agent Skill with a standard-library Python workflow
engine and offline review UI. It does not assume a model provider, API key, web
server, or frontend build. Scientific outputs default to English.

## Install and invoke

```bash
npx skills add SeanXunX/idea-shaokao --skill idea-shaokao
```

Or copy `SKILL.md`, `references/`, `scripts/`, `assets/`, `examples/`, and optionally
`agents/` into your host's skill directory under `idea-shaokao`. Store research
projects outside the installed skill.

```text
Use $idea-shaokao to develop research on retrieval under distribution shift.
Target ICML 2026 Main Track. Assume one 24 GB GPU and a two-week prototype budget.
Develop a complete proposal, verify novelty adversarially, and conduct up to four
independent research/review rounds. Save to research/retrieval-shift.
```

The target conference, year and track are required for venue-calibrated review.
A narrower exploration can proceed without them, with no acceptance-readiness
claim. Honor a supplied idea and the user's actual resource constraints.

## Scientific workflow

1. **Official venue configuration.** Retrieve current reviewer/form, author,
   AC/SAC and CFP sources. Preserve exact scales, labels, definitions, questions,
   response rules, source hashes, retrieval failures and historical uncertainty.
   There is no universal scoring rubric or numerical acceptance threshold.
2. **Evidence and insight.** Investigate foundational, recent, journal, preprint,
   concurrent, closest and adjacent work. Compose a non-obvious insight through
   problem → limitation → observation → hypothesis → mechanism → contribution →
   falsification. Prefer significant research over convenient experiments.
3. **Complete paper.** Write all fourteen parts, including technical design,
   appropriate theory, rigorous experiments and explicitly hypothetical numerical
   predictions with assumptions, uncertainty and failure conditions.
4. **Mandatory novelty gate.** Three fresh adversaries investigate prior art,
   conceptual originality and venue significance. The author responds by concern
   ID. Conditional/fail requires recomposition and a repeated test; the cap ends
   polishing of an indefensible idea.
5. **Independent peer review.** Three or four blind initial reviewers use the exact
   official form. Author rebuttal, permitted discussion, score reassessment,
   AC synthesis and an independent senior audit preserve disagreement.
6. **Research-level iteration.** Revise mechanisms, hypotheses, theory, experiments
   or prediction calibration around actual concerns. Acceptance requires both
   chairs' evidence-backed support and no unresolved major/critical issue.
   Defaults are four rounds, three novelty attempts, and two consecutive eligible
   rounds on the same rubric/core hypothesis. Budgets never reset silently.

A **simulated Accept** means the proposal appears competitive under the
reconstructed process. It does not guarantee real acceptance or substitute for
completed experiments. Reviewers are not rewarded for favorable scores.

## Persistent engine

Python 3.10+; no third-party runtime dependency:

```bash
python3 scripts/research.py init research/retrieval-shift \
  --topic "Retrieval under distribution shift" \
  --conference ICML --year 2026 --track "Main Track"
```

Initialize first, then fetch official sources for this project. The ICML files
below are a real retrospective validation example; discover and verify the
requested venue/year instead of treating them as defaults:

```bash
python3 scripts/research.py fetch-sources examples/icml2026-sources.json \
  --output /tmp/official-sources.json
python3 scripts/research.py build-rubric /tmp/official-sources.json \
  examples/icml2026-rubric-spec.json --output /tmp/rubric.json
python3 scripts/research.py install-rubric research/retrieval-shift /tmp/rubric.json
```

`build-rubric` re-extracts the fields from preserved official sources. An
unsupported form or missing evidence blocks installation. The ICML example labels
its official-instructions reconstruction, unknown optional flags, restricted
OpenReview endpoint, and additional internal senior audit explicitly. Inspect
retrieval failures and the source-linked specification before installation.

The host agent performs actual research with its tools. Native isolated-context
dispatch uses the pending queue and structured JSON packets:

```bash
python3 scripts/research.py status research/retrieval-shift
python3 scripts/research.py packet research/retrieval-shift --output /tmp/packet.json
# Execute the packet in the appropriate actual host-agent context.
python3 scripts/research.py submit research/retrieval-shift /tmp/returned-response.json
```

An unattended adapter can execute one fresh process per task:

```bash
python3 scripts/research.py run research/retrieval-shift \
  --agent-command '["/absolute/path/to/your-agent-adapter"]'
```

The adapter receives one JSON packet on stdin and returns one validated JSON
response on stdout. It owns model/tool integration and truthful isolation/session
provenance. No provider-specific executable is bundled. The synthetic test adapter
is exclusively a software fixture, never a research-quality model.

An append-only hash-linked journal is authoritative; `project.json` is a
recoverable cache. Every report references its exact round, paper and context.
Missing or failed outputs remain pending. Resume without overwriting history:

```bash
python3 scripts/research.py verify research/retrieval-shift
python3 scripts/research.py status research/retrieval-shift
python3 scripts/research.py render research/retrieval-shift
```

See [workspace and adapter contract](references/workspace.md),
[conference configuration](references/conference.md),
[role boundaries](references/roles.md), and [review protocol](references/review-protocol.md).

## Review interface

The generated `final/review.html` has three primary views:

- **Overview:** final title, venue/year, summary, insight, novelty, contributions,
  method, decisive validation and simulated outcome.
- **Final Paper:** complete academic prose with section navigation, hypothetical
  prediction tables, technical/experiment details and evidence references.
- **Review Process:** each frozen submission, all novelty attempts, independent
  reviews with exact original/updated labels, threaded author responses,
  discussion, AC/SAC reasoning and side-by-side paper versions.

Original journal sources and hashes are inspectable offline. Equations use the bundled KaTeX 0.19.1 renderer and embedded fonts, without CDN requests. Annotations, drafts,
feedback export and JSON note backups retain stable identities across regeneration.
No demo research is inserted into real workspaces. Existing schema-1 workspaces
and their renderer remain supported; they do not acquire new gate guarantees
merely by rendering successfully.

## Validation and limitations

```bash
python3 -m unittest discover -s tests -v
node tests/verify_review_browser.cjs
node tests/verify_research_browser.cjs
```

Browser tests use development-only Playwright. Set `PLAYWRIGHT_MODULE` to an
existing Playwright module when it is not locally installed. Python tests cover
real cached official-source extraction, exact options, full multi-round execution,
scientific failure paths, session/context boundaries, journal recovery and legacy
compatibility. Browser tests cover offline rendering, interactions, notes, sources
and desktop/mobile layouts. The new engine was also checked by an independent
forward-testing agent; findings received regression tests.

**Test research and agent judgments are explicitly synthetic.** Software checks
cannot prove research novelty or that a chosen model will produce rigorous papers.
The framework requires a host with browsing and genuinely isolated review contexts;
a fresh process or a session ID alone does not provide an OS security boundary.
Official rubric layouts beyond supported HTML/OpenReview schemas require a tested
parser extension. The engine assesses proposals, not experimentally completed
papers. See [implementation and validation report](docs/implementation-report.md)
for exact test evidence, remaining limitations and recommended follow-up work.
