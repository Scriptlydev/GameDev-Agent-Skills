# First task for Claude Code — copy/paste instruction

## Objective

Build **G01: Godot scene-doctor** as a minimal, production-minded, read-only proof-of-concept. This is a new public open-source project, separate from private game repositories.

## Important context

- Read `AGENTS.md`, `STATE.md`, `DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/REPORT_SCHEMA.md`, `docs/QUALITY_GATE.md` and `docs/skills/G01-scene-doctor.md` first.
- Our Godot 4.5.1 path does NOT rely on Godot AI v4, which currently requires Godot 4.7+.
- Only a documentation scaffold exists; do not assume runtime components or tests have been created.
- Do not modify the owner's installed editor or private projects. Do not touch existing Arcanvil services/configs.

## Deliverables

1. Isolated Python package or CLI prototype exposing **only read-only inspect** command.
2. Valid `skills/godot/scene-doctor/SKILL.md` with correct frontmatter/triggers.
3. Minimal synthetic Godot 4.5.1 scene fixture with a *known good* and *known broken resource* case.
4. Output consistent with `docs/REPORT_SCHEMA.md` and useful diagnostic codes.
5. Unit tests, integration test plan and first real native Godot headless check if the binary is available.
6. Evidence log: exact commands, versions, hashes, exit codes, outputs and copied-project write audit.
7. Updated `STATE.md`, `docs/JOURNAL.md`, `docs/HANDOFF.md` and a reviewable PR.

## Constraints

- No internet-dependent functionality necessary for the first test.
- Godot may write import caches: always run on an expendable **copy** of a fixture.
- Unavailable Godot binary → flag integration as `NOT_TESTED` / `BLOCKED`; do not mark passed.
- Follow canonical path checks; reject path traversal and symlink escapes.
- Avoid auto-fix; no modifications to original inputs in this milestone.
- No proprietary user assets, tokens or private repo content.

## Acceptance tests

- Good fixture produces `pass` or justified `warn` with correct source IDs.
- Broken resource fixture produces an actionable finding and nonzero appropriate outcome.
- Untouched original fixture remains byte-for-byte identical, including untracked files.
- Missing Godot is reported as `blocked` rather than false success.
- `SKILL.md` passes official format validation when validator is installed.

## Response required

State which files were made, what exactly ran and passed, which checks were skipped, limitations and a safe next step. No inflated completion claims.
