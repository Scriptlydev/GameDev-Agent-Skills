# Multi-agent work protocol

## Roles

- **Coordinator / maintainer:** prioritize and approve scope; review evidence; decide publication. This is a human-governed role.
- **Claude Code implementation agent:** writes small, isolated modules and integration scripts.
- **Codex review / implementation agent:** tests independently, reviews logic and adds regressions on another branch.
- **Optional Gemini reviewer:** checks docs, tests and edge-case reasoning without receiving secrets/private content.
- **Release reviewer:** verifies licenses, security and native-editor evidence before merge.

## Work partitioning

- One issue per skill feature or atomic capability, maximum one primary owning agent.
- Separate branches: `feat/G01-scene-doctor-readonly`, `test/G01-broken-fixtures`, `docs/adapter-compatibility`.
- Limit concurrent agents to **independent files**. Merge contracts/interfaces before parallel modules; otherwise integration chaos dominates.
- Use a queue and branch/PR lock for shared adapters and report schemas.
- Prefer a shared GitHub issue + handoff to cross-chat communication; agents do not share memory by default.

## Task lifecycle

`SPEC → ASSIGNED → IN_PROGRESS → PR_OPEN → REVIEWED → VERIFIED → MERGED → RELEASED`.

A coordinator may not label `VERIFIED` without an actual test report and version data. Agents must not merge their own high-risk work without an independent review.

## Standard issue contract

- Goal and explicit non-goals
- In-scope files and protected paths
- Engine version and test fixture
- Expected schema/output
- Approvals required
- Acceptance tests and failure cases
- Rollback and release considerations

## Cost and quota controls

Use bounded tasks, narrow context, repo file searches before full-file reads, deterministic unit tests before LLM reviews and no repeated long agent loops without new evidence. Existing free/paid quotas are not unlimited; monitor and log costs only when actually measurable.
