# Review Dossier — three interactive directions

Open any HTML file directly in your browser. Each is self-contained: content,
fonts, styles, and scripts are embedded. No server, account, or network is needed.

| Direction | Reading model | Open |
| --- | --- | --- |
| A. Signal Desk | Verdict first, horizontal review sequence, expandable issue inspector | [Prototype](signal-desk.html) · [Screenshot](screenshots/signal-desk-1440.png) |
| B. Editorial Dossier | Reading column, serif hierarchy, margin evidence and annotations | [Prototype](editorial-dossier.html) · [Screenshot](screenshots/editorial-dossier-1440.png) |
| C. Evidence Table | Issue index and aligned concern / rebuttal / reassessment columns | [Prototype](evidence-table.html) · [Screenshot](screenshots/evidence-table-1440.png) |

## Try the review flow

1. Read the core idea, investment decision, evidence stage, and next action.
2. Select an issue. Inspect the concern, author response, final reassessment,
   original reviewer IDs, and closure criterion.
3. Open a source. The reader includes exact bundled text, relative artifact path,
   and SHA-256 digest. Close it to return to your reading position.
4. Annotate an issue, claim, or report section. Choose Question, Needs evidence,
   or Suggested change. Your wording is preserved.
5. Use My notes / Notes to edit or delete comments. Export feedback downloads
   `review_feedback.md`, with project/version/round, target IDs, source paths,
   source hashes, and comments.

Notes are private drafts in the current browser, stored separately for each design.
The HTML file itself is not rewritten. Export feedback to share or keep your notes
when moving the file. If browser storage is unavailable, the interface states
“Session only · export to keep notes”; annotation and export still work.

## Test-case content

The shared content comes from the actual earlier one-round projection review.
Every prototype is labeled Test Case. All three reviewers and both chairs
recommended stopping the submitted formulation. External novelty/runtime remain
unassessed, and the conditional E02/E03 experiments were canceled. E01 is an exact
analytical finding, not an empirical run. No synthetic scores or results were added.

The dataset preserves 18 original source texts and their hashes. Concise summaries
in the interface link to those texts. Human annotations do not change the source
record or the recorded recommendation.

## Build and verification

Rebuild the three portable HTML files with Python 3.10+ and the standard library:

```bash
python3 design-demos/src/build_demos.py
```

The builder verifies source hashes and embeds the font binaries, license notices,
dataset, shared runtime, and each direction's template. Open font licenses and
provenance are included in `assets/fonts/` and embedded in each output file.

Browser checks use Playwright. Install it in your chosen development environment,
then run:

```bash
node design-demos/src/verify_demos.cjs
node design-demos/src/check_readability.cjs
```

Set `PLAYWRIGHT_MODULE` to an installed Playwright module directory if it is outside
normal Node resolution. Set `CHROMIUM_EXECUTABLE` when using an existing Chromium
binary. These are development-only requirements; the delivered HTML has none.

Checks cover 1440×900 and 1024×768 viewports, local drafts, source fidelity, reading
position, annotation editing/deletion, verbatim-safe text, feedback download,
storage-denied fallback, stable evidence, anchors, and offline rendering.
[Interaction results](verification/interaction-results.json) and
[readability results](verification/readability-results.json) record the checks.
The latter checks computed text contrast, 12px minimum secondary text, and document
width; primary narrative text uses at least 14px. All six viewport screenshots
are in `screenshots/`.

## Design selection

These are three exploratory directions, not an approved final interface. After
selection, record the user's chosen direction and plan integration that generates
`final/review.html` alongside future research reports. The current skill execution
contract remains the research workflow documented in the repository's SKILL.md.
