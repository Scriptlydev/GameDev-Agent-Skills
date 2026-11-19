# Architecture Decision Log

## ADR-001 — One skills monorepo (2026-11-19, accepted)

**Decision:** one repository housing separate engine-specific collections, universal skills, and adapters. **Why:** consistent safeguards, QA, documentation and discoverability. **Trade-off:** repository size and cross-engine CI complexity.

## ADR-002 — Agent Skills standard (accepted)

Skills use `SKILL.md` and progressive resource loading; no vendor-only syntax is required for core operation. Vendor-specific enhancements must be optional. Source: https://agentskills.io/specification.

## ADR-003 — Reuse MCP integrations as dependencies, not wholesale copies (accepted)

Candidates: `hi-godot/godot-ai`, `CoplayDev/unity-mcp`, `ahujasid/mcp-for-blender`. The original repositories are not bundled. Pin tested versions. If code is copied later, add required license notices and audit dependencies.

## ADR-004 — Two Godot compatibility tracks (accepted)

- **Track A:** Godot 4.5.1 read-only CLI/headless analysis (first release target).
- **Track B:** Godot 4.7+ editor integration using compatible version-pinned Godot AI (future target).

Never assume Godot AI v4 operates on 4.5.1. Confirm alternate adapters separately; do not mix editor configurations.

## ADR-005 — Safety and evidence (accepted)

Read-only by default. Any write needs an explicit plan and permission; snapshot project state, apply minimal edits, test, and support rollback. Findings include reproducibility metadata.

## ADR-006 — MIT for original code (provisional)

MIT is intended for this project's original code/documentation. Before public publication, maintainer must confirm copyright holder and file-level compatibility. Existing third-party licenses remain intact.

## ADR-007 — Public naming and attribution (accepted)

External-facing docs describe functions and tests, not an exaggerated account of authorship. Do not fabricate individual contributions, hide mandated license notices, or misrepresent development methods where disclosure is required.

## ADR-008 — G01 implemented by Claude Code (2026-11-19, accepted)

`docs/QUOTA_AND_QUALITY.md` makes Codex the default implementer, with Claude reviewing. For G01 the maintainer explicitly asked Claude Code to implement and finish the skill in a single session, so Claude owned the whole G01 file scope (`skills/godot/scene-doctor/`, `tests/test_scene_doctor.py`, `tests/fixtures/godot/scene_doctor/`) and no second agent worked on the same task. This is a recorded one-time exception. From the next issue onward the default applies again: Claude writes the contract and acceptance criteria, Codex implements on an isolated branch, and Claude does one focused review of the diff and its evidence.

## ADR-009 — G01 engine version policy (2026-11-19, accepted)

The tested target set is `SUPPORTED_ENGINE_VERSIONS = ("4.5.1",)`. Any other Godot 4.x version is refused as `blocked` (G01-B003) unless the caller passes `--allow-untested-engine`. With that flag the native check runs, adds G01-W010, and the run is never reported as `verified`. Godot 3 and unparseable versions are refused (G01-B002). The only native evidence so far comes from 4.7.2 behind this flag, so G01 stays `implemented_unverified` until a 4.5.1 run is recorded.

## ADR-010 — Meaning of `verified` in G01 reports (2026-11-19, accepted)

`verified=true` means only this: the native check completed (DONE marker seen) on a tested engine version, and the before/after hash audit found no change to the project. It says nothing about the project being healthy, so a `fail` report can be `verified=true` when the engine confirmed the errors. Static-only, blocked, timed-out or untested-engine runs are always `verified=false`.

## Open decisions

- Final public repository name and organization/owner (working name: `gamedev-agent-skills`).
- Minimum supported Unity and Blender versions after test fixture checks.
- CLI packaging/distribution for read-only analyzer (Python package, plugin, or both).
- Safe-approval UX and snapshot backend choice for write-enabled skills.
- Telemetry policy: initial default is no project-content collection; formal policy required if any diagnostics are added.
