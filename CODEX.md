# CODEX.md — Codex CLI entry point

Use `AGENTS.md` and `docs/AGENT_WORKFLOW.md`. Codex may implement isolated tasks but must not alter a shared/global Codex configuration, existing Arcanvil Atelier processes, or unrelated VPS services.

Start with read-only repository inspection. Isolate task branches/worktrees and run only approved commands. Return precise diffs, test evidence, and remaining risks. Ask for a review before merging into the release branch.

## Quota-efficient implementation contract

Follow [`docs/QUOTA_AND_QUALITY.md`](docs/QUOTA_AND_QUALITY.md). For assigned issues, Codex is the default implementation and test executor. Start with an atomic issue and targeted file discovery; avoid reading or reprinting the entire repository. Work on a dedicated branch/worktree, keep API contracts unchanged unless approved, run local deterministic checks then real engine integration tests on expendable fixtures, and preserve full logs locally. Hand off a concise diff summary, exact commands, statuses, evidence paths, outstanding risks and PR link to Claude for focused review. Do not call Claude for every trivial edit or repeat expensive agent loops without new evidence. If quotas or environments block progress, checkpoint and mark NOT_TESTED/BLOCKED; never claim passing results without proof.
