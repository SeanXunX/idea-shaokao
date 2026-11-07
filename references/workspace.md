# Persistent engine and host execution

## New projects

Python 3.10+ and the standard library are sufficient. No provider API or build
system is required. Create a distinct project outside the installed skill:

```bash
python3 <skill-dir>/scripts/research.py init research/<slug> \
  --topic "<direction>" --conference "<venue>" --year <year> --track "<track>" \
  --max-rounds 4 --max-stress-iterations 3 --reviewers 4 --acceptance-rounds 2
```

The conference/year/track are mandatory for the full venue-calibrated workflow.
`--constraints` records actual resource assumptions. Limits are configurable
positive integers up to 100; four rounds and three novelty attempts are defaults,
not universal scientific thresholds. `--mode` can be `independent`,
`external_review`, or `single_agent`. The latter cannot satisfy independent gates.

Initialize first, then fetch sources for that project using
[conference.md](conference.md). Installation refuses older project-independent
cached rubrics, except explicitly synthetic test workspaces.

## Authoritative data

```text
research/<slug>/
  events/000001.json ...           Immutable, hash-linked transition records
  project.json                    Rebuildable schema-2 checkpoint/cache
  final/
    final_report.md               Honest outcome and continuation
    paper.md                      Selected complete paper, when available
    review.html                   Offline Overview / Final Paper / Review Process
    review-manifest.json          Persistent annotation identity and source hashes
```

Each record has sequence, previous hash, timestamp, event type, payload and hash.
A complete fsynced temporary file is atomically linked into an exclusive event
name. Partial writes never become transitions. Competing coordinators cannot
commit the same sequence; reload and retry the still-pending task. One coordinator
should own dispatch. A hash chain detects accidental tampering; it is not a
cryptographic signature against someone who controls all files.

The schema-2 project contains conference configuration, budgets, rounds and role
session provenance. Each round freezes its rubric, predecessor, literature,
research revisions, idea/paper versions, novelty attempts, submission, initial
reviews, rebuttal, discussions, author follow-ups, final reviews, AC and SAC.
Hypotheses, literature papers, experiments, predictions, concerns and responses
have stable IDs. Every role output references its task, round, exact context hash,
paper version, session and timestamp. Actual experiments are never synthesized
from predictions; this engine's evidence stage is a paper-level **proposal**.

`project.json` is a cache. Never manually edit it to advance a stage or close a
concern. `verify` replays and checks the journal and rebuilds it. Rendered files
are derived views of that same journal, not independent research truth.

## Native-host dispatch (preferred in an agent skill)

```bash
python3 <skill-dir>/scripts/research.py status research/<slug>
python3 <skill-dir>/scripts/research.py packet research/<slug> \
  --task <pending-task-id> --output /tmp/task-packet.json
```

The packet contains a role-specific brief, frozen approved context, output
contract and response envelope. Use the host's real isolated-context facility to
execute it. A child does not inherit the author conversation, private notes,
workspace path, peer reviews or prior-round scores for initial assessment. Give it
only the packet and the tools needed to retrieve evidence; restrict its filesystem
scope. Return its actual structured response as JSON, then:

```bash
python3 <skill-dir>/scripts/research.py submit research/<slug> /tmp/response.json
```

Use a distinct session for each novelty adversary, initial reviewer and chair.
Reviewers may reuse their own session for discussion, or a fresh replacement with
only approved materials. A reviewer cannot reuse an author's or peer's session.
The session identifiers are host attestations, not proof of cognitive diversity.
Do not falsely mark `independent: true` when the host cannot isolate contexts.
Missing or rejected reports stay pending; do not fabricate a positive response.

The host may queue independent tasks in batches. Initial-review and initial
reassessment packet hashes stay stable while peer outputs arrive. Task/version
hashes reject stale responses; submitted outputs cannot be replaced. Newly
required stages appear only after their prerequisites are complete.

## Unattended command adapter

```bash
python3 <skill-dir>/scripts/research.py run research/<slug> \
  --agent-command '["/absolute/path/to/your-agent-adapter"]' \
  --max-steps 100 --timeout 600
```

The command must be a JSON argv array. Each task launches a fresh process, takes
one packet on stdin and returns exactly one JSON response on stdout. The adapter
owns model/tool integration, true context isolation, source retrieval and session
identity. No provider command, key, paid call, browser, or model is assumed or
silently installed. Use absolute paths: the working directory is the workspace.

The driver runs authorized stages until termination, the step budget, or an error.
Timeout, process failure, malformed JSON and rejected scientific artifacts are
journaled. Rerun `run` or use native packet dispatch to continue the same pending
task. A fresh process is not an OS sandbox: use a provider/host with proper scopes.
The bundled `tests/fixture_agent.py` is explicitly synthetic and only tests software.

## Resume and target changes

```bash
python3 <skill-dir>/scripts/research.py verify research/<slug>
python3 <skill-dir>/scripts/research.py status research/<slug>
```

The journal is authoritative even if `project.json` is missing or malformed.
A broken sequence/hash blocks recovery instead of silently deleting history.
Inspect corruption against backups. Old temporary `.pending-*` files are not
committed events. Completed roles and budgets remain intact after interruption.

A target change is allowed at a round boundary, including the next pending
revision. `change-target --conference ... --year ... --track ...` invalidates the
active rubric. Fetch new official sources and install a matching rubric. Previous
rounds retain their original venue and scale. Acceptance streaks cannot cross
rubric or core-insight/hypothesis/mechanism changes.

## Legacy compatibility and capability limits

`init_research.py` and schema-1 `state.json`/`final/review-data.json` remain supported
for existing workspaces. Their source fidelity, annotations, missing-data behavior
and renderer tests are retained. They do not enforce the new scientific gates;
never claim a legacy report completed them without actual recorded evidence.
Do not automatically convert legacy prose into fictional structured judgments.

Without Python, follow the same contracts using native file tools and explicit
checkpoints. Without browsing, preserve supplied sources and missing coverage;
independent prior-art PASS is unavailable without adequate verified investigation.
Without independent contexts, deliver honest self-critique and pending packets.
