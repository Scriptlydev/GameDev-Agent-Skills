# Handoff to the next agent

**As of 2026-11-19:** full documentation set is created, **no working implementation**.

## Before starting

Read `../AGENTS.md`, `../STATE.md`, `../DECISIONS.md`, `PRD.md`, `ARCHITECTURE.md`, `QUALITY_GATE.md`, and `FIRST_TASK_FOR_CLAUDE.md`.

## Exact first action

Implement the minimal *read-only* Godot `scene-doctor` on disposable fixtures. Use Godot CLI/headless against 4.5.1 first; avoid linking this project to personal/revenue-producing game assets. Report findings to JSON, validate fixture outputs and add failure handling.

## Known environment constraints

- Owner has described Windows Shadow and a Debian server; no direct access to their files/tools is implied by this documentation.
- Existing Godot project environment includes 4.5.1, while current hi-godot/godot-ai v4 targets 4.7+.
- Codex CLI might already be used for unrelated projects: never overwrite global config or assume its runtime is free.

## Handoff template

- Branch/commit:
- Scope and files changed:
- Actual commands executed:
- Tests: passed / failed / skipped (with evidence paths):
- Findings and blockers:
- Potential security or licensing issues:
- Next atomic assignment:
