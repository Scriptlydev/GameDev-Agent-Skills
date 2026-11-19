# Y07 — unity-test-runner

**Collection:** Unity | **Priority:** P2 | **Status:** SPECIFIED — NOT IMPLEMENTED

## Purpose and trigger

Execute Unity Edit Mode/Play Mode tests reliably. Activate this skill when a user requests this exact category of work; otherwise do not run it by default.

## Preconditions and inputs

- Authorized project/fixture root and explicit task scope.
- Identified editor and compatible version: **Unity Editor + Test Framework and optional MCP**.
- Relevant input paths, user preferences or thresholds, optional read-only report directory.
- For write-capable modes, a proposed diff, secure snapshot and explicit approval.

## Planned workflow

1. Confirm project root, paths, version and supported capabilities. Refuse unsupported combinations rather than guessing.
2. Perform a read-only preflight. Use Unity Test Framework batch mode; capture XML and exit codes.
3. Generate stable diagnostic codes, file/object locations, severity and evidence.
4. Summarize suggested fixes without applying them by default.
5. If the feature explicitly supports modifications and user approves, snapshot and use smallest atomic patch. Otherwise remain read-only.
6. Run native verification on a copy/scratch workspace where applicable, recording commands, versions, exit codes and logs.
7. Produce the standard structured JSON report and concise human summary, or `blocked/not_tested` if execution was unavailable.

## Expected outputs

- `report.json` matching [`../REPORT_SCHEMA.md`](../REPORT_SCHEMA.md), with `skill_id: "Y07"` and honest `verified` state.
- Findings for cases such as: **Test failure, import crash, unavailable license**.
- If applicable, separate patch preview / artifact manifest / rollback receipt.

## Acceptance tests (must be implemented and run)

| Case | Test fixture and expected result |
|---|---|
| Success | Passing Edit Mode fixture produces parsed XML. Record actual tool and version. |
| Expected failure | Failing assertion yields fail not success. Diagnostic must identify the problem. |
| Missing runtime | No editor/tool available: report `blocked` and `verified=false`. |
| Non-destructive | Hash and list original fixture before/after; no lost or overwritten tracked/untracked data. |
| Adversarial | Untrusted input, illegal path or malformed data triggers safe refusal. |

## Safety / caveats

Bound timeout, licensed local editor and scratch workspace. Follow [`../SECURITY_MODEL.md`](../SECURITY_MODEL.md). Do not mark this skill as working until tested in the actual supported environment.

## Definition of done

- Valid `SKILL.md` with instructions and scripts actually present (not simply this spec).
- At least one passing positive and one passing negative native test where applicable.
- Structured report validated; exact engine/OS versions recorded.
- Unit, error and safety regression tests; README example; versioned evidence.
- Approved PR with status advanced from `SPECIFIED` to `ALPHA VERIFIED` only after independent evidence.
