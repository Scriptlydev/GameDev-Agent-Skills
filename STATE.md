# STATE — verified project state

**Last documented:** 2026-11-19 (Europe/Paris). **Overall state: DESIGN + first skill G01 IMPLEMENTED / UNVERIFIED (PR pending review).**

| Area | Status | Evidence |
|---|---|---|
| Mission, PRD and architecture | Documented | Files in `docs/` |
| 30 skill definitions | Documented | `docs/SKILL_CATALOG.md`, `docs/skills/` |
| Agent Skills spec alignment | Requirements recorded; runtime validation pending | `docs/SKILL_FORMAT.md` |
| Executable skills | G01 `scene-doctor`: IMPLEMENTED / UNVERIFIED; 29 others NOT BUILT | `skills/godot/scene-doctor/`, [evidence](docs/evidence/G01-scene-doctor-evidence.md) |
| Godot 4.5.1 headless integration | NOT TESTED | 4.5.1 binary not available in the G01 session; target version unproven |
| Godot 4.7.2 headless (untested-engine opt-in) | PASS on synthetic fixtures, `verified=false` by design | [G01 evidence](docs/evidence/G01-scene-doctor-evidence.md) |
| Godot 4.7+ MCP adapter | NOT TESTED | Candidate `hi-godot/godot-ai` |
| Unity integration | NOT TESTED | Requires installed licensed Unity Editor |
| Blender integration | NOT TESTED | Requires real Blender installation |
| Documentation CI | PASS on GitHub Actions | [Documentation checks](https://github.com/Scriptlydev/GameDev-Agent-Skills/actions/runs/44571795435); local validator and two unit tests |
| Runtime skill / security tests | G01: 43 unit tests (41 pass, 2 real-Godot tests skipped by default), and those 2 real-Godot tests pass on 4.7.2 | `tests/test_scene_doctor.py` |
| `skills-ref` external validator | SKIPPED | Install not authorized; the in-repo frontmatter test is a partial substitute |
| Public repository | VERIFIED | `Scriptlydev/GameDev-Agent-Skills`, MIT existing; docs imported and 14 issues created |
| Actual skill adoption / downloads | NOT VERIFIED | No claim of users or installs |

## Known decisions

- One monorepo of 30 *planned* skills: Godot 8, Unity 8, Blender 8, universal 6.
- First executable implementation: Godot `scene-doctor` read-only, CLI/headless compatibility path for Godot 4.5.1.
- Existing MCP tools remain optional external dependencies; do not vendor them by default.
- Project presentation focuses on functionality; maintain accurate provenance, license notices and truthful contributor history.

## Immediate next task

1. Review the G01 pull request (`feat/g01-scene-doctor` → `main`). Do not merge without review.
2. Run the 4.5.1 native check: `GODOT_BIN=<godot-4.5.1> python3 -m unittest tests.test_scene_doctor.RealGodotTests -v`, plus the CLI matrix in the evidence file. Record the results there. Only then can G01 move beyond `implemented_unverified`.
3. Next skill: per `docs/QUOTA_AND_QUALITY.md`, Claude writes the contract and Codex implements it (see ADR-008).

## Blockers / unknowns

- Godot 4.5.1 binary not available to the agent session; only 4.7.2 was tested (behind `--allow-untested-engine`).
- `skills-ref` validator not run (install not authorized).
- Windows/macOS behaviour of G01 not tested.
- Unity and Blender editor installations/versions have not been checked for this project.
- No third-party code has been imported. Final package/dependency licenses require a per-release audit.
