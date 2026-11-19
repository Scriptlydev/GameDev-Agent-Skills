# Product Requirements Document — v0.1

**Product:** GameDev Agent Skills | **Owner:** Scriptlydev | **Date:** 2026-11-19 | **Status:** proposed, implementation pending.

## Problem statement

Game developers can instruct AI agents to edit project files, but such workflows often lack engine-aware validation, safely repeatable tests, traceable results and an auditable path back to the initial project state. Existing MCP servers expose operations but do not guarantee robust end-to-end workflows for every job.

## Target users

1. Indie developers using Claude Code/Codex with Godot, Unity or Blender.
2. Technical artists exporting GLB/FBX assets and validating downstream import.
3. Small studios wanting standardized project checks and safe AI collaboration.
4. Open-source contributors reviewing AI-assisted changes in game repositories.

## Value proposition

**One portable agent-skill collection, three authoring ecosystems, consistently verified outcomes.** Skills run repeatable processes on existing engine tooling, emit evidence and avoid destructive defaults.

## Product goals

- G1: ship one read-only, reproducible Godot workflow on a real 4.5.1 fixture.
- G2: ship six high-quality skills before expanding the catalogue.
- G3: eventually ship eight tested skills per engine and six universal ones.
- G4: every claimed supported editor/version combination has documented run evidence.
- G5: all write-enabled skills support preview, explicit approval and tested recovery.
- G6: support multiple agent clients via vendor-neutral `SKILL.md` instructions.

## Out of scope for first release

- Building a new game engine or replacing Unity/Godot/Blender editors.
- Guaranteed one-click creation of entire commercial games.
- Unrestricted code execution on remote machines.
- Automatic changes to production projects with no approval.
- Training or hosting custom LLMs; collecting project files as telemetry.
- Promising compatibility with untested editor versions or every MCP implementation.

## Functional requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FR-01 | Discover skills by metadata without reading every script | Manifest/frontmatter validation and client discovery smoke test |
| FR-02 | Inspect a project without modifying files | Hashes unchanged on a read-only fixture |
| FR-03 | Return consistent machine-readable findings | Schema check + sample positive and negative reports |
| FR-04 | Support engine/version detection and graceful incompatibility | Version matrix including expected refusal cases |
| FR-05 | Provide reproducible command and tool provenance | Run log records hashes and versions |
| FR-06 | Require approval before writes and destructive operations | Denied approval means no file changes |
| FR-07 | Recover from failed or rejected modifications | Restore test on tracked and untracked fixtures |
| FR-08 | Support offline/local use when tools permit | Offline smoke tests on local fixtures |
| FR-09 | Provide diagnostic user-facing messages | Error cases documented and tested |
| FR-10 | Keep third-party source and assets separately licensed | Release audit and SBOM / dependency list |
| FR-11 | Offer documented install paths for each engine | Clean machine test records before public claim |
| FR-12 | Supply scoped agent instructions for collaborating via GitHub | Handoff and PR metadata checked during review |

## Non-functional requirements

- **Security:** least privilege; restricted roots; no unauthenticated remote Blender execution; no secrets in logs.
- **Reliability:** deterministic output where possible; no silently successful partial failures; retry only idempotent reads.
- **Portability:** Windows and Linux for CLI analysis first; macOS a future verified target.
- **Maintainability:** independently versioned adapter interfaces; unit fixtures; documented deprecations.
- **Performance:** record baseline and compare against identical fixture/hardware; no numerical target until measured.
- **Privacy:** run locally by default and avoid uploading game files or telemetry automatically.

## Measures of success

- Technical: test pass rate, crashes, import/export validation failures, incident count, reproducibility of diagnostics, restore reliability.
- Adoption (only after publication): documented external users, verified downstream dependencies, issue resolution rate, independent contributions and repeat usage.
- Avoid vanity KPI inflation: stars and commits alone do not prove actual use.

## Release criteria

Alpha: one end-to-end engine task + test fixtures and truthful docs. Public beta: at least six independently tested skills + install instructions + safety gate. V1: 30 skills tested on declared versions, security checklist, release notes and real recovery drills.

## Dependencies

Optional external integrations: Godot AI (MIT), MCP for Unity (MIT), MCP for Blender (MIT). See `THIRD_PARTY_NOTICES.md` and `docs/COMPATIBILITY.md` for version caveats.
