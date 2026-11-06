# Verification record

Validated in headless Chromium using Playwright 1.59.1, with the browser network
disabled and each prototype opened via file://.

All three directions passed at 1440×900 and 1024×768. The interaction record
includes the SHA-256 digest of the exact HTML tested. The readability record
reports computed text contrast, minimum 12px secondary text, and horizontal
overflow checks. Primary narrative text uses at least 14px.

The common flow covers four issue groups, immutable source text and source
switching, reader position, annotations on claims/issues/sections, editing,
deletion, safe verbatim comments, local persistence, unfinished draft recovery,
Markdown downloads, and storage-denied session-only fallback. No page errors or
HTTP(S) requests were recorded.

Screenshots include both requested viewport sizes and the source/annotation
dialogs. Screenshots were inspected visually for layout and reading hierarchy.
These checks validate the prototypes, not the scientific quality of future runs
or identical behavior in every browser.
