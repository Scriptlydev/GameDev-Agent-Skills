# CLAUDE.md — Claude Code entry point

Follow [`AGENTS.md`](AGENTS.md) **before** making changes. Do not treat this file as permission to execute tools remotely.

## Mission

Implement a small, fully verified vertical slice of **GameDev Agent Skills**, beginning with a read-only Godot `scene-doctor` workflow for Godot 4.5.1 CLI/headless. Keep other engines and modifications behind explicit milestones.

## Session startup

1. Read `STATE.md`, `DECISIONS.md`, `docs/HANDOFF.md` and `docs/FIRST_TASK_FOR_CLAUDE.md`.
2. Show a short plan with the exact scope, affected files, risks and tests.
3. Create an isolated branch/worktree if authorized.
4. Implement the smallest useful slice; run offline/unit checks before invoking a real engine.
5. Update the journal and handoff with observed evidence, then open a PR for review.

## Session end report

- Completed / partially completed / blocked (never guess)
- Commit/branch, files and behavior changed
- Tests run + explicit pass/fail/skipped state + logs
- Security implications and rollback instructions
- Next atomic task

If unable to launch Godot, report it as **not tested**, not "working". Do not silently upgrade or reconfigure the owner's existing Godot installation.