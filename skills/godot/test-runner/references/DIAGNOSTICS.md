# G07 diagnostics v0.1

| Code | Meaning | Next step |
|---|---|---|
| G07-E001 | test_script_load_failed | Fix the script parse/build error; inspect import/tests logs. |
| G07-E002 | test_failed | Inspect the returned failure message. |
| G07-E003 | test_runtime_error | Fix the runtime error or failing hook. |
| G07-E004 | engine_crash | Inspect exit/log evidence; nonzero exit or missing DONE. |
| G07-W001 | no_tests_collected | Check directory, naming convention and filter; never a pass. |
| G07-W002 | test_skipped | Review the SKIP reason; excluded from pass totals. |
| G07-W010 | untested_engine_version | Reproduce on 4.5.1; opted-in results remain unverified. |
| G07-R001 | Invalid, absent or non-directory root | Supply an existing authorized directory. |
| G07-R002 | Filesystem root refused | Select a single project. |
| G07-R003 | Missing or symlinked project.godot | Select a regular Godot project. |
| G07-R004 | Unsafe output path | Put report and evidence outside the project. |
| G07-R005 | Unsafe tests directory | Use an in-root res:// directory without traversal or symlinks. |
| G07-R006 | Invalid timeout | Use a finite value greater than 0 and at most 900 seconds. |
| G07-B001 | No engine | Supply --godot or GODOT_BIN, or an installed godot4/godot. |
| G07-B002 | Not Godot 4 or failed version probe | Supply a working Godot 4 executable. |
| G07-B003 | Untested version without opt-in | Use 4.5.1 or explicitly allow an unverified version. |
| G07-B004 | Symlinks present | Use a project copy containing regular files/directories only. |
| G07-X001 | Execution, filesystem or native protocol failure | Inspect local evidence; do not infer success. |
| G07-X002 | Original project changed | Investigate edits; no automatic rollback. |
| G07-X003 | Timeout | Process group killed; inspect hanging test before retrying. |

Errors/refusals are in `errors[]`; E/W codes are in `findings[]`.
An incomplete test with SCRIPT ERROR becomes an error result. A runtime error
followed by END still overrides its apparent return value. A crash or incomplete
protocol without SCRIPT ERROR never invents a passed test.
