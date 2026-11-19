# Security model & threat assessment

## Protected assets

Source code, scenes, original game assets, credentials, Git history, machine resources, personal data and paid tool quotas.

## Threat scenarios and mitigations

| Threat | Mitigation | Test |
|---|---|---|
| Path traversal / access outside project | canonical paths, symlink-aware allowlist, no direct relative concatenation | Try `../`, symlinks, absolute paths |
| Destructive tool execution | deny by default; explicit approval; action allowlist | Deny scenario produces zero writes |
| Prompt injection from game assets/docs | treat content as untrusted; no execution based solely on embedded strings | Malicious fixture with instructions |
| Arbitrary Blender Python | prohibit by default; restricted local adapter and approved commands | Attempted unapproved code is blocked |
| Unauthenticated remote MCP | local loopback / verified secure tunnel; firewall | Network exposure scan |
| Secrets in logs | redact credentials, paths, prompts; store local outputs | Seed synthetic secret and inspect logs |
| Dependency compromise | pin refs, hashes, scan dependencies, review vendored code | Tampered checksum rejected |
| Mixed projects and quota abuse | isolated worktrees/processes/config/ports | Integration never touches existing Arcanvil services |
| Broken rollback | pre-change snapshot + tracked/untracked manifest | Recovery drill with conflicts |
| Misleading success report | native test evidence + verified flag gating | Force missing runtime and expect `blocked` |

## Safe modification protocol

1. Ensure explicit scoped project authorization.
2. Reject changes if input project has unexpected concurrent changes; do not erase them.
3. Capture content hashes for every touched file including untracked files; create a recoverable snapshot *outside* the target subtree.
4. Present structured plan, diff and exact risk level.
5. Obtain approval for writes; additional confirmation for destructive or bulk changes.
6. Apply atomic changes to copies/staging where possible.
7. Run native parser/import/tests and compare expected results.
8. Provide a rollback operation that verifies snapshot identity and warns on concurrent edits.
9. Confirm recovery was tested, never infer from the presence of a Git branch.

## Explicit prohibitions for default workflows

No external network uploads, software installations, credential reads, payments, push/merge/release, edits to private projects, or `rm -rf` without a separate user authorization. No bypassing paid tool quotas or abusive automated engagement on GitHub.

## Disclosure and incident response

Do not publish exploit details or private reports in public GitHub issues. See the root `SECURITY.md`. Document incident severity, affected versions, containment, responsible disclosure, patched verification and changelog entry.
