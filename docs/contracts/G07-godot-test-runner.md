# G07 godot-test-runner — implementation contract v0.1

Status: SPECIFIED, contract ready for implementation. Spec: [`../skills/G07-godot-test-runner.md`](../skills/G07-godot-test-runner.md). Decision: ADR-011.

## Goal

A read-only CLI that copies an authorized Godot 4 project to a disposable workspace, runs the project's GDScript tests (built-in convention below) headless, and writes a `report.json` that follows `docs/REPORT_SCHEMA.md` 0.1.0 with `skill_id: "G07"`.

## Non-goals (v0.1)

- GUT, gdUnit4 and C# tests; MCP or editor plugin; Godot 3.
- Any write, fix, re-save or import into the original project. Exporting builds.
- Windows and macOS claims. They may work but stay NOT TESTED.

## Test convention (built in)

- The tests directory defaults to `res://tests`. `--tests-dir res://<dir>` overrides it, and it must stay inside the root (`..`, absolute paths, URLs and symlinks are refused).
- Test files are `test_*.gd`, collected recursively and sorted. Each file `extends RefCounted` (or `Object`) and needs no constructor arguments.
- Test methods are the script's own methods named `test_*` with 0 arguments, sorted by name. The optional `before_each()` and `after_each()` run around each test.
- Return value:
  - `null` (no return) means pass.
  - A `String` starting with `SKIP:` means skipped.
  - Any other `String` means fail, with that string as the message.
  - Any other type means fail, with the message `non-string return`.
- `--filter <substring>` keeps only tests whose `file::method` id contains the substring.
- A GDScript runtime error inside a test means fail. It is detected from a per-test start marker without an end marker, plus a `SCRIPT ERROR:` line. The runner must go on to the next test whenever the engine allows it.
- A file that fails to load or parse produces G07-E001 for that file. Its tests are not counted as passed.

## CLI

```
python3 -I skills/godot/test-runner/scripts/test_runner.py run <project> \
    [--godot <bin>] [--allow-untested-engine] [--tests-dir res://tests] \
    [--filter <s>] [--timeout <s, default 120, max 900>] \
    --report <outside>/report.json [--evidence-dir <outside>/logs]
```

Exit codes:

| Code | Meaning |
|---|---|
| 0 | pass (all executed tests passed), or warn |
| 1 | fail |
| 2 | input refused |
| 3 | blocked or not_tested |
| 4 | error |

Status rules:
- `warn` covers two cases:
  - an untested engine with the opt-in flag;
  - some tests skipped and none failed.
- Zero collected tests gives `not_tested` (G07-W001), never `pass`.

## Diagnostics (stable codes, documented in `references/DIAGNOSTICS.md`)

Findings:

| Code | Meaning |
|---|---|
| G07-E001 | test_script_load_failed (parse or build error) |
| G07-E002 | test_failed |
| G07-E003 | test_runtime_error |
| G07-E004 | engine_crash (non-zero exit or signal, no DONE marker) |
| G07-W001 | no_tests_collected |
| G07-W002 | test_skipped |
| G07-W010 | untested_engine_version |

Run-level errors:

| Code | Meaning |
|---|---|
| G07-R001..R00x | refusals, same as G01 (bad root, filesystem root, no project.godot, output inside project), plus an unsafe tests dir |
| G07-B001 | no engine |
| G07-B002 | not Godot 4 |
| G07-B003 | untested version without opt-in |
| G07-B004 | symlinks present, so native run refused |
| G07-X001 | execution failure |
| G07-X002 | project changed |
| G07-X003 | timeout (process group killed) |

Report `tests[]` (schema field): one entry per test, with these fields:
- `id`;
- `result` (pass, fail, skipped or error);
- `message`, clipped and redacted;
- `duration_ms`.

Also report the exact command (paths redacted), the engine version and binary sha256, and the totals.

`verified=true` only when all of the following hold:
- the run completed (DONE marker);
- the engine version is a tested one (`4.5.1`);
- the hash audit found no change;
- at least one test was collected (`not_tested`, `blocked` and `error` are never verified).

## Safety invariants (must have tests)

- Python stdlib only, `-I`, with no shell. The engine is started from an argument list in a new process group, with a timeout.
- Disposable copy without `.godot/` and `.git/`, plus an isolated HOME and XDG. The original tree is hashed before and after each run, and any difference gives `error` (G07-X002).
- Project files are untrusted data. Test output is clipped and redacted, and no home or project path may appear in the report or logs.
- `--report` and `--evidence-dir` outside the root (enforced).

## Fixtures (synthetic only, under `tests/fixtures/godot/test_runner/`)

| Fixture | Content | Expected result |
|---|---|---|
| `passing` | 2 files, 3 passing tests | pass |
| `failing` | 1 pass, 1 fail with a message | fail, E002 |
| `skipped` | 1 pass, 1 `SKIP:` | warn, W002, never counted as passed |
| `parse_error` | a test file with a syntax error | fail, E001 |
| `runtime_error` | a test with a null method call; the next test still runs | E003 |
| `crash_or_hang` | a test that loops forever, run with a short timeout | error, X003 |
| `empty` | no tests | not_tested, W001 |
| `unsafe` | `--tests-dir res://../x`, a symlinked tests dir | refused or B004 |

## Acceptance

1. Unit tests use a fake engine, as in G01, for every engine path:
   - tested and untested versions, with and without opt-in;
   - Godot 3 or garbage version, crash, missing DONE, timeout;
   - an engine that writes into the workspace;
   - all refusals.
2. Real-engine tests are opt-in (`GODOT_BIN=...`) and cover `passing` and `failing`. They pass on Godot 4.5.1 (official Linux build).
3. `python3 -m unittest discover -s tests` and `python3 scripts/verify_docs.py` pass. The G01 tests are unchanged and still pass.
4. `SKILL.md` follows the Agent Skills frontmatter and carries `metadata.status: implemented_unverified`. The manifest and catalog are updated as for G01.
5. `docs/evidence/G07-test-runner-evidence.md` contains the commands run, the results, the CLI matrix and the hash audit. Anything not run is written as NOT TESTED.
