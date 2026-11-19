# Implementation roadmap — milestone and dependency plan

**Reference date:** 2026-11-19. Estimates assume access to the named editor runtimes and significant engineering hours; they are not guarantees.

## Phase 0 — preparation (days 1–2)

- Confirm public name, licensing/copyright holder and threat model.
- Make a *new* isolated GitHub repo, not a fork of a private game project.
- Verify Godot 4.5.1 binary path and create a tiny synthetic game fixture.
- Introduce Python package scaffold, report schema and docs lint.
- Record versions and blockers; no public functionality claim yet.

## Phase 1 — vertical slice (days 3–7)

- Implement **G01 `scene-doctor`** static+headless parser checks on fixture copy.
- Emit machine JSON and a short Markdown summary.
- Negative/positive tests; verify zero original project writes.
- Publish a short reproducible demo with observed commands/results.
- Quality gate: **ALPHA VERIFIED** only when engine actually ran.

## Phase 2 — small strong core (weeks 2–3)

- Build G02, G07, B01, U02, U05 as *candidates*, adapting priority to evidence.
- Verify first Blender headless path and universal reviews.
- Expand documented fixtures; test clean installation.
- Target six verified skills; no assumption about how quickly approval occurs.

## Phase 3 — broader beta (weeks 4–6)

- Add Unity adapter on a Windows test installation with approved license.
- Validate first Unity scene and C# workflows.
- Build safe-change gate with rollback drills before enabling any writes.
- Target 12–18 verified skills + public beta if security/release criteria pass.

## Phase 4 — full catalogue (weeks 7–12)

- Finish remaining Godot/Unity/Blender/universal skills.
- Cross-engine GLB path, batch export and performance audit workflows.
- Cross-platform CI and regression coverage for advertised versions.
- Target all 30 specs implemented and verified in a v1 candidate.

## Critical dependency chain

Read-only foundation → report schema → tests/fixtures → one native E2E → adapter expansion → safe write gate/rollback → optimization/import/export workflows → beta → stable.

## Milestones (proposed, not achieved)

| Milestone | Target | Hard proof |
|---|---|---|
| M1 | First week | G01 reproducible native CLI report + fixture hashes |
| M2 | Weeks 2–3 | Six verified skills, docs and independent PR reviews |
| M3 | Weeks 4–6 | Unity/Blender tested + beta safety gate |
| M4 | Weeks 7–12 | Thirty verified specs, release checklist and evidence pack |

## Priority / backlog order

P0: G01, U06 (snapshot contract, no auto writes), U05, G07. P1: B01, B08, U02, G02, G03. P2: Y01, Y02, Y07 and dependent Unity skills after editor is available.

## Pause / reevaluate triggers

- An editor version is incompatible with its adapter.
- A skill silently modifies test inputs.
- Rollback loses an untracked file.
- A source license is unclear or restricts intended distribution.
- Claude/Codex agents generate unreviewed fragile code faster than it can be tested.
- Public demand indicates a narrower tool would be more useful than 30 features.
