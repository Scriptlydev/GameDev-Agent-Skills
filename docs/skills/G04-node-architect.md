# G04 — node-architect

**Collection:** Godot | **Priority:** P2 | **Status:** SPECIFIED — NOT IMPLEMENTED

## Purpose and trigger

Review node hierarchies and suggest maintainable structures. Activate this skill when a user requests this exact category of work; otherwise do not run it by default.

## Preconditions and inputs

- Authorized project/fixture root and explicit task scope.
- Identified editor and compatible version: **Godot 4.5.1 CLI first; Godot 4.7+ MCP later**.
- Relevant input paths, user preferences or thresholds, optional read-only report directory.
- For write-capable modes, a proposed diff, secure snapshot and explicit approval.

## Planned workflow

1. Confirm project root, paths, version and supported capabilities. Refuse unsupported combinations rather than guessing.
2. Perform a read-only preflight. Inspect scene tree, duplicated nodes and scripts; propose changes as patch preview.
3. Generate stable diagnostic codes, file/object locations, severity and evidence.
4. Summarize suggested fixes without applying them by default.
5. If the feature explicitly supports modifications and user approves, snapshot and use smallest atomic patch. Otherwise remain read-only.
6. Run native verification on a copy/scratch workspace where applicable, recording commands, versions, exit codes and logs.
7. Produce the standard structured JSON report and concise human summary, or `blocked/not_tested` if execution was unavailable.

## Expected outputs

- `report.json` matching [`../REPORT_SCHEMA.md`](../REPORT_SCHEMA.md), with `skill_id: "G04"` and honest `verified` state.
- Findings for cases such as: **Unexpected tight coupling, duplicate node path, deep hierarchy**.
- If applicable, separate patch preview / artifact manifest / rollback receipt.

## Acceptance tests (must be implemented and run)

| Case | Test fixture and expected result |
|---|---|
| Success | Fixture tree graph matches engine view. Record actual tool and version. |
| Expected failure | Dangling NodePath reference is highlighted. Diagnostic must identify the problem. |
| Missing runtime | No editor/tool available: report `blocked` and `verified=false`. |
| Non-destructive | Hash and list original fixture before/after; no lost or overwritten tracked/untracked data. |
| Adversarial | Untrusted input, illegal path or malformed data triggers safe refusal. |

## Safety / caveats

Never reorganize target scene automatically. Follow [`../SECURITY_MODEL.md`](../SECURITY_MODEL.md). Do not mark this skill as working until tested in the actual supported environment.

## Definition of done

- Valid `SKILL.md` with instructions and scripts actually present (not simply this spec).
- At least one passing positive and one passing negative native test where applicable.
- Structured report validated; exact engine/OS versions recorded.
- Unit, error and safety regression tests; README example; versioned evidence.
- Approved PR with status advanced from `SPECIFIED` to `ALPHA VERIFIED` only after independent evidence.
