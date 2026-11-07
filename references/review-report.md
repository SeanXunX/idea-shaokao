# Generate the final review interface

Run this finalization step for every persisted research run, including a Kill,
budget stop, or incomplete scoped review. The approved interface is a compact
GitHub Issues-style report. Use the bundled assets; do not redesign it each run.

## Finalization sequence

1. Save the real final report, reviewed proposal versions, issue dispositions,
   reviews/discussion/rebuttals, experiment records, and checkpoint first.
2. Write `final/review-data.json` using the schema below. This is a sourced display
   index, not a replacement for the original documents. Summarize only what the
   sources establish. Preserve stable IDs across revisions and include all review
   rounds, missing responses, and unresolved disagreements honestly. Keep list
   titles and overview summaries concise; leave full reasoning in the source
   documents and discussion entries.
3. Run the installed skill's helper, from any working directory:

   ```bash
   python3 <skill-dir>/scripts/render_review.py <research-workspace>
   ```

   It validates the index and local references, reads the current source files,
   computes their hashes, and writes `final/review.html` plus
   `final/review-manifest.json`. It requires Python 3.10+ and no third-party package.
   `--check` performs validation/compilation without writing.
4. Open or inspect the generated report when browser tools are available. Check
   the actual title, recommendation/assessor, mode, round history, issue states,
   and source text. Confirm no demo claims or scores have appeared. Link both
   `final/review.html` and `final/final_report.md` in the workspace index and final
   handoff. A render failure leaves the run's delivery incomplete; fix the input
   or report the exact capability limitation rather than claiming HTML was made.

The helper never executes research, changes source evidence, upgrades the review
stage, or decides whether research has converged. A favorable proposal assessment
is still a proposal assessment. Missing arrays produce explicit empty states,
not invented reviewers, responses, experiments, or numerical scores.

## Display index, schema version 1

All paths are relative to the research workspace and use `/`. Source IDs are
stable keys referenced by items. The helper automatically includes these IDs:
`state` → `state.json`, `report` → `final/final_report.md`, and, when present,
`issues` → `issue_tracker.md`. Do not remap them. Add every other source needed for
the actual study; text documents, source code, and bounded run logs are supported.
Binary artifacts should be represented by their authoritative text evidence record.
Sources must be UTF-8 text, at most 2 MiB each and 20 MiB in total. Missing,
external, or escaping paths fail validation instead of silently dropping evidence.

A minimal index for an unfinished run can contain only:

```json
{
  "schema_version": 1,
  "overview": {
    "description": "A concise account of the actual research question and method.",
    "recommendation": "Undetermined",
    "assessor": "Author",
    "rationale": "The scoped review is unfinished; no independent verdict exists.",
    "sources": ["report"]
  }
}
```

Replace this illustrative wording with the run's actual, supported account. Use
optional `overview.title` for a shorter title and `overview.next_action` when the
checkpoint's next action needs a sourced display summary. The workspace's slug,
proposal version, stage, execution mode, current/max round, status, and convergence
come from `state.json`, not from the display index. If a recorded recommendation
exists in state, it must agree with the index.

`recommendation`: `Proceed`, `Revise`, `Restart`, `Kill`, or `Undetermined`.
`assessor`: `Author`, `AC`, `SAC`, or `Unassigned`. Chair labels require independent
or external-review mode and an actual returned assessment. Use `Author` for
self-critique. Optional `test_case: true` labels an explicit evaluation fixture;
omit it for real research. No sample project content is bundled into the renderer.

Add these top-level collections as the corresponding work exists:

| Collection | Fields |
| --- | --- |
| `sources` | Object mapping source ID to its exact relative artifact path |
| `issues` | `id`, `title`, `severity`, `status`, optional `round` (0 before review), `aliases`, `criterion`, `sources`, `discussion` |
| `claims` | `id`, `title`, `text`, `status` (honest evidence label), `sources` |
| `reviewers` | `id`, `round`, optional `focus`, `stage`, `rubric`, `confidence`, `initial`, `final` |
| `timeline` | `id`, `round`, `label`, `role`, `summary`, `source` |
| `experiments` | `id`, `title`, `kind`, `status`, `summary`, `source` |

Every source reference must resolve. `sources` arrays are nonempty lists of source
IDs; singular `source` is one ID. Scores and recommendations are copied from the
record, never inferred by the renderer. Put the actual assessment document first
in `overview.sources`; it is the overview’s Read assessment source link.

