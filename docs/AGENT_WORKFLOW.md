# Multi-agent work protocol

## Roles

- **Coordinator / maintainer:** prioritize and approve scope; review evidence; decide publication. This is a human-governed role.
- **Claude Code coordinator / reviewer:** clarifies architecture, acceptance contracts, risky decisions and targeted reviews; implements when Codex is blocked or a specialized task requires it.
- **Codex implementation / test agent:** performs the bulk of scoped coding, regression fixtures and deterministic test reproduction on isolated branches.
- **Model routing:** choose the least costly available agent that can satisfy all quality gates; escalate for evidenced complexity, never skip tests to save quotas.
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

Follow [the quota/quality operating procedure](QUOTA_AND_QUALITY.md) for model routing, task packets, staged reading, evidence handoff, deterministic tests, targeted review and escalation.

- Default to **Claude planning/review + Codex implementation/tests** for meaningful changes, but skip the second agent for truly trivial tasks.
- Keep quality gates, real engine verification and safe rollback unchanged even when quotas are exhausted.
- One task owner; separate worktrees; share concise PR diffs and evidence paths instead of full conversations.
- Abort repeated attempts without new diagnostic evidence; checkpoint work rather than continuing token-heavy loops.
- Log costs only if measurable and never assume subscription quota/pricing.
