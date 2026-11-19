# Catalogue — 30 planned skills

**Important:** 29 entries are **specifications** only. G01 has a first implementation ([skills/godot/scene-doctor](../skills/godot/scene-doctor/SKILL.md)) that is **IMPLEMENTED / UNVERIFIED**: native evidence on the Godot 4.5.1 target (Linux, synthetic fixtures) is recorded and pending review for ALPHA VERIFIED. None is stable. Each linked document contains behavior, integration approach, tests and risk controls. Implementation must be proven separately.

## Catalog

| ID | Skill | Collection | Priority | Primary use case | Status |
|---|---|---|---|---|---|
| [U01](skills/U01-project-architect.md) | `project-architect` | Universal | P1 | Map project structure and propose a bounded task plan | SPECIFIED |
| [U02](skills/U02-code-reviewer.md) | `code-reviewer` | Universal | P1 | Review scoped diffs for correctness and regression risks | SPECIFIED |
| [U03](skills/U03-dependency-auditor.md) | `dependency-auditor` | Universal | P2 | Audit version compatibility, licenses and supply-chain exposure | SPECIFIED |
| [U04](skills/U04-documentation-generator.md) | `documentation-generator` | Universal | P2 | Generate truthful operator docs from tested behaviors | SPECIFIED |
| [U05](skills/U05-multi-agent-handoff.md) | `multi-agent-handoff` | Universal | P0 | Transfer exact project state between agents | SPECIFIED |
| [U06](skills/U06-safe-change-rollback.md) | `safe-change-rollback` | Universal | P0 | Guard file changes with preview, approval, snapshots and verified recovery | SPECIFIED |
| [G01](skills/G01-scene-doctor.md) | `scene-doctor` | Godot | P0 | Detect broken references and parse failures in Godot scenes | IMPLEMENTED / UNVERIFIED |
| [G02](skills/G02-script-debugger.md) | `script-debugger` | Godot | P1 | Diagnose GDScript parse errors and suspicious script wiring | SPECIFIED |
| [G03](skills/G03-collision-inspector.md) | `collision-inspector` | Godot | P1 | Inspect collision shapes, layers and obvious physics mistakes | SPECIFIED |
| [G04](skills/G04-node-architect.md) | `node-architect` | Godot | P2 | Review node hierarchies and suggest maintainable structures | SPECIFIED |
| [G05](skills/G05-asset-importer.md) | `asset-importer` | Godot | P2 | Verify imported GLB textures/materials and resource consistency | SPECIFIED |
| [G06](skills/G06-performance-auditor.md) | `performance-auditor` | Godot | P2 | Collect reproducible scene and script performance evidence | SPECIFIED |
| [G07](skills/G07-godot-test-runner.md) | `godot-test-runner` | Godot | P0 | Run selected Godot tests and summarize native results | SPECIFIED |
| [G08](skills/G08-safe-scene-editor.md) | `safe-scene-editor` | Godot | P2 | Apply approved scene edits with verification and recovery | SPECIFIED |
| [Y01](skills/Y01-csharp-code-doctor.md) | `csharp-code-doctor` | Unity | P2 | Diagnose Unity C# compile errors and API misuse | SPECIFIED |
| [Y02](skills/Y02-scene-analyzer.md) | `scene-analyzer` | Unity | P2 | Analyze Unity scenes for broken references and configuration issues | SPECIFIED |
| [Y03](skills/Y03-prefab-inspector.md) | `prefab-inspector` | Unity | P2 | Validate prefab connections, overrides and missing assets | SPECIFIED |
| [Y04](skills/Y04-physics-debugger.md) | `physics-debugger` | Unity | P2 | Detect suspicious collider/rigidbody layer configurations | SPECIFIED |
| [Y05](skills/Y05-asset-import-optimizer.md) | `asset-import-optimizer` | Unity | P2 | Inspect asset import size/format and suggest targeted optimizations | SPECIFIED |
| [Y06](skills/Y06-performance-profiler.md) | `performance-profiler` | Unity | P2 | Summarize measurable editor/player performance traces | SPECIFIED |
| [Y07](skills/Y07-unity-test-runner.md) | `unity-test-runner` | Unity | P2 | Execute Unity Edit Mode/Play Mode tests reliably | SPECIFIED |
| [Y08](skills/Y08-build-validator.md) | `build-validator` | Unity | P2 | Validate project build prerequisites and packaging | SPECIFIED |
| [B01](skills/B01-mesh-doctor.md) | `mesh-doctor` | Blender | P1 | Inspect mesh topology, normals and geometry defects | SPECIFIED |
| [B02](skills/B02-topology-analyzer.md) | `topology-analyzer` | Blender | P2 | Evaluate topology suitability for game assets | SPECIFIED |
| [B03](skills/B03-uv-inspector.md) | `uv-inspector` | Blender | P2 | Audit UV presence, overlap and bounds | SPECIFIED |
| [B04](skills/B04-material-auditor.md) | `material-auditor` | Blender | P2 | Detect missing textures, invalid nodes and export risks | SPECIFIED |
| [B05](skills/B05-rig-validator.md) | `rig-validator` | Blender | P1 | Verify armatures, weights and deform chains for game export | SPECIFIED |
| [B06](skills/B06-animation-checker.md) | `animation-checker` | Blender | P2 | Review action/NLA keyframe and rig compatibility | SPECIFIED |
| [B07](skills/B07-game-asset-optimizer.md) | `game-asset-optimizer` | Blender | P2 | Plan controlled poly/texture optimization and compare quality | SPECIFIED |
| [B08](skills/B08-batch-exporter.md) | `batch-exporter` | Blender | P1 | Export multiple assets with consistent naming and validation | SPECIFIED |

## Totals

- Godot: 8 (G01–G08).
- Unity: 8 (Y01–Y08).
- Blender: 8 (B01–B08).
- Universal: 6 (U01–U06).

## Recommended first six (may be revised after testing)

1. G01 scene-doctor (foundational native engine validation)
2. G07 godot-test-runner (evidence runner)
3. U05 multi-agent-handoff (agent continuity)
4. U06 safe-change-rollback (contract and tests, no writes enabled prematurely)
5. B01 mesh-doctor (Blender read-only pipeline)
6. U02 code-reviewer (review and regression discipline)

## Publication standard

A `SKILL.md` published in `skills/` is not evidence of functionality by itself. The current package intentionally stores future skill definitions in `docs/skills/`. They move to implementation only alongside executable components, real tests and honest status updates.
