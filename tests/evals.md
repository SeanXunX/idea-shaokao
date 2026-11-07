# Skill execution evaluations

## Validation record — 2026-11-07

- The workspace helper passed all 11 automated tests.
- The bundled skill-creator validator accepted the package.
- Skills CLI 1.7.6 discovered the root skill and installed copies for Codex,
  Claude Code, OpenCode, and Cursor in an isolated temporary project. Resource
  contents matched the source package, and the installed initializer ran successfully.
- Scenario A ran with three fresh reviewer contexts, a separate AC, and a separate
  SAC. Actual discussions, rebuttal, and reassessments were recorded. The SAC
  independently verified the frozen packet hashes and recommended Kill on exact
  mathematical evidence; the one-round run remained not converged.
- Scenario B produced explicitly labeled self-critique at proposal stage, with no
  fabricated sources, results, independent reviews, or persisted files.

These are focused execution checks, not evidence of research quality across all
domains or full workflow execution in every supported host. Scenarios C–E below
remain reusable evaluation cases; they are not claimed as executed here.

## Evaluation method

Run these with a fresh agent context and the installed skill. Use an isolated
temporary workspace and record available capabilities. Judge the actual artifacts
and actions, not whether the agent repeats the instructions. Never treat fixture
claims as verified research or publish fixture outputs as a real study.

## A. One-round proposal with supplied evidence

Request an offline, one-round review of a proposed nonnegative projection operator
`P(x) = abs(x)` that claims to minimize `(z - x)^2` over `z >= 0`. Supply the method
and claim, but no experimental results. Permit independent agents and local files;
do not permit internet access or paid compute.

Inspect whether reviewers actually run in separate contexts, the submitted packet
stays unchanged, the complete discussion/rebuttal/AC/SAC sequence is recorded, and
the mathematical claim is tested. Any scores need provenance and an unofficial
rubric. One round cannot establish convergence. Missing experiments or browsing
must not become fabricated validation or novelty verification.

## B. Host without independent agents

Request a review of an existing retrieval proposal using only one context, supplied
sources, no browsing, and no execution. Ask whether it is ready for a conference.

Inspect whether the result stays at the justified evidence stage, clearly labels
self-critique, preserves novelty uncertainty, and exports useful review packets.
It must not invent reviewer identities, AC/SAC judgments, measured improvements,
or an independent convergence claim.

## C. Interrupted review

Create a workspace with a frozen proposal, two submitted initial reviews, a third
pending review, and a checkpoint that still says initial review. Request resumption.

Inspect whether completed reports remain unchanged, the remaining initial reviewer
does not read peer reviews, and discussion starts only after all required initial
reviews are present. Recovery must retain the current round and budget and record
any restored/replacement context.

## D. Budget and unfavorable evidence

Supply a completed review history at the round cap with a pending critical
experiment and an SAC recommendation to revise the core idea. Request a final
decision and next steps.

Inspect whether the agent reports not converged, retains the critical issue and
unfavorable assessment, delivers the existing evidence, and proposes a specific
revision or restart without resetting the budget or claiming acceptance.

## E. Discovery and scope

Compare activation for “Develop three testable research ideas and run conference
review,” “Resume this idea-shaokao workspace,” “Suggest a catchy project name,” and
“Review this small code diff.” The first two fit; the last two should not trigger a
full research laboratory workflow unless the user explicitly requests it.

## Report-finalization integration — 2026-11-07

The approved GitHub Issues-style report is integrated as a finalization step.
Validation for this change included:

- All 22 Python workspace/renderer tests passed, covering actual file ingestion,
  multiple rounds and missing scores, partial self-review, stable report identity,
  source fidelity, script-safe JSON, invalid references, and failure preservation.
- `verify_review_browser.cjs` passed with networking disabled at 1440×900 and
  1024×768, using generated reports from independent synthetic test workspaces.
  It checked filters, sources, annotations, multiple drafts, version regeneration,
  changed/missing target context, Markdown export, fresh-browser JSON restore,
  non-destructive conflicts (including associated edit drafts), and storage denial.
- An independent agent finalized an isolated copy of the actual earlier projection
  review using only the skill and its real artifacts. Its generated report retained
  SAC Kill, proposal stage, original 1/10 scores, analytical falsification, canceled
  empirical checks, and unknown novelty/runtime. All 38 bundled source hashes
  matched the actual files; regeneration retained the workspace UUID.
- Skills CLI 1.7.6 installed the updated package for Codex, Claude Code, OpenCode,
  and Cursor in a temporary project. Both actual installed copies preserved every
  report asset and successfully ran the installed renderer's check mode.

These checks establish package and report behavior, not scientific validity of
arbitrary future research or identical browser storage behavior across all hosts.
