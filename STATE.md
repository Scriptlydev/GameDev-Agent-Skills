# STATE — verified project state

**Last documented:** 2026-11-19 (Europe/Paris). **Overall state: DESIGN + G01 and G07 IMPLEMENTED / UNVERIFIED. G01 is a candidate for ALPHA VERIFIED (Linux, Godot 4.5.1) pending PR review; G07 waits for the G01 PR.**

| Area | Status | Evidence |
|---|---|---|
| Mission, PRD and architecture | Documented | Files in `docs/` |
| 30 skill definitions | Documented | `docs/SKILL_CATALOG.md`, `docs/skills/` |
| Agent Skills spec alignment | Requirements recorded; runtime validation pending | `docs/SKILL_FORMAT.md` |
| Executable skills | G01 `scene-doctor` and G07 `test-runner`: IMPLEMENTED / UNVERIFIED; 28 others NOT BUILT | `skills/godot/scene-doctor/`, `skills/godot/test-runner/`, evidence: [G01](docs/evidence/G01-scene-doctor-evidence.md), [G07](docs/evidence/G07-test-runner-evidence.md) |
| Godot 4.5.1 headless integration | PASS on synthetic fixtures (Linux): `verified=true` on good and broken fixtures | Official checksum-verified build; [G01 evidence](docs/evidence/G01-scene-doctor-evidence.md) |
| G07 native run on Godot 4.5.1 | PASS on 9 synthetic cases (Linux): exit codes, statuses and totals as specified; fixtures unchanged | [G07 evidence](docs/evidence/G07-test-runner-evidence.md) |
| Godot 4.7.2 headless (untested-engine opt-in) | PASS on synthetic fixtures, `verified=false` by design | [G01 evidence](docs/evidence/G01-scene-doctor-evidence.md) |
| Godot 4.7+ MCP adapter | NOT TESTED | Candidate `hi-godot/godot-ai` |
| Unity integration | NOT TESTED | Requires installed licensed Unity Editor |
| Blender integration | NOT TESTED | Requires real Blender installation |
| Documentation CI | PASS on GitHub Actions | [Documentation checks](https://github.com/Scriptlydev/GameDev-Agent-Skills/actions/runs/44571795435); local validator and two unit tests |
| Runtime skill / security tests | Full suite: 69 tests OK with `GODOT_BIN` set to 4.5.1 (no skips); without it, 4 real-Godot tests are skipped. G01: 43 unit tests (41 pass, 2 real-Godot tests skipped by default), and those 2 real-Godot tests pass on 4.5.1 and on 4.7.2 (opt-in) | `tests/test_scene_doctor.py` |
| `skills-ref` external validator | PASS for G01 (skills-ref 0.1.1) | [G01 evidence](docs/evidence/G01-scene-doctor-evidence.md) |
| Public repository | VERIFIED | `Scriptlydev/GameDev-Agent-Skills`, MIT existing; docs imported and 14 issues created |
| Actual skill adoption / downloads | NOT VERIFIED | No claim of users or installs |

## Known decisions

- One monorepo of 30 *planned* skills: Godot 8, Unity 8, Blender 8, universal 6.
- First executable implementation: Godot `scene-doctor` read-only, CLI/headless compatibility path for Godot 4.5.1.
- Existing MCP tools remain optional external dependencies; do not vendor them by default.
- Project presentation focuses on functionality; maintain accurate provenance, license notices and truthful contributor history.

## Immediate next task

1. Open and review the G01 pull request (`feat/g01-scene-doctor` → `main`). Do not merge without review.
2. After review, the reviewer decides whether to promote G01 to ALPHA VERIFIED (Linux + Godot 4.5.1). Evidence is recorded; the manifest status is still `implemented_unverified`.
3. G07 branch `feat/g07-test-runner` is stacked on G01: open its PR once G01 is merged (or review it against `feat/g01-scene-doctor`).
4. Next skill: per `docs/QUOTA_AND_QUALITY.md`, Claude writes the contract and Codex implements it (ADR-008).

## Blockers / unknowns

- Windows/macOS behaviour of G01 and G07 not tested.
- No GitHub API access from the automation host (SSH push only): PRs are opened by the owner.
- Unity and Blender editor installations/versions have not been checked for this project.
- No third-party code has been imported. Final package/dependency licenses require a per-release audit.
