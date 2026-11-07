# Research workflow validation

Run `python3 -m unittest discover -s tests -v`, then both browser integration
scripts with an installed development Playwright module. Cached official sources
are in `fixtures/`; all research/agent data is explicitly synthetic.

| Requirement | Executable verification |
| --- | --- |
| Exact conference/year/track and current/historical distinction | ConferenceTests; venue-change engine regression |
| Official retrieval and failures | Live `fetch-sources` validation; cached source/HTTP 403 fixture; all-failed acquisition test |
| Exact options, labels, confidence and required questions | Source re-extraction, option tampering and arbitrary categorical/noncontiguous tests |
| Insight chain and contribution types | Structured idea validator and full workflow fixture |
| Structured seven-category literature and closest-work evidence | Literature validator; unavailable concurrent/closest evidence blocks prior-art PASS |
| Three independent novelty adversaries, response and retries | Conditional/fail gate tests, cap abandonment, carried-major concern regression |
| Complete paper and hypothetical estimates | Missing-section, outline, fabricated-kind, invalid range/experiment-reference tests |
| Three/four blind reviewers and exact justified scores | Packet-stability, missing-role, invalid score and provenance tests |
| Individual bounded rebuttal and discussion | Missing concern/over-limit tests; original-to-updated histories and stable batch packets |
| Independent AC and senior assessment | Contradictory chair option, reviewer disagreement and AC/SAC disagreement regressions |
| Multi-round substantive revision and convergence/failure | Full two-round test, acceptance streak, fatal overlap and budget exhaustion |
| Immutable cross-round history and resume | Replay equality, stale response, duplicate report, concurrent commit, cache recovery and chain tamper tests |
| Unattended orchestration | Fresh-process fixture adapter; injected command failure resumes same task |
| Full UI | New browser suite: paper, final experiment specifications/predictions, searchable related-paper links and comparisons, exact scores, threaded responses, side-by-side revisions, sources, annotations, four viewports, offline behavior |
| Existing workspaces remain usable | Existing 26 Python cases and legacy browser suite retained |

A separate forward-testing agent exercised native packet/submit and interruption
recovery in an isolated temporary workspace. Its reproduced findings became tests
for chair recommendation contradictions, dropped novelty concerns, reviewer-session
reuse, mutable batch context and cross-venue acceptance streaks.

These checks establish software invariants, not scientific merit. A live
research-quality evaluation must use real searches and truly isolated model/host
sessions, inspect citations and proposal coherence, and solicit domain-expert
assessment of novelty, significance, hypotheses and experimental predictions.
No synthetic accepted fixture counts as a competitive research contribution.
