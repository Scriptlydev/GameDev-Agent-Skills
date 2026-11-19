# Contributing

Thank you for considering helping GameDev Agent Skills. This repository currently contains a **proposal and specifications**. Contributions that make a small real workflow safer, reproducible or easier to install are especially welcome.

## Contribution types

- Minimal reproducible bug reports and fixtures.
- Additions to tests, diagnostic clarity and safe file handling.
- Documentation corrections and verified editor compatibility results.
- Implementations of proposed skills with real tests and version evidence.

## Development flow

1. Read `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/SECURITY_MODEL.md` and the skill spec.
2. Start from an approved issue; propose scope and acceptance tests.
3. Make a focused branch/PR. Avoid giant changes and unreviewed dependency upgrades.
4. Use synthetic assets with documented redistribution rights.
5. Attach exact commands, versions, logs and negative/positive test results.
6. Identify any AI/tool assistance accurately when required by the contribution policy; do not invent authorship or evaluation evidence.
7. Declare third-party code/assets and preserve notices.

## Pull request checklist

- [ ] Tests genuinely executed and pass, or clearly explained as skipped/blocked.
- [ ] No private data/secrets/paid assets included.
- [ ] No unintended changes to input projects or shell environment.
- [ ] Version compatibility and rollback behaviors tested where relevant.
- [ ] `STATE.md` and `docs/JOURNAL.md` updated if status changes.

## Review policy

A maintainer may reject changes that are untestable, duplicate existing MCP functionality without added value, unsafe, license-incompatible or primarily designed to inflate contribution metrics. Automated code is reviewed by the same standards as manually written code.

## License

By submitting, contributors agree that their contributions may be distributed under the repository's MIT license, subject to ownership and rights they actually possess.
