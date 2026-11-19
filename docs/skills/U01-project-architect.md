# U01 — project-architect

**Collection:** Universal | **Priority:** P1 | **Status:** SPECIFIED — NOT IMPLEMENTED

## Purpose and trigger

Map project structure and propose a bounded task plan. Activate this skill when a user requests this exact category of work; otherwise do not run it by default.

## Preconditions and inputs

- Authorized project/fixture root and explicit task scope.
- Identified editor and compatible version: **Local filesystem, Git and optional native runners**.
- Relevant input paths, user preferences or thresholds, optional read-only report directory.
- For write-capable modes, a proposed diff, secure snapshot and explicit approval.

## Planned workflow

1. Confirm project root, paths, version and supported capabilities. Refuse unsupported combinations rather than guessing.
2. Perform a read-only preflight. Inspect folders, manifests and declared dependencies; summarize entry points, build paths and explicit unknowns.
3. Generate stable diagnostic codes, file/object locations, severity and evidence.
4. Summarize suggested fixes without applying them by default.
5. If the feature explicitly supports modifications and user approves, snapshot and use smallest atomic patch. Otherwise remain read-only.
6. Run native verification on a copy/scratch workspace where applicable, recording commands, versions, exit codes and logs.
7. Produce the standard structured JSON report and concise human summary, or `blocked/not_tested` if execution was unavailable.

## Expected outputs

- `report.json` matching [`../REPORT_SCHEMA.md`](../REPORT_SCHEMA.md), with `skill_id: "U01"` and honest `verified` state.
- Findings for cases such as: **Missing owner, broken path, incompatible project layout**.
- If applicable, separate patch preview / artifact manifest / rollback receipt.

## Acceptance tests (must be implemented and run)

| Case | Test fixture and expected result |
|---|---|
| Success | Synthetic 2-engine repo yields correct map and no writes. Record actual tool and version. |
| Expected failure | Unknown engine returns limited analysis without guessing. Diagnostic must identify the problem. |
| Missing runtime | No editor/tool available: report `blocked` and `verified=false`. |
| Non-destructive | Hash and list original fixture before/after; no lost or overwritten tracked/untracked data. |
| Adversarial | Untrusted input, illegal path or malformed data triggers safe refusal. |

## Safety / caveats

Do not read hidden secret material or execute install scripts. Follow [`../SECURITY_MODEL.md`](../SECURITY_MODEL.md). Do not mark this skill as working until tested in the actual supported environment.

## Definition of done

- Valid `SKILL.md` with instructions and scripts actually present (not simply this spec).
- At least one passing positive and one passing negative native test where applicable.
- Structured report validated; exact engine/OS versions recorded.
- Unit, error and safety regression tests; README example; versioned evidence.
- Approved PR with status advanced from `SPECIFIED` to `ALPHA VERIFIED` only after independent evidence.
