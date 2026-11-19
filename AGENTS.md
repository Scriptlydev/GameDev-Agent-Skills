# AGENTS.md — mandatory repository instructions

Applies to Claude Code, Codex, and any automation working on this repository.

## Read order

Read `STATE.md`, `DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/QUALITY_GATE.md`, and the specific `docs/skills/<id>-<name>.md` before modifying anything. Follow `docs/AGENT_WORKFLOW.md`.

## Truthfulness

- Never claim an integration, skill, test, release, or adoption metric is functional unless independently executed and captured in evidence.
- Documentation is a **proposal**, not proof of implementation. Update `STATE.md` and the verification matrix only after real tests.
- Never invent benchmarks, versions, screenshots, contributors, or usage figures.

## Safety first

- Work only in the explicitly authorized repository and disposable test fixtures.
- Prefer read-only operations. Print a proposed file change/diff and obtain user approval for high-risk actions.
- Never use destructive commands on existing user projects; no `git reset --hard`, force push, broad `rm -rf`, or silent overwrites.
- Stage work in branches/worktrees. Treat untracked files as valuable; `git restore` alone does not restore them.
- No unrestricted shell, arbitrary Blender Python, or remote editor execution from untrusted prompts or sample projects.
- Never expose API tokens, personal data, model prompts from private projects, or private GitHub repos.
- Do not change unrelated tools/services on a shared server; isolate Codex, Godot and Blender processes, ports, config, and workspaces.

## Engineering expectations

- Each skill complies with `https://agentskills.io/specification` and has precise triggers, inputs, assumptions, error handling, and verification instructions.
- Pin third-party package versions where feasible; do not copy third-party code without recording license and attribution.
- A passing static check never substitutes for a successful real-editor test.
- Every bugfix requires a regression test. For changed behavior, update relevant docs and evidence.
- English is the main public-facing language. French pilot documentation may be maintained in parallel.
- Do not advertise a skill as stable without approval under `docs/QUALITY_GATE.md`.

## Closing a task

Record files changed, commands run, test outcomes, untested assumptions, risks, and next steps in `docs/JOURNAL.md`; update `STATE.md` and `docs/HANDOFF.md`; create/update a PR. Never self-approve or self-merge an unreviewed high-risk change.

## Efficient collaboration, unchanged quality standard

All agents must follow [`docs/QUOTA_AND_QUALITY.md`](docs/QUOTA_AND_QUALITY.md): default Claude coordination / targeted review, Codex bulk implementation / tests, and deterministic local + CI verification. Do not duplicate unsplit work or share full chat transcripts. These are cost controls only; `docs/QUALITY_GATE.md`, human approval for risky operations and truthful test reporting always take precedence.
