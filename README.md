# idea-shaokao

<p align="center">
  <img src="assets/logo.png" alt="Idea Shaokao logo: a lightbulb with a brain, flame, and barbecue grill" width="360">
</p>

**Put research ideas through the heat before spending months on them.**

An installable Agent Skill for persistent research discovery and conference-style
review: literature, competing ideas, technical design, experimental plans,
independent reviewers, author rebuttals, AC synthesis, and SAC assessment.

All instructions and generated research deliverables default to English. The
result is a concrete **Proceed / Revise / Restart / Kill** decision with evidence
and an implementation roadmap. A convincing proposal is never presented as an
experimentally validated paper.

## Install

Use the [Skills CLI](https://github.com/vercel-labs/skills) from your project:

```bash
npx skills add SeanXunX/idea-shaokao --skill idea-shaokao
```

Select your agents interactively, or specify them:

```bash
npx skills add SeanXunX/idea-shaokao --skill idea-shaokao \
  -a codex -a claude-code -a opencode -a cursor
```

Add `-g` for a user-wide installation, `--copy` to copy rather than symlink, or
`-y` to skip installer prompts. Preview discovery with:

```bash
npx skills add SeanXunX/idea-shaokao --list
```

The current Skills CLI requires Node.js 22.20 or later. The skill itself does not
require Node.js, a provider API key, a specific model, or an MCP server. See the
upstream [installation reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)
and [agent directory reference](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)
for current host support and destinations.

For manual installation, clone this repository and copy `SKILL.md`, `references/`,
`scripts/`, `assets/`, and optionally `agents/` into a directory named `idea-shaokao` inside
your agent's skill directory. For example, a Claude Code project can use
`.claude/skills/idea-shaokao/`. No build step is required. Do not copy the `.git/`
directory or store research output inside the installed skill.

## Use

Invoke by the skill's name or your host's skill selector. In hosts that support
`$skill-name` syntax:

```text
Use $idea-shaokao to develop a research proposal on efficient retrieval under
distribution shift. Target ICML. Assume one 24 GB GPU and a two-week prototype
budget. Review at proposal stage, with up to three rounds. Save the work under
research/efficient-retrieval. Deliver the final report in English.
```

For an existing idea:

```text
Use idea-shaokao to stress-test the proposal in proposal.md. Do one independent
review round with three reviewers, author rebuttal, AC discussion, and SAC
assessment. Focus on whether the claimed novelty survives the closest prior work.
```

To continue a project:

```text
Use idea-shaokao to resume research/efficient-retrieval from its checkpoint.
Preserve completed reviews and continue the first unfinished phase within the
existing budget.
```

The agent infers the workflow from the task. It asks for a topic if none is
available; a target venue is optional. An ordinary brainstorming request does not
need the full process.

## What happens

1. **Discovery:** verify sources, map related work, compare distinct ideas when
   ideation is requested, and explain the selection.
2. **Design:** specify the method, assumptions, implementation path, resource
   estimates, and falsifiable experiments with strong and simple baselines.
3. **Independent review:** three or four reviewers assess novelty, correctness,
   experimental rigor, and significance from separate contexts.
4. **Discussion and rebuttal:** the AC identifies disagreements, the author
   responds with evidence, and reviewers reassess their positions.
5. **Decision and revision:** the AC synthesizes the record; a separate SAC audits
   its quality and issues a recommendation. Revise within a bounded round budget.
6. **Delivery:** a final report, versioned proposal, experiment plan, full review
   history, issue resolutions, and a first-week implementation roadmap.

The default limit is four rounds. Convergence requires two consecutive complete
independent rounds with no new critical issues and no unresolved critical blocker.
A single round can still yield a useful preliminary decision. A decisive failure
can end the process immediately; extra rounds must not manufacture favorable scores.

## Compatibility and evidence limits

This repository uses the open [Agent Skills format](https://agentskills.io/specification)
with progressive disclosure. `SKILL.md` is the portable entrypoint; the optional
`agents/openai.yaml` adds Codex UI metadata. The instructions use capability-based
dispatch instead of hard-coded orchestration APIs.

| Available capability | Behavior |
| --- | --- |
| Isolated subagents | Full independent reviewer, AC, and SAC workflow |
| Few concurrent slots | Batch isolated reviewers, then run chairs separately |
| External reviewer sessions | Export packets and preserve returned reviews; missing roles stay pending |
| One agent only | Clearly labeled self-critique; no invented independent reviews or SAC verdict |
| No browsing | Assess supplied sources and disclose unresolved novelty/search coverage |
| No code execution | Deliver experiment plans, without claiming measured results |
| No filesystem | Return inline artifacts and a continuation checkpoint |

Installation compatibility does not guarantee that a host provides independent
subagents or browsing. A shared model family is also not a guarantee of diverse
judgment. The workflow is conference-inspired, uses an explicitly unofficial
rubric by default, and makes no promise of real conference acceptance.

## Persistent workspaces

The agent can create files directly, or use the optional Python 3.10+ helper:

```bash
python3 scripts/init_research.py --root research --slug retrieval-audit \
  --topic "Retrieval under distribution shift" --stage proposal --max-rounds 4

python3 scripts/init_research.py --root research --slug retrieval-audit --resume
```

This creates `research/retrieval-audit/` with a state file, index, issue tracker,
and directories for research artifacts. Resume validates and prints the checkpoint
without changing files; it does not run the research workflow. The helper refuses
collisions and unsafe identifiers. See [the workspace contract](references/workspace.md).

## Repository map and validation

Three offline [review-interface prototypes](design-demos/README.md) explore how to
inspect a completed research run, trace evidence, and export human feedback:
[Signal Desk](design-demos/signal-desk.html),
[Editorial Dossier](design-demos/editorial-dossier.html), and
[Evidence Table](design-demos/evidence-table.html).
They share the actual projection-review test case. Automatic report generation
will follow visual selection.

- [SKILL.md](SKILL.md): discovery metadata, workflow, capability fallbacks, and decision gates.
- [Research contracts](references/research.md): sources, candidates, design, experiments.
- [Agent roles](references/roles.md) and [review protocol](references/review-protocol.md): dispatch, independence, discussion, scoring, closure.
- [Deliverables](references/deliverables.md): final report and implementation roadmap.
- [Workspace helper](scripts/init_research.py): optional standard-library-only initialization.
- [Behavioral evaluation scenarios](tests/evals.md): realistic skill execution checks.

Run the helper's automated tests:

```bash
python3 -m unittest discover -s tests -v
```

Check local package discovery without installing:

```bash
npx skills add . --list
```

Tests verify workspace behavior, not research quality. Behavioral evaluation must
inspect actual agent artifacts and decisions; a frontmatter check alone cannot
establish that reviews were independent or that a research claim is true.
