# Security Policy

**Current status:** planning documentation; there is no released executable integration yet.

## Reporting vulnerabilities

Please **do not** post secrets, private project files, exploit scripts, or unpublished vulnerabilities in public GitHub issues. Once the public repository is live, use its private GitHub Security Advisories reporting feature if enabled. Otherwise contact the maintainer through a verified private channel announced in the repository (not yet configured).

Provide affected version/commit, minimal synthetic reproduction, expected/actual behavior and potential impact. Do not attach copyrighted proprietary game assets.

## Supported versions

No software versions are supported yet. `docs/COMPATIBILITY.md` shows potential future targets and the verification state.

## Security defaults planned

Read-only checks first, path allowlists, explicit approvals for edits, pinned dependencies, quarantined fixture tests and verified restore. Never expose a Blender arbitrary-Python MCP socket on the public internet.
