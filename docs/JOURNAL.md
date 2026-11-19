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

### New entry template

#### YYYY-MM-DD — short description
- Agent/operator and branch:
- Files changed:
- Commands/tests executed:
- Evidence and results:
- Blockers and security notes:
- Next action:
