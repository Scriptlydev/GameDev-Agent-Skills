# Handoff to the next agent

**As of 2026-11-19:** G01 `scene-doctor` is IMPLEMENTED / UNVERIFIED on `feat/g01-scene-doctor` and its PR awaits review. No skill is verified or stable.

## Before starting

Read `../AGENTS.md`, `../STATE.md`, `../DECISIONS.md`, `PRD.md`, `ARCHITECTURE.md`, `QUALITY_GATE.md`, and `FIRST_TASK_FOR_CLAUDE.md`.

## GitHub entry points

- Public repo: https://github.com/Scriptlydev/GameDev-Agent-Skills
- First branch: `feat/g01-scene-doctor`
- First work item: https://github.com/Scriptlydev/GameDev-Agent-Skills/issues/5
- Docs checks: https://github.com/Scriptlydev/GameDev-Agent-Skills/actions/runs/44571795435
- Private planning is independent; do not mirror it without authorization.

## Current handoff (G01)

- Branch/commit: `feat/g01-scene-doctor` (see the PR to `main`; not merged).
- Scope and files changed: `skills/godot/scene-doctor/`, `tests/test_scene_doctor.py`, `tests/fixtures/godot/scene_doctor/`, `docs/evidence/G01-scene-doctor-evidence.md`, manifest, catalog, backlog, `scripts/verify_docs.py`, DECISIONS ADR-008–010.
- Actual commands executed: listed in `docs/evidence/G01-scene-doctor-evidence.md`.
- Tests: 41 passed and 2 skipped (real Godot, opt-in); the real-Godot tests pass on 4.7.2 with `G01_ALLOW_UNTESTED=1`; `verify_docs.py` PASS; `skills-ref` SKIPPED.
- Findings and blockers: Godot 4.5.1 NOT TESTED. Known limits: instanced sub-scenes are opaque, binary resources are not parsed, and UID-only references are not resolved without sidecars.
- Potential security or licensing issues: none known. There are no dependencies (stdlib only) and no third-party code.
- Next atomic assignment:
  1. Reviewer: review the PR diff and evidence.
  2. Maintainer: provide a Godot 4.5.1 binary and run the commands in the evidence file.
  3. Next skill: Claude writes the issue contract; Codex implements on an isolated branch (ADR-008).

## Exact first action for G01 follow-up

Run `GODOT_BIN=<godot-4.5.1> python3 -m unittest tests.test_scene_doctor.RealGodotTests -v` on a machine with Godot 4.5.1. Record the results in the evidence file, then update the status only if the evidence supports it.

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
