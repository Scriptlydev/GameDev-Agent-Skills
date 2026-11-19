# Risk register

| Risk | Likelihood | Impact | Mitigation / owner |
|---|---|---|---|
| Godot 4.5.1 vs Godot AI 4.7+ mismatch | High | High | Separate CLI track; pin and test editor MCP later |
| Unity not installed or licensed in test environment | Medium | High | Make Unity integration milestone conditional; no fake testing |
| Unsafe arbitrary Python via Blender | Medium | Critical | No exposed remote addon, allowlist and disposable scenes |
| Inadequate rollback on modified assets | High | Critical | Snapshot/hash approach and restore tests before any write-enabled skill |
| Third-party license mismatch | Medium | High | Link externally, audit vendoring and bundled assets |
| Overly broad 30-skill scope | High | High | Start with one tested vertical; release in small groups |
| Agents conflict on shared files | Medium | Medium | One branch/owner per task and shared contract freeze |
| AI-hallucinated test success | Medium | High | Native commands + logs + verified flag, separate reviewer |
| Public disclosure of private game files | Medium | Critical | Synthetic fixtures, secret scans, no external content uploads |
| Chasing a temporary subscription promotion | High | Medium | Build enduring OSS utility; don't assume funding approval |
| Burnout/maintenance burden | Medium | High | Narrow supported matrix, issue templates, triage rota |

Statuses and estimates should be updated from observed project evidence, not just intuition.
