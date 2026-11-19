# Claude Code + Codex: quota-efficient, quality-preserving workflow

**Status:** mandatory working agreement for automated contributors. Applies together with `AGENTS.md`, `docs/AGENT_WORKFLOW.md`, `docs/QUALITY_GATE.md`, and per-skill specifications.

## Principle

**Save tokens on repeated reading, redundant drafting, unnecessary agents and failed loops; never save tokens by skipping validation, security reviews or native engine tests.** Model subscriptions and rate limits vary: do not assume a model, quota, context capacity, or pricing level. Do not silently switch paid tiers or add services.

## Ownership and cost-aware routing

| Work item | Default primary owner | Other agent's role | Required independent evidence |
|---|---|---|---|
| Define acceptance criteria and public API contract | Claude Code (short, scoped planning) | Codex reviews feasibility | Written interface + fixtures/tests planned |
| Bulk implementation, CLI/Python scripts, unit tests and fixtures | Codex | Claude reviews *diff and results*, not all source again | Local automated tests + GitHub CI |
| Architecture/security decisions and dependency changes | Claude Code + maintainer | Codex explores options/validates testability | Decision note + targeted security review |
| Mechanical refactors, formatting and deterministic code changes | Codex + local tools | Claude only if behaviour changes | Formatter/linter + regression tests |
| CI failures and regression reproduction | Codex | Claude escalated only after a concise diagnosis | Commands, exit code, minimal log excerpt |
| README/examples and publishing notes | Lowest-cost suitable agent or local tooling | Claude final targeted edit if necessary | Documentation checks + replayed examples |
| High-risk writes, rollback, external execution or secrets | Human approval first | Claude reviews plan; Codex implements in isolated fixture | Security gate and verified recovery |

These are defaults, not exclusive assignments. If Codex is blocked or unavailable, Claude may implement; if the task is trivial, do not create multiple agents. One owner per issue and file scope. Never launch two agents to solve the *same* unsplit task.

## Task packet (issue -> agent)

Before invoking any agent, provide only:
- One GitHub issue link/ID, branch and exact deliverable; what is explicitly **out of scope**.
- Paths and versioned contracts to read; **do not paste the entire repository**.
- Allowed file paths, target editor version, test fixture and commands.
- Acceptance criteria including negative/adversarial test, and required safety/rollback checks.
- Maximum one concise handoff artifact per stage.

If the interface/schema is ambiguous, settle it before concurrent coding. Do not distribute overlapping edits to `STATE.md`, shared schema, central adapters, or lock files in parallel. Use separate worktrees, isolate local environments, and avoid touching unrelated services.

## Context budget: progressive disclosure

1. Start with `git status --short`, current issue, and `STATE.md` / `docs/HANDOFF.md` summaries.
2. Inspect repo layout / file names, then narrow searches (`rg`, `git grep`, targeted `git diff`). Read only relevant portions of files before widening scope.
3. Reuse stable contracts and previous test evidence where still applicable; re-run necessary tests on changed code. Do not claim stale results are current.
4. Share **a diff, diagnostic summary and evidence paths**, not complete file copies, giant terminal dumps or transcripts.
5. Store task decisions in the issue/PR and concise handoff so a new session does not need prior chat history. Protect private and commercial project information.

Never truncate evidence in the repository: keep full local logs/artifacts where appropriate, and show only the useful excerpt plus a pointer in agent messages. Redact tokens, personal paths and secrets.

## Cheap deterministic checks before expensive model cycles

Use, in order where applicable:
1. Schema/format checks and offline lint/format tools.
2. Small unit tests on synthetic fixtures.
3. Targeted regression tests for the changed module.
4. Native Godot/Unity/Blender integration on isolated fixture copies.
5. Full CI or broader compatibility matrix at release gates or when an affected component warrants it.
6. Independent review of the actual diff, with greater depth for dangerous changes.

Static tests are **not** equivalent to editor tests. A missing editor must be reported as `NOT_TESTED` or `BLOCKED`, never silently bypassed.

## Review strategy (no duplicate implementation)

- Codex outputs: changed paths, concise diff summary, tests run with commands/status, open risks, evidence paths, PR URL.
- Claude reviews only the changed code and affected contracts first; expand scope on red flags. Review invariants, security, tests, regression coverage, cross-platform/engine behaviour and licensing.
- Claude produces actionable findings with file/line and severity; no broad rewrite unless required. Codex fixes; tests rerun; Claude performs *one focused re-review*.
- If a second attempt repeats the same failure without new evidence, stop, record a blocker and escalate to the human maintainer rather than burning quota.

## Escalate to deeper reasoning when it earns its cost

Use a more capable model / longer reasoning **only** for novel architecture decisions, elusive reproducible bugs, security risks, invalid rollback, API compatibility, and complex concurrency. For straightforward scaffolding, tests, docs and mechanical changes use the least expensive available agent/model that reliably passes the quality gate. Escalate based on failure evidence, not preference or arbitrary turn counts.

Do not lower acceptance criteria because quotas are low. Pause the task, make an exact checkpoint and resume later if needed.

## Completion and quality gate

A task is done only when:
- The requested behaviour is implemented and the contract is met.
- Positive, negative and adversarial cases are tested; failures and skips are recorded.
- No unauthorized writes, unexpected changed files, leaked secrets, or license violations.
- Native engine checks run for every claimed compatibility target.
- A reviewer can understand the diff, reproduce evidence and revert safely.
- `STATE.md`, `docs/JOURNAL.md`, `docs/HANDOFF.md` and PR notes reflect actual state.

**Quality is measured by reproduced outcomes, not token spend, number of agents or amount of code.**

## Example task execution

1. Claude defines G01 `scene-doctor` read-only CLI contract in one short GitHub issue.
2. Codex implements the CLI, fixtures and unit tests on its isolated branch/worktree.
3. Local checks + Godot 4.5.1 headless test on expendable fixture copy; keep original hashes.
4. Codex opens PR with diffs, test proof, limitations and `NOT_TESTED` items.
5. Claude reviews the PR's changed files and test results; Codex addresses findings.
6. Maintainer decides merge after required GitHub checks pass.

**Privacy:** The public repo must not reference private repo names, private instructions, personal subscription details, budgets or machine addresses; publish only generic agent workflow and public reproducible evidence.
