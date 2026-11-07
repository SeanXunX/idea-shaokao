# Official-source software fixture

`icml2026-official-sources.json.gz` is the gzip-compressed output of the new
`fetch-sources` command, retrieved from the official ICML pages on 2026-11-07.
It preserves exact raw HTML, normalized text, retrieval dates, content hashes,
and the OpenReview invitation's HTTP 403 failure. Gzip keeps the original source
snapshots compact; Python's standard library reads them without dependencies.

The rubric is extracted afresh in each test using the example specification.
The official instructions are a reconstruction source, not an authenticated
OpenReview schema. Required/optional flags and unnumbered ethics subfields are
explicitly uncertain. The sample adds a labeled internal SAC readiness audit.

All research claims, search results, agent reports, predictions and decisions
in `engine_fixture.py` are **synthetic software inputs**. Passing these tests does
not establish that a model can discover novel research or produce quality reviews.
