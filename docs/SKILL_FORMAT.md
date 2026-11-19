# Agent Skills format rules

Canonical specification: https://agentskills.io/specification (checked 2026-11-19).

## Mandatory structure

Each *implemented* skill lives in a directory matching its lowercase hyphenated name, containing a `SKILL.md` beginning with YAML frontmatter. Required fields: `name` (<=64 characters, lowercase alphanumeric/hyphen, equal to directory name) and nonempty `description` (<=1024 characters). Optional: `license`, `compatibility`, `metadata`, and experimental `allowed-tools`.

Example shown in `templates/SKILL_TEMPLATE.md`. **Do not put placeholder-only skills under `skills/` and promote them as working.** Each actual skill may add `scripts/`, `references/`, and `assets/`.

## Good skill instructions

- State the exact trigger and exclusions (when *not* to run).
- Check tool availability, editor version, user authorization and project root.
- Provide a deterministic sequence: inspect → plan → verify → propose fix → approve → apply → test → report.
- Prefer read-only. Require manual approval for modifications.
- Clearly distinguish static lint from real-engine validation.
- Include example inputs, expected outputs, failure modes and rollback.
- Reference scripts using paths relative to skill root, not arbitrary absolute paths.
- Keep instructions small, and load extended reference material only when needed.

## Validation

Run `skills-ref validate <skill-directory>` with the official reference validator when available, plus project-specific validation for report schema, tests and security controls. A valid frontmatter does **not** prove functional correctness.

## Integration

Do not hardcode MCP tool names unless pinned to tested version; use capability discovery or provide an explicit unsupported error. `allowed-tools` is experimental and cannot be the sole security boundary.
