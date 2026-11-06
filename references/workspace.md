# Persistent workspace and recovery

Keep each idea in a separate user workspace, never inside the installed skill.
The default parent is `research/`; honor an existing user-selected location.

## Initialize or inspect

The optional helper needs Python 3.10+ and no third-party dependencies:

```bash
python3 <skill-dir>/scripts/init_research.py \
  --root research --slug efficient-retrieval \
  --topic "Efficient retrieval under distribution shift" \
  --venue "Unspecified" --stage proposal --max-rounds 4

python3 <skill-dir>/scripts/init_research.py \
  --root research --slug efficient-retrieval --resume
```

Replace `<skill-dir>` with the actual installed skill directory. Run from the
user's project so the default workspace is created there. `--root` is the parent;
the helper creates `<root>/<slug>`, not an additional nested `research/` directory.
It refuses to overwrite an existing directory. `--resume` validates the checkpoint
and required layout and prints state without writing. Supplied topic, venue,
stage, or round options on resume must match the saved state. The helper does not
launch agents, verify research conclusions, or perform the recorded next action.

Without Python, use file tools to create the layout and state below. Without file
tools, return an inline checkpoint with artifact sections instead of claiming
persistence. Do not install software solely to initialize a directory.

## Layout

```text
research/<slug>/
  README.md                       Artifact index and project status
  state.json                      Checkpoint, configuration, next action
  issue_tracker.md                Stable issue IDs and evidence-based dispositions
  literature/
    search_log.md
    papers.md
    research_landscape.md
    related_work_matrix.md
  ideation/
    candidate_ideas.md
    idea_selection.md
  proposal/
    v01/                          proposal.md, experiments.md, evidence.md
    v02/                          Next submission, including changes.md
    final/                        Selected version and its provenance
  reviews/
    score-history.md
    round-01/                     Manifest, reviews, discussion, AC and SAC
  rebuttals/
    round-01.md
  experiments/
    <run-id>/                     Configuration, commands, raw logs, measurements
  final/
    final_report.md
```

Only the top-level directories, README, state, and empty issue tracker are created
by the helper. Write phase artifacts when work actually happens. The review
filenames and contracts are in [review-protocol.md](review-protocol.md).

## State contract

`schema_version` is `1`. The helper creates these fields:

| Field | Meaning |
| --- | --- |
| `slug`, `topic`, `venue` | Stable workspace ID and research scope; venue may be `Unspecified` |
| `review_stage` | `proposal`, `implementation`, or `paper` |
| `execution_mode` | Initially `unselected`; then `independent`, `external_review`, or `single_agent` |
| `current_round` | Latest round started, or `0` before review; never exceeds `max_rounds` |
| `max_rounds` | Integer from 1 to 4; default 4 |
| `status` | Initially `in_progress`; use `completed`, `budget_stopped`, `blocked`, or `killed` when applicable |
| `next_action` | Initially `literature`; replace with a concrete next step and artifact/issue references |
| `created_at`, `updated_at` | ISO 8601 UTC timestamps; retain creation time |

Extend state as work proceeds with `last_completed_round`, `proposal_version`,
`convergence` (`not_assessed`, `not_converged`, `converged`), `recommendation`,
`constraints`, and `pending_tasks` when useful. Keep unknown extension fields on
resume. A completed bounded review can still be `not_converged`; completion and
scientific readiness are different facts. `blocked` means a concrete required
input/tool is missing, not that the research conclusion is unfavorable.

Record the topic scope, evidence inventory, compute/time budget, authorization
limits, source cutoff, and capability limitations in the README or a linked intake
note. Record agent/session identifiers and review provenance in each round's
manifest. These identifiers document provenance; they do not grant independence.

## Checkpoint and recovery

One coordinator owns shared state and the aggregate issue tracker. Give each
reviewer a separate report destination to prevent concurrent overwrites. Save
completed artifacts first, then checkpoint state (prefer a temporary file plus an
atomic rename), then update the index. Preserve original reviews and measurements.

On resume, reconcile state against actual artifacts and the latest manifest:

1. Verify the active proposal version, stage, round, completed role outputs, and
   open issues. A file that merely exists is not proof of a completed review.
2. If state is ahead of disk, mark the operation incomplete and rerun only the
   missing work. If disk is ahead of state, inspect the artifact before advancing
   the checkpoint. Record the correction; do not silently rewrite history.
3. Reattach an available reviewer context or dispatch a documented replacement
   using only that role's approved materials. An unsubmitted initial reviewer
   must still be blind to peer reports, even if they already exist on disk.
4. Revalidate stale literature for novelty-sensitive work and check code/data
   identifiers before reusing results. Preserve evidence dates and prior verdicts.
5. Continue the exact pending phase within the existing round/resource budget.
   Record changed constraints explicitly; do not reset rounds during recovery.

If the helper rejects malformed state, inspect the file and actual artifacts.
Back up the existing checkpoint before a deliberate repair, then validate it.
Never reinitialize over an existing project to conceal missing history.
