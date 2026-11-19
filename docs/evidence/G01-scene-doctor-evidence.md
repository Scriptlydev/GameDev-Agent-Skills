# G01 scene-doctor — evidence (2026-11-19)

**Status: IMPLEMENTED / UNVERIFIED, candidate for ALPHA VERIFIED (Linux, Godot 4.5.1)
pending PR review.** The native check passed on the pinned target Godot 4.5.1
(official build, checksum verified) and also on 4.7.2 behind the untested-engine opt-in.
Windows and macOS are not tested.

Paths are redacted: `<repo>` = repository checkout, `<scratch>` = disposable
directory outside the repository, `<godot>` = Godot executable.

## Environment

| Item | Value |
|---|---|
| OS | Linux 6.1 (Debian, x86_64, headless server) |
| Python | 3.11.2 (stdlib only, run with `-I`) |
| Godot 4.5.1 (target) | Official `Godot_v4.5.1-stable_linux.x86_64.zip` from the godotengine/godot `4.5.1-stable` release; zip matches the release `SHA512-SUMS.txt`; `--version` = `4.5.1.stable.official.f62fdbde1`; binary sha256 `db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199` |
| Godot 4.7.2 (untested) | `--version` = `4.7.2.stable.official.ed1daf0bf`; binary sha256 `8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e` |
| Fixtures | Synthetic only, `tests/fixtures/godot/scene_doctor/` (no private game files) |

## Automated tests

```text
python3 -m unittest discover -s tests -v
  -> Ran 43 tests: OK (skipped=2)   # the 2 skips are the real-Godot tests
GODOT_BIN=<godot-4.5.1> python3 -m unittest tests.test_scene_doctor.RealGodotTests -v
  -> Ran 2 tests: OK (about 26 s)
GODOT_BIN=<godot-4.7.2> G01_ALLOW_UNTESTED=1 python3 -m unittest tests.test_scene_doctor.RealGodotTests -v
  -> Ran 2 tests: OK (about 28 s)
agentskills validate skills/godot/scene-doctor      # skills-ref 0.1.1, throwaway venv
  -> Valid skill: skills/godot/scene-doctor (exit 0)
python3 scripts/verify_docs.py
  -> PASS: manifest and local documentation links validated. No skill is marked verified or stable.
```

The unit tests use a fake Godot executable to cover each engine path: tested
version, untested version with and without the opt-in flag, Godot 3 or garbage
version, load failure, missing DONE marker, timeout with process-group kill, and
an engine that writes into the workspace. They also cover refusals R001–R004,
symlink escape, case mismatch, stale UID, `.gdignore`, binary or oversized
files, and the fixture write audit.

The external `skills-ref` validator (0.1.1) was run in a throwaway virtual
environment outside the repository and reported the skill valid. `SkillPackageTests`
checks the same frontmatter rules in CI.

## Native check on Godot 4.5.1 (pinned target)

`python3 -I skills/godot/scene-doctor/scripts/scene_doctor.py inspect <fixture> --godot <godot-4.5.1> --report <scratch>/r.json --evidence-dir <scratch>/logs`

| Fixture | Exit | status | verified | native | Codes (findings / errors) |
|---|---|---|---|---|---|
| good | 0 | pass | **true** | ok | — |
| broken_texture | 1 | fail | true | ok | E002, E021 |
| missing_script | 1 | fail | true | ok | E003, E021 |
| malformed | 1 | fail | true | ok | E001, E005, E006, E007, E011, E013, E020, E021, W002 |
| unsafe_paths | 1 | fail | false | unsafe | E004, I001 / B004 (engine not run) |

On the `fail` rows, `verified=true` means the engine confirmed the errors natively
(ADR-010). The fixture hashes were identical before and after these 5 runs, and
the reports and logs contain no home or project paths.

## CLI matrix on fixtures (static, no engine, 4.7.2)

Command shape (`<mode>` below):

- `static`: `python3 -I skills/godot/scene-doctor/scripts/scene_doctor.py inspect <fixture> --static-only --report <scratch>/r.json`
- `no-godot`: same without `--static-only`, `GODOT_BIN` unset, `PATH=/usr/bin:/bin` (no Godot)
- `4.7.2`: `--godot <godot>` without the opt-in flag
- `4.7.2+flag`: `--godot <godot> --allow-untested-engine --evidence-dir <scratch>/logs`

| Fixture | Mode | Exit | status | verified | native | Codes (findings / errors) |
|---|---|---|---|---|---|---|
| good | static | 3 | not_tested | false | not_requested | — |
| good | no-godot | 3 | blocked | false | no_engine | B001 |
| good | 4.7.2 | 3 | blocked | false | blocked | B003 |
| good | 4.7.2+flag | 0 | warn | false | ok | W010 |
| broken_texture | static | 1 | fail | false | not_requested | E002 |
| broken_texture | no-godot | 1 | fail | false | no_engine | E002 / B001 |
| broken_texture | 4.7.2 | 1 | fail | false | blocked | E002 / B003 |
| broken_texture | 4.7.2+flag | 1 | fail | false | ok | E002, E021, W010 |
| missing_script | static | 1 | fail | false | not_requested | E003 |
| missing_script | 4.7.2+flag | 1 | fail | false | ok | E003, E021, W010 |
| malformed | static | 1 | fail | false | not_requested | E001, E005, E006, E007, E011, E013, W002 |
| malformed | 4.7.2+flag | 1 | fail | false | ok | static codes + E020, E021, W010 |
| unsafe_paths | static | 1 | fail | false | not_requested | E004, I001 |
| unsafe_paths | 4.7.2+flag | 1 | fail | false | unsafe | E004, I001 / B004 (engine not run) |

The `no-godot` and `4.7.2` (no flag) rows of missing_script, malformed and
unsafe_paths give the same static codes with B001, B003 or B004 respectively
(B004 for unsafe_paths in both cases). All 20 reports were checked for the
required fields of `docs/REPORT_SCHEMA.md` 0.1.0 (none missing); the suite asserts the same.

## Non-destructive audit

- The sha256 of the 17 fixture files was identical before and after all 20 runs
  (`cmp` reported no difference), and `git status` showed no change under the
  fixtures.
- Every native run works on a disposable copy without `.godot/` and `.git/`,
  with an isolated HOME/XDG profile. The tool hashes the original tree before and
  after each run, and any difference makes the run `error` (G01-X002). The
  fake-engine `mutate` test covers that path.
- A grep of the reports and logs for home or project paths matched only the
  intentional unsafe input `/tmp/g01-absolute.png`, which is a fixture value
  quoted as evidence of G01-E004 and is never opened.

## Not demonstrated

- Windows and macOS: NOT TESTED.
- Real-world projects: NOT TESTED (synthetic fixtures only, by design).
- Instanced sub-scene contents, binary `.scn`/`.res` and UID-only references
  without sidecars: documented limits in `references/DIAGNOSTICS.md`.
