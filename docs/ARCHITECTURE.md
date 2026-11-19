# System Architecture — proposed

## High-level architecture

```text
                        Claude Code / Codex / compatible agents
                                        |
                              Agent Skills SKILL.md
                                        |
                 +----------------------+----------------------+
                 |                      |                      |
          Workflow policy        Evidence/reporting       Safety gate
                 |                      |                      |
                 +----------------------+----------------------+
                                        |
                               Adapter abstraction
                        +---------------+---------------+
                        |               |               |
                  Godot adapter     Unity adapter    Blender adapter
                        |               |               |
                 Headless CLI /      Unity Editor      bpy / MCP addon
                 verified MCP        + Unity MCP      + Blender MCP
                        |               |               |
                   Fixture game      Fixture game      Fixture .blend
```

## Repository layout (target, not yet populated)

```text
gamedev-agent-skills/
  README.md / README.fr.md / AGENTS.md / CLAUDE.md / CODEX.md
  LICENSE / THIRD_PARTY_NOTICES.md
  docs/ (PRD, architecture, 30 specs, operations, quality evidence)
  skills/ (created only when each SKILL.md is actually implemented)
    godot/scene-doctor/SKILL.md
    unity/scene-analyzer/SKILL.md
    blender/mesh-doctor/SKILL.md
    universal/project-architect/SKILL.md
  packages/ (future reusable core and adapters)
  tests/fixtures/ (future miniature synthetic projects)
  tests/integration/ (future real editor checks)
  reports/ (generated locally; gitignored)
  .github/ (issue/PR templates and future CI)
```

## Contracts

Each skill is a workflow orchestrator, not a replacement for native tool APIs. It must define:

1. `detect` — identify engine, version, project root and capabilities; refuse unknown setups safely.
2. `plan` — state affected files and command/tool actions; `dry-run` before edits.
3. `inspect` — read and collect evidence; report errors with stable codes and locations.
4. `change` — optional, only after explicit approval and protected snapshot.
5. `verify` — validate output using native engine + fixtures, not text-only speculation.
6. `report` — JSON schema + concise Markdown summary and exact tested versions.
7. `rollback` — restore pre-change state, including untracked files, or explain blockages without silently overwriting unrelated changes.

## Integration priorities

### Godot track A — required for first milestone

Use the installed **Godot 4.5.1** executable through a subprocess on a disposable test project to support read-only validation. Preferred engine invocation (adapt exact flags after version help): `godot --headless --path <fixture> --editor --quit` for import/parser checks; direct `.tscn`/`.tres` analysis is an additional independent check. The project root is a strict allowlisted directory. Do not treat editor import cache writes as strict read-only: copy the fixture to a temporary workspace before launching Godot.

### Godot track B — future

Use a version-pinned `hi-godot/godot-ai` integration on **Godot 4.7+** only. Verify its connection and schema on the tested release. Do not alter a 4.5.1 installation in place.

### Unity

Use Unity's own CLI/Test Framework for tests, and optionally `CoplayDev/unity-mcp` for editor operations. Validate engine executable, project version, licensing/activation, package list and Unity Test Framework presence. Work on fixture copies; Unity import processes mutate project metadata/cache.

### Blender

Use Python `bpy` in isolated headless execution for reproducible inspections/exports. Optionally connect an approved version of `ahujasid/mcp-for-blender` for interactive tasks. **Never expose unauthenticated remote sockets**; arbitrary Python execution is high-risk. Test output on generated fixture files, not the owner's commercial asset library.

## Evidence format

Canonical report object proposal (full schema in `docs/REPORT_SCHEMA.md`): `schema_version`, `run_id`, `skill_id`, `status`, `verified`, `engine`, `engine_version`, `project_root_redacted`, `started_at`, `completed_at`, `input_hashes`, `findings[]`, `actions[]`, `tests[]`, `artifacts[]`, `rollback`, `errors[]`.

Statuses: `pass`, `warn`, `fail`, `blocked`, `error`, `not_tested`. `verified=true` is allowed only if the required native execution completed successfully and evidence paths exist.

## Trust boundaries

- Skill text and repository source are untrusted inputs to the agent until inspected.
- Editor MCP integrations may allow broad reads/writes/execution; grant minimal scope and consent.
- Forked libraries stay outside our source tree unless vendoring is approved and legally reviewed.
- Agent-generated input must never become an unrestricted shell fragment.
- Privileged write approvals occur outside the skill's own untrusted instructions.

## Future extensibility

Use adapters with capability negotiation, not hardcoded assumption of a common MCP namespace. Add Unreal only after evidence-based demand and adapter ownership are resolved. Each engine adapter can fail closed and skip incompatible tasks without breaking the rest of the suite.
