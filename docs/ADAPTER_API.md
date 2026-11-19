# Adapter API — technical contract proposal

Adapters are local wrappers around native tools. This is a **design contract**; none of these interfaces are implemented in the documentation package.

## Core typed interfaces (pseudocode)

```python
class EngineAdapter(Protocol):
    def detect(self, root: Path) -> EngineInfo: ...
    def capabilities(self) -> set[str]: ...
    def inspect(self, request: InspectionRequest) -> InspectionResult: ...
    def run_native_check(self, request: CheckRequest) -> CheckResult: ...

class WriteAdapter(EngineAdapter, Protocol):
    def preview(self, request: ChangeRequest) -> DiffPlan: ...
    def apply_approved(self, request: ApprovedChange) -> ChangeReceipt: ...
    def restore(self, receipt: ChangeReceipt) -> RestoreResult: ...
```

Every adapter must validate root and input paths against an allowlist **before** starting an engine. The engine's own plugins and test runners are not a privilege boundary; isolate them in a disposable workspace.

## Error taxonomy

| Code | Meaning | Required action |
|---|---|---|
| `RUNTIME_NOT_FOUND` | Engine executable unavailable | Status blocked, verified=false |
| `UNSUPPORTED_VERSION` | Known version outside declared matrix | Fail closed, suggest tested path |
| `PATH_DENIED` | Outside root / traversal / symlink escape | Refuse and log sanitized path |
| `INVALID_INPUT` | Corrupt or malformed fixture | Emit structured error |
| `TIMEOUT` | Operation exceeded configured bound | Terminate child process safely |
| `APPROVAL_REQUIRED` | Write requested without approval | No changes; return plan |
| `SNAPSHOT_FAILED` | Snapshot is incomplete | Refuse write |
| `CONCURRENT_MODIFICATION` | File hashes changed while task ran | Refuse restore/apply without human resolution |
| `NATIVE_VALIDATION_FAILED` | Native editor rejected result | Report fail and offer safe restore |
| `ROLLBACK_FAILED` | Recovery incomplete or conflicting | Stop, preserve state, request human intervention |

## Report and logs

Each adapter returns errors and artifacts in the common schema. Redact absolute paths/usernames from exported reports, keep local debug logs private. A missing editor is not a successful integration test.

## Capability negotiation

Potential capabilities: `static-read`, `native-parse`, `runtime-test`, `editor-tree`, `asset-import`, `render-preview`, `safe-write`, `rollback`. A skill declares the capabilities it requires; adapters expose only those validated on the current version.

## Version pinning

For MCP adapters record exact package version/commit. Discovery of tool names must be done against the pinned version; avoid assuming any future upstream API remains identical.