For each issue:

- Retain the original stable `id`; `aliases` defaults to `[id]`. When grouping
  duplicates, include every original ID exactly once and preserve their evidence.
- Severity is `Critical`, `Major`, `Moderate`, or `Minor`. Status is `Open`,
  `Partially resolved`, `Pending experiment`, `Resolved`, or `Rejected with
  justification`. The last two appear in the resolved filter; all others remain
  open. This grouping does not change the displayed scientific disposition.
- `round` identifies the round associated with the current issue record. Each
  discussion entry has its own actual round; carried concerns retain their IDs.
- `discussion` is an ordered list of objects containing `author`, `phase`, `text`,
  `source`, and optional `round`. Include real reviewer concern, author rebuttal,
  reassessment, and chair exchanges as appropriate. Leave missing responses out.
  The source reader retains their exact original documents behind the summaries.
- Supply a truthful `criterion` and source IDs supporting the issue. If `sources`
  is omitted, the helper uses discussion sources and the original issue tracker.

Example structure for one sourced entry (IDs and paths are illustrative):

```json
{
  "sources": {
    "r2-initial-01": "reviews/round-01/reviewer-R2-initial.md",
    "rebuttal-01": "rebuttals/round-01.md"
  },
  "issues": [{
    "id": "R01-R2-01",
    "title": "The concern actually raised in the review",
    "severity": "Major",
    "status": "Pending experiment",
    "round": 1,
    "criterion": "The actual reviewer or chair's resolution criterion.",
    "discussion": [
      {"author": "R2", "phase": "Initial review", "round": 1,
       "text": "A faithful summary of the original concern.", "source": "r2-initial-01"},
      {"author": "Author", "phase": "Rebuttal", "round": 1,
       "text": "The actual author response, without claiming the experiment ran.",
       "source": "rebuttal-01"}
    ]
  }]
}
```

For reviewer rows, `initial` and `final` are either `null`/omitted for missing
records, or `{"score": "7/10", "source": "actual-source-id"}`. Include the actual
scale in the score string (or use the exact recorded number). Do not assume a
10-point scale. Repeated reviewer IDs across different rounds are supported.
Record each row's actual stage and rubric; missing metadata displays “Not recorded.”

For experiments, distinguish planned, running, failed, completed, and canceled
work in `status` and `kind`. Cite actual run artifacts for measured outcomes; an
expected result is not an observation. Claim/experiment IDs must remain stable.

## Annotations, regeneration, and continuation

`review-manifest.json` holds a persistent workspace UUID and source hashes. Keep
it when regenerating, resuming, or moving the research directory. The UUID stays
stable across proposal versions and rounds, so saved notes use the same browser
storage key. The renderer can recover it from an existing generated HTML if the
manifest alone was lost. A malformed or mismatched identity fails explicitly.

Notes store their original target, proposal version, round, stage, and source hash
snapshots. After regeneration, changed-source and removed-target annotations stay
visible in My notes with their original context. They are never silently deleted
or retargeted to an unrelated claim. Multiple unfinished drafts are preserved.

Annotations live in browser storage, not inside the HTML file or Python process.
File URLs and browsers may scope storage differently. Use **Back up notes** and
**Restore notes** in My notes to move saved notes and unfinished drafts between
browsers or file locations. Restore requires the same workspace UUID; conflicts
are retained separately. If storage is denied, in-session annotation, Markdown
export, and JSON backup still work with a visible session-only indicator.

**Export feedback** produces `review_feedback.md`, including target IDs, original
version/round/stage, source paths/hashes, and verbatim comments. Treat it as human
feedback on the referenced snapshot. Reconcile it with current evidence and issue
history on continuation; it does not itself change a reviewer or SAC verdict.

## Hosts without Python or execution

With file-editing capability, the agent may assemble the same standalone report
using `assets/review/template.html`, `styles.css`, `runtime.js`, and `app.js`:
inline CSS and scripts at their markers and put the normalized data in the
`review-data` JSON script. Follow the index mapping implemented in the renderer,
read actual sources, compute real hashes using available native tools, preserve
the workspace UUID, and escape `<` in JSON as `\u003c`. Do not fetch libraries or
copy example data. Prefer the validated Python helper whenever available.

If writing or executing cannot produce/verify the artifact, deliver the real
Markdown and checkpoint, state that HTML generation remains pending, and retain
that exact next action. Never claim a saved or verified report that does not exist.
