# Official conference rubric acquisition

There is no built-in universal score scale. Each project retrieves official
reviewer/form, AC, SAC, author-response and CFP sources for its exact year/track.
Prefer an official OpenReview invitation schema. Official form instructions may
be used for a clearly labeled reconstruction. Never invent optional flags, nested
ethics choices or form dimensions from prose.

## Acquisition and extraction

1. Write a source manifest with `conference: {name,year,track}`, an explicit list
   of exact `official_domains`, and sources containing `id`, `kind`, `year`,
   `track`, and HTTPS `url`. Discover the URLs from official sites; do not guess
   that venue paths share a convention. See `examples/icml2026-sources.json` for
   a verified retrospective test case, not a default for future projects.
2. After initializing this project, run:

```bash
python3 <skill-dir>/scripts/research.py fetch-sources sources.json --output sources-fetched.json
```

Every request records its retrieval timestamp and success/failure. Successful
responses preserve raw content, normalized text and a hash. Failed requests
preserve their error. Review failures: fetching a bundle does not mean all sources
were available. The exact-domain allowlist rejects unrelated source domains and
external redirects; it does not establish institutional ownership by itself.

3. Extract the official form. OpenReview JSON supports exact enum values and
   optional status. HTML extraction takes exact form section headings and detects
   numerical options only within each field heading; unnumbered lists remain
   prose, never guessed categorical options:

```bash
python3 <skill-dir>/scripts/research.py extract-form sources-fetched.json \
  --source reviewer --start "<form-section heading>" --end "<next track heading>" \
  --output extracted-fields.json
```

Omit `--start`/`--end` for OpenReview invitation JSON. Inspect every extracted field
against the official page. Unsupported document structures need a new tested
parser or an explicit pending state, not a universal fallback.

4. Write the rubric specification: version, status, form basis/extraction,
   overall/confidence field IDs, historical flag/reason, uncertainty,
   previous-year differences, and evidence-linked procedures. The ICML example
   shows the schema. Preserve contribution types/track-specific criteria and their
   source in additional configuration fields when the venue provides them. A `contribution_types` entry has `id`, exact `label`, `criteria`, `source_id`, and
   supporting `quote`. Select the appropriate category with `--contribution-type`
   at initialization or `select-contribution-type <workspace> <id>` before rubric
   installation. The selected category is frozen per round and sent to reviewers;
   a venue with categories cannot install its rubric while the category is unknown.

Each exchange has role, label, official source ID, exact supporting quote and any
character limit. Each chair has a summary, scope (`official_simulation` or
`internal_simulation`), supported authority, decision options and acceptance
options. Official labels must appear in their source. Internal options are
separately declared; a favorable internal category is never presented as an
actual conference decision. If the venue has no SAC, label the extra senior audit
internal. Program-chair final authority must not silently move to the SAC.

5. Build and validate, then install:

```bash
python3 <skill-dir>/scripts/research.py build-rubric sources-fetched.json rubric-spec.json \
  --output rubric.json
python3 <skill-dir>/scripts/research.py install-rubric research/<slug> rubric.json
```

The validator re-extracts the form from the preserved sources and requires exact
field/option equality, including labels and numerical types. It checks target
identity, source hashes, historical status, procedures and decision authority.
Unknown current-year material is explicit. Missing form or score evidence blocks
installation and formal review. `status: verified` describes evidence-linked
reconstruction, not third-party certification of the parser or conference rules.

## Historical and unavailable material

Use only the most recent available official historical version when the current
one cannot be obtained. Record failed current-year URLs, older source year,
reason, uncertainties and whether the procedure might differ. The project target
remains the requested year. Cross-venue substitutions are forbidden.

Guideline HTML often omits official required/optional status. These fields have
`official_required: null`, `requirement_scope: internal_completeness`, and an
explicit reconstruction warning. All headings are required by our completeness
contract, not falsely described as authenticated official form requirements.
Policy attestations in an internal simulation must state that no real reviewer
assignment exists; do not falsely attest to a privately assigned conference policy.

Do not normalize scores or derive numerical acceptance cutoffs. The same number
may mean different things across venues/years. Preserve disagreement and exact
scale meaning, including after target changes.
