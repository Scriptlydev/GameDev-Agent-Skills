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

## Working with Codex without wasting quota

Follow [`docs/QUOTA_AND_QUALITY.md`](docs/QUOTA_AND_QUALITY.md) as well as `docs/AGENT_WORKFLOW.md`. Default to **Claude as the scoped planner, architecture/security reviewer and final diff reviewer**, and **Codex CLI for bulk implementation, fixtures, unit tests and deterministic CI fixes**. Do not duplicate Codex's work or request full-repository dumps in chat; inspect focused diffs and test evidence. Give Codex an atomic issue, contract, allowed files and test criteria. Escalate only when a concrete failure or higher-risk decision requires deeper reasoning. Never skip native engine tests, security review or regression tests to save quota.

When Codex is unavailable or blocked, Claude may implement in an isolated branch, recording that delegation decision. Agents must not alter each other's global configuration or unrelated projects.
