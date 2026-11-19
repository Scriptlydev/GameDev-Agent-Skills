# GameDev Agent Skills

> **Status: planning / documentation only.** No skill in this repository is presented as implemented or production-ready yet.

**GameDev Agent Skills** is a proposed open-source toolkit of 30 portable [Agent Skills](https://agentskills.io/specification) for **Godot, Unity, Blender, and cross-engine game development**. Rather than replacing existing MCP servers, it adds repeatable workflows, quality checks, consistent evidence, and safe-change conventions *on top* of compatible tools.

## Planned coverage

| Collection | Proposed skills | Target workflows |
|---|---:|---|
| Godot | 8 | Scene/script analysis, physics, assets, tests, editing, performance |
| Unity | 8 | C# diagnostics, scenes/prefabs, physics, tests, assets, builds |
| Blender | 8 | Geometry, UVs, materials, rigs, animations, optimization, export |
| Universal | 6 | Planning, reviews, dependency audits, handoffs, documentation, rollback |
| **Total** | **30** | **Specifications drafted; implementation pending** |

See **[all 30 specifications](docs/SKILL_CATALOG.md)**, **[product requirements](docs/PRD.md)** and **[architecture](docs/ARCHITECTURE.md)**.

## What makes this different

1. **Evidence-first:** each skill returns structured findings, test artifacts, software versions and an explicit `verified` / `unverified` status.
2. **Safe by default:** read-only inspections first; reviewable plans and explicit approval before modifications.
3. **Reusable integrations:** compatible adapters for existing open-source MCP tools, with honest version constraints.
4. **Cross-engine asset workflow:** inspect a game asset in Blender, validate it, export to Godot or Unity, and verify its import.
5. **Agent interoperability:** transferable instructions for Claude Code, Codex and other clients supporting the Agent Skills standard.

## Project status

- ✅ Product, architecture, 30 skill definitions, quality gates and governance documents prepared.
- ⬜ Executable skill implementations, real application integrations and automated tests **not yet built**.
- ⬜ CI workflows, compatibility matrix and public demos **not yet validated**.
- ⬜ Community metrics or adoption: **none claimed**.

## Getting started as a developer

Read the docs in this order:

1. [`AGENTS.md`](AGENTS.md) — mandatory safe development rules.
2. [`STATE.md`](STATE.md) — verified state and current blockers.
3. [`DECISIONS.md`](DECISIONS.md) — decisions already made, and pending trade-offs.
4. [`docs/PRD.md`](docs/PRD.md) — scope and acceptance criteria.
5. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — components and boundaries.
6. [`docs/SKILL_CATALOG.md`](docs/SKILL_CATALOG.md) — the exact 30 planned skills.
7. [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) — first steps and milestones.
8. [`docs/QUALITY_GATE.md`](docs/QUALITY_GATE.md) — what qualifies as "working".

For a concrete first assignment, use [`docs/FIRST_TASK_FOR_CLAUDE.md`](docs/FIRST_TASK_FOR_CLAUDE.md).

## Dependencies and acknowledgements

Candidate optional integrations (**not bundled**):

- [Godot AI](https://github.com/hi-godot/godot-ai) (MIT; currently Godot 4.7+).
- [MCP for Unity](https://github.com/CoplayDev/unity-mcp) (MIT; check tagged compatibility before installation).
- [MCP for Blender](https://github.com/ahujasid/mcp-for-blender) (MIT; arbitrary Python tool requires careful isolation).
- [Agent Skills specification](https://agentskills.io/specification) (format reference).

We do **not** imply endorsement or affiliation with Godot, Unity, Blender, Anthropic, OpenAI, or the above maintainers.

## Development and licensing

Planned license: **MIT** for code and original docs (see [`LICENSE`](LICENSE)). Third-party code/assets require separate license review. Contributions welcome once initial implementation is published; please read [`CONTRIBUTING.md`](CONTRIBUTING.md).

Maintainer: **Scriptlydev**. Project inception: 2026-11-19.
