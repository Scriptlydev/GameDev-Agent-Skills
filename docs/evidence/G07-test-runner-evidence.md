# G07 test-runner v0.1 implementation evidence

Implementation session: 2026-11-19, Linux, Python standard library only.
Status: **IMPLEMENTED / UNVERIFIED**, native check run by the reviewer on Godot
4.5.1 (Linux, synthetic fixtures; see "Native check" below). Fake engines
exercise Python control flow; they are not evidence of native compatibility on their own. No network,
dependency install, commit, push or merge was performed.

## Executed checks

- `python3 -m unittest discover -s tests -p test_test_runner.py`: 25 tests,
  OK, 2 native tests skipped (first successful targeted run). An earlier run
  failed the output-flood test; separating stdout/stderr capture fixed it.
- `timeout 180 bash -c 'python3 -m unittest discover -s tests && python3 scripts/verify_docs.py'`:
  exit **0**; **69 tests in 22.965s, OK (skipped=4)**. The four skips are
  the two G01 and two G07 opt-in native tests. Documentation validation:
  **PASS**, no skill marked verified or stable. This final suite includes the
  additional empty/NUL-root checks and empty-report-path regression.
- `git diff --check`: exit **0**. Protected G01, state, journal, handoff,
  decisions, agent instructions and CI paths: `git diff --quiet -- <protected paths>`
  exit **0**, unchanged.
- No `godot4` or `godot` found on PATH; `GODOT_BIN` unset.
- Godot 4.5.1: NOT TESTED in the implementation session; run by the reviewer afterwards (next section).
- Windows/macOS, GUT, gdUnit4, C#, other engine versions: **NOT TESTED**.
- External Agent Skills validator and native GDScript parsing: **NOT TESTED**.

## Native check on Godot 4.5.1 (reviewer, 2026-11-19)

Engine: official `4.5.1.stable.official.f62fdbde1`, binary sha256
`db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199` (same build as G01).

`GODOT_BIN=<godot-4.5.1> python3 -m unittest tests.test_test_runner -v` -> 26 tests OK,
including both RealGodotTests (about 48 s).

`python3 -I skills/godot/test-runner/scripts/test_runner.py run <fixture> --godot <godot-4.5.1> --report <scratch>/r.json --evidence-dir <scratch>/logs`
(`--timeout 20` for crash_or_hang):

| Fixture | Exit | status | verified | pass/fail/skip/error | Codes |
|---|---|---|---|---|---|
| passing | 0 | pass | true | 3/0/0/0 | — |
| failing | 1 | fail | true | 1/1/0/0 | E002 |
| skipped | 0 | warn | true | 1/0/1/0 | W002 |
| parse_error | 1 | fail | true | 0/0/0/0 | E001 |
| runtime_error | 1 | fail | true | 1/0/0/1 | E003 |
| crash_or_hang | 4 | error | false | 0/0/0/0 | X003 (group killed) |
| empty | 3 | not_tested | false | 0/0/0/0 | W001 |
| unsafe, `--tests-dir res://../x` | 2 | blocked | false | — | R005 |
| unsafe copy with symlinked `tests/` | 2 | blocked | false | — | R005 |

The first native pass reported `verified=true` for `empty`; the reviewer changed
the rule so that `not_tested`, `blocked` and `error` are never verified, and the
matrix test now asserts it. The sha256 of every G07 fixture file was identical
before and after these runs, and a grep of reports and logs found no home or
project path. Refusals print the report on stdout without writing `--report`,
as G01 does.

## CLI matrix (fake engine, subprocess CLI with Python `-I`)

All CLI checks invoke `run <fixture> --godot <fake-engine> --report <outside>/report.json
--evidence-dir <outside>/logs`, plus the indicated flags. Private paths are
intentionally omitted; subprocess assertions check actual reports and log hashes.

| Scenario | Observed expectation asserted by tests |
|---|---|
| passing | exit 0, pass, 3 passed across 2 files, DONE, verified flag true under simulated 4.5.1 |
| failing | exit 1, fail, 1 pass / 1 fail, E002, completed and verified under simulation |
| skipped | exit 0, warn, 1 pass / 1 skip, W002 |
| parse_error | exit 1, fail, E001, zero passed |
| runtime_error | exit 1, fail, E003, next test passes; both missing-END and present-END runtime cases |
| crash_or_hang, timeout 0.2 | exit 4, X003; group killed, unverified |
| empty or unmatched filter | exit 3, not_tested, W001 |
| unsafe tests directory (traversal, URL, absolute, symlink, backslash) | exit 2, R005; no native execution |
| other project symlinks, including excluded directories | exit 3, B004 |
| missing / non-executable binary | exit 3, B001 |
| Godot 3, garbage version or failing version probe | exit 3, B002 |
| simulated 4.7.2 without opt-in | exit 3, B003, unverified |
| simulated 4.7.2 with --allow-untested-engine | exit 0, warn, W010, unverified |
| crash, signal or missing DONE | exit 1, E004, unverified |
| incomplete test without SCRIPT ERROR | E004, never invent a test result |
| import crash | fail, E001 |
| version or import timeout | exit 4, X003 |
| invalid executable or malformed protocol | exit 4, X001 |
| workspace writes | pass; original unchanged, including untracked files and caches |
| original changed (in-process injected concurrent writer) | error, X002, unverified |
| invalid root / filesystem root / absent or linked project.godot | exit 2, R001/R002/R003 |
| output inside root or through symlink alias; empty report path | exit 2, R004 |
| symlinked evidence file pointing into original | exit 4, X001, no original write |
| invalid timeout, including nan/inf | exit 2, R006 |
| custom directory and substring filter | exact expected selected ids and totals |
| non-string return | fail, E002, message `non-string return` |
| large stdout, private paths and synthetic credentials | valid protocol; clipped/redacted logs and messages |

## Hash audit and evidence

Synthetic originals are hashed before/after native execution attempts; reports
include file counts, relative changed paths and SHA-256 input hashes. Tests
independently compare the entire original fixture snapshot around a simulated
engine that writes its workspace. Tracked-like, untracked and `.git`/`.godot`
content is preserved. Every saved log checksum is independently recomputed in
the tests. A separately injected writer proves that a real original change
forces X002 and clears `verified`; the modification is not silently restored.
No native Godot hash-audit claim is made in this session.

## Reviewer commands and limits

```sh
python3 -m unittest discover -s tests
python3 scripts/verify_docs.py
GODOT_BIN=<godot-4.5.1> python3 -m unittest discover -s tests -p test_test_runner.py
```

The two opt-in RealGodotTests assert passing/failing native fixtures, exact
totals, verified gating and unchanged originals. The other native fixtures
were run by the reviewer as listed above. Fake stubs do not parse GDScript.

The copy/profile are not an OS security boundary against authorized test code
that deliberately accesses external resources. Audit detects rather than
prevents concurrent or malicious original writes. Output capture uses temporary
files (at most 2 MiB per stream read into memory); disk output is bounded by run
time, not by a byte quota. Logs retain at most 65,536 characters, and truncated
protocol cannot establish success. Redaction handles known paths and common
credential patterns, not arbitrary secrets. Native review remains required.
Protected state/journal/handoff and G01 files were left unchanged as instructed;
PR creation and release approval are delegated to devhub/reviewer.
