# Development journal

Use append-only dated entries. Do **not** overwrite or reinterpret older test evidence.

## 2026-11-19 — documentation package generated

- Prepared product and engineering documentation, 30 skill specifications, contributor materials and issue templates.
- No integration deployed, no executable skill tested, no external repository modified.
- Next: review copyright and public name, then implement the Godot `scene-doctor` vertical slice.

## 2026-11-19 — public and private GitHub setup verified

- Public MIT repository populated with 79 new documentation and tooling files, preserving original MIT LICENSE.
- Private coordination repository initialized separately with 8 planning documents and an internal README; no secrets transferred.
- Public GitHub issues #1–#14 created for phased implementation.
- Branch `feat/g01-scene-doctor` created from initial main documentation commit.
- Verification: `python scripts/verify_docs.py` and `python -m unittest discover -s tests -v` passed locally. [GitHub documentation checks](https://github.com/Scriptlydev/GameDev-Agent-Skills/actions/runs/44571795435) completed successfully.
- No executable skills or game-engine integrations tested yet.
- Next: implement G01 with synthetic fixtures, real Godot CLI evidence and a reviewed PR.

## 2026-11-19 — G01 scene-doctor implemented (unverified)

- Agent/operator and branch: Claude Code, `feat/g01-scene-doctor` (ADR-008: one-time exception to the default "Codex implements").
- Files changed: `skills/godot/scene-doctor/` (SKILL.md, scripts/scene_doctor.py, scripts/godot_check_scenes.gd, references/DIAGNOSTICS.md); `tests/test_scene_doctor.py`; `tests/fixtures/godot/scene_doctor/` (5 synthetic fixtures); manifest, catalog and backlog status set to implemented_unverified; `scripts/verify_docs.py` accepts implemented_unverified when implementation_path exists; DECISIONS ADR-008–010; `docs/evidence/G01-scene-doctor-evidence.md`.
- Commands/tests executed: `python3 -m unittest discover -s tests` (43 run, OK, 2 skipped); `RealGodotTests` with Godot 4.7.2 and the untested-engine opt-in (2 OK); `python3 scripts/verify_docs.py` (PASS); a 20-run CLI matrix over the fixtures.
- Evidence and results: see the evidence file. Statuses and exit codes match SKILL.md. The fixture hashes were unchanged after all runs, and no report is `verified=true`.
- Blockers and security notes: Godot 4.5.1 NOT TESTED (binary not available); `skills-ref` SKIPPED (install not authorized). The tool is read-only: the engine runs only on a disposable copy, symlinks and unsafe paths are refused, and paths are redacted.
- Next action: PR review; a 4.5.1 run; the next skill implemented by Codex under a Claude-written contract.

## 2026-11-19 — G01 native check on Godot 4.5.1

- Agent/operator and branch: Claude Code, `feat/g01-scene-doctor`.
- Commands/tests executed: downloaded the official Godot 4.5.1 Linux build (zip checked against the release SHA512-SUMS); ran `RealGodotTests` (2 OK) and the 5-fixture CLI matrix on 4.5.1; ran `agentskills validate` (skills-ref 0.1.1) in a throwaway venv (valid).
- Evidence and results: good fixture gives `pass` with `verified=true`; broken fixtures give `fail` with `verified=true`; unsafe_paths is refused natively (B004). Fixture hashes were unchanged.
- Blockers and security notes: none. Windows and macOS not tested.
- Next action: PR review, then a decision on promoting G01 to ALPHA VERIFIED.

### New entry template

#### YYYY-MM-DD — short description
- Agent/operator and branch:
- Files changed:
- Commands/tests executed:
- Evidence and results:
- Blockers and security notes:
- Next action:

## 2026-11-19 — G07 test-runner implemented (unverified)

- Agent/operator and branch: Codex implementation (devhub task 24), Claude review; `feat/g07-test-runner`, stacked on `feat/g01-scene-doctor`.
- Files changed: `skills/godot/test-runner/` (SKILL.md, scripts/test_runner.py, scripts/g07_runner.gd, references/DIAGNOSTICS.md); `tests/test_test_runner.py`; `tests/fixtures/godot/test_runner/` (8 synthetic fixtures); G07 rows in manifest, catalog and backlog; `docs/evidence/G07-test-runner-evidence.md`; contract and ADR-011 from the earlier commit.
- Commands/tests executed: full suite with `GODOT_BIN` set to Godot 4.5.1, 69 tests OK (no skips); `RealGodotTests` for G07, 2 OK; a 9-case native CLI matrix; `verify_docs.py` PASS; `git diff --check` clean.
- Review finding fixed by the reviewer: an `empty` run reported `not_tested` with `verified=true`. `not_tested`, `blocked` and `error` are now never verified, and the test asserts it.
- Not tested: Windows, macOS, GUT, gdUnit4, C#, real projects.
- Next: G01 PR review, then the G07 PR.
