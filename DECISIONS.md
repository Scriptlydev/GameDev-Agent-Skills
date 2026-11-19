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

## Open decisions

- Final public repository name and organization/owner (working name: `gamedev-agent-skills`).
- Minimum supported Unity and Blender versions after test fixture checks.
- CLI packaging/distribution for read-only analyzer (Python package, plugin, or both).
- Safe-approval UX and snapshot backend choice for write-enabled skills.
- Telemetry policy: initial default is no project-content collection; formal policy required if any diagnostics are added.
