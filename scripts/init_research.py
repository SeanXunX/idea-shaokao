#!/usr/bin/env python3
"""Create or inspect an idea-shaokao research workspace without dependencies."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys


SCHEMA_VERSION = 1
STAGES = ("proposal", "implementation", "paper")
DIRECTORIES = (
    "literature", "ideation", "proposal", "reviews", "rebuttals", "experiments", "final"
)
REQUIRED_FILES = ("README.md", "state.json", "issue_tracker.md")
SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class WorkspaceError(ValueError):
    """An invalid configuration or workspace; safe to show to the caller."""


def nonempty(value, field):
    if not isinstance(value, str) or not value.strip():
        raise WorkspaceError(f"{field} must be a nonempty string")
    return value.strip()


def validate_slug(slug):
    if not isinstance(slug, str) or len(slug) > 64 or not SLUG_PATTERN.fullmatch(slug):
        raise WorkspaceError(
            "slug must be 1-64 lowercase letters or digits, separated by single hyphens"
        )
    return slug


def validate_rounds(value):
    if type(value) is not int or not 1 <= value <= 4:
        raise WorkspaceError("max_rounds must be an integer from 1 to 4")
    return value


def validate_state(state, slug):
    if not isinstance(state, dict):
        raise WorkspaceError("state.json must contain a JSON object")
    if type(state.get("schema_version")) is not int or state["schema_version"] != SCHEMA_VERSION:
        raise WorkspaceError("unsupported or missing state.json schema_version (expected 1)")
    if state.get("slug") != slug:
        raise WorkspaceError("state.json slug does not match the workspace directory")
    for field in ("topic", "venue", "execution_mode", "status", "next_action"):
        nonempty(state.get(field), f"state.json {field}")
    if state.get("review_stage") not in STAGES:
        raise WorkspaceError("state.json review_stage must be proposal, implementation, or paper")
    maximum = validate_rounds(state.get("max_rounds"))
    current = state.get("current_round")
    if type(current) is not int or not 0 <= current <= maximum:
        raise WorkspaceError("state.json current_round must be an integer between 0 and max_rounds")
    for field in ("created_at", "updated_at"):
        value = nonempty(state.get(field), f"state.json {field}")
        try:
            stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise WorkspaceError(f"state.json {field} must be an ISO 8601 timestamp") from error
        if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
            raise WorkspaceError(f"state.json {field} must include a UTC timezone")
    return state


def resume_workspace(workspace, slug, expected):
    if workspace.is_symlink() or not workspace.is_dir():
        raise WorkspaceError(f"workspace is missing or is not a regular directory: {workspace}")
    for name in DIRECTORIES:
        entry = workspace / name
        if entry.is_symlink() or not entry.is_dir():
            raise WorkspaceError(f"workspace is missing a regular directory: {name}")
    for name in REQUIRED_FILES:
        entry = workspace / name
        if entry.is_symlink() or not entry.is_file():
            raise WorkspaceError(f"workspace is missing a regular file: {name}")
    try:
        state = json.loads((workspace / "state.json").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as error:
        raise WorkspaceError(f"cannot read state.json: {error}") from error
    validate_state(state, slug)
    for field, supplied in expected.items():
        if supplied is not None and state[field] != supplied:
            raise WorkspaceError(
                f"--resume {field} does not match state.json; resume without that option "
                "or inspect and deliberately update the existing workspace"
            )
    return state


def initialize_workspace(workspace, slug, topic, venue, stage, max_rounds):
    topic = nonempty(topic, "topic")
    venue = nonempty(venue, "venue")
    validate_rounds(max_rounds)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state = {
        "schema_version": SCHEMA_VERSION,
        "slug": slug,
        "topic": topic,
        "venue": venue,
        "review_stage": stage,
        "execution_mode": "unselected",
        "current_round": 0,
        "max_rounds": max_rounds,
        "status": "in_progress",
        "next_action": "literature",
        "created_at": now,
        "updated_at": now,
    }
    validate_state(state, slug)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    try:
        workspace.mkdir()
    except FileExistsError as error:
        raise WorkspaceError(
            f"workspace already exists: {workspace}; use --resume to inspect it or choose a new slug"
        ) from error
    for directory in DIRECTORIES:
        (workspace / directory).mkdir()
    index = (
        f"# Research workspace: {slug}\n\n"
        "This workspace was initialized by idea-shaokao. No research or review has been completed.\n\n"
        "- [State and next action](state.json)\n"
        "- [Issue tracker](issue_tracker.md)\n"
        "- [Literature](literature/)\n"
        "- [Candidate ideas](ideation/)\n"
        "- [Versioned proposals](proposal/)\n"
        "- [Review rounds](reviews/)\n"
        "- [Author rebuttals](rebuttals/)\n"
        "- [Experiments and evidence](experiments/)\n"
        "- [Final deliverables](final/)\n\n"
        "Maintain state.json after each checkpoint. Preserve earlier proposal versions, "
        "review reports, and experimental records.\n"
    )
    tracker = (
        "# Issue tracker\n\n"
        "No issues have been recorded yet. This does not imply that the idea has passed review.\n\n"
        "| Issue ID | Source | Claim / concern | Severity | Stage | Resolution criterion | Owner | Response | Evidence | Status | Reviewer / chair disposition |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    )
    files = {
        "README.md": index,
        "state.json": json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        "issue_tracker.md": tracker,
    }
    for name, content in files.items():
        with (workspace / name).open("x", encoding="utf-8", newline="\n") as output:
            output.write(content)
    return state


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("research"), help="research parent directory (default: ./research)")
    parser.add_argument("--slug", required=True, help="unique lowercase-hyphen workspace identifier")
    parser.add_argument("--topic", help="research topic (required when creating a workspace)")
    parser.add_argument("--venue", help="target venue and year (default: Unspecified)")
    parser.add_argument("--stage", choices=STAGES, help="review stage (default: proposal)")
    parser.add_argument("--max-rounds", type=int, help="review round budget, 1-4 (default: 4)")
    parser.add_argument("--resume", action="store_true", help="validate and inspect an existing workspace without modifying it")
    args = parser.parse_args(argv)
    try:
        slug = validate_slug(args.slug)
        workspace = args.root.expanduser().resolve() / slug
        if args.max_rounds is not None:
            validate_rounds(args.max_rounds)
        expected = {
            "topic": nonempty(args.topic, "topic") if args.topic is not None else None,
            "venue": nonempty(args.venue, "venue") if args.venue is not None else None,
            "review_stage": args.stage,
            "max_rounds": args.max_rounds,
        }
        if args.resume:
            state = resume_workspace(workspace, slug, expected)
        else:
            if args.topic is None:
                raise WorkspaceError("--topic is required unless --resume is used")
            state = initialize_workspace(
                workspace, slug, expected["topic"], expected["venue"] or "Unspecified",
                args.stage or "proposal", args.max_rounds if args.max_rounds is not None else 4,
            )
    except (WorkspaceError, OSError) as error:
        parser.error(str(error))
    print(json.dumps({"workspace": str(workspace), "resumed": args.resume, "state": state}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
