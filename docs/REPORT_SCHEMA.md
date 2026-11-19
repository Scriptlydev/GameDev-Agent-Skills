# Unified report contract (design specification)

The canonical report is JSON UTF-8, emitted per run; reports should be excluded from public git history when generated from private projects.

## Proposed fields

| Field | Type | Rule |
|---|---|---|
| `schema_version` | string | start at `0.1.0` |
| `run_id` | string | unique local ID, no user identifier embedded |
| `skill_id` | string | catalog ID such as `G01` |
| `status` | enum | `pass`, `warn`, `fail`, `blocked`, `error`, `not_tested` |
| `verified` | boolean | true only after required native evidence exists |
| `engine`, `engine_version` | string/null | actual identified tool and version |
| `project_root_redacted` | string | use a logical alias, avoid publishing personal paths |
| `started_at`, `completed_at` | ISO-8601 string | include timezone |
| `input_hashes` | object | stable relative names to SHA-256 hashes |
| `findings[]` | object array | `code`, `severity`, `summary`, `file`, `line`, `evidence` |
| `actions[]` | object array | command/tool, intent, approved?, changed files |
| `tests[]` | object array | command, expected, observed, pass/fail/skipped, evidence |
| `artifacts[]` | object array | relative path, purpose, checksum, privacy |
| `rollback` | object | available? snapshot ref, verified? |
| `errors[]` | object array | code, message, retryable? |

## Example: documentation-only sample (NOT a test result)

```json
{
  "schema_version": "0.1.0",
  "run_id": "example-only-001",
  "skill_id": "G01",
  "status": "not_tested",
  "verified": false,
  "engine": "godot",
  "engine_version": null,
  "project_root_redacted": "<fixture>",
  "started_at": "2026-11-19T00:00:00+01:00",
  "completed_at": "2026-11-19T00:00:00+01:00",
  "input_hashes": {},
  "findings": [],
  "actions": [],
  "tests": [],
  "artifacts": [],
  "rollback": {"available": false, "verified": false},
  "errors": []
}
```

## Design constraints

1. Never label output `verified` because an agent merely asserts that it ran a test.
2. Do not log credentials, raw chat transcripts, absolute private paths or proprietary source by default.
3. Give findings stable codes and non-destructive repair guidance.
4. Keep machine reports backwards compatible or bump schema version.
5. Emit valid JSON even for failures when possible; process exit code still reflects failure.
