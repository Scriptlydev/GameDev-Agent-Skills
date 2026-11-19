# Release and maintenance plan

## Tagging

Use `v0.1.0-alpha`, `v0.2.0-beta`, `v1.0.0` only after associated gates pass. The current documentation has no software release.

## Checklist before a public release

- [ ] Maintainer approves name/copyright and license.
- [ ] Working code actually exists, not just SKILL.md descriptions.
- [ ] No keys/private files or proprietary game assets in git history.
- [ ] Install + execution reproduced on a clean setup.
- [ ] Supported versions and exact dependencies pinned in release notes.
- [ ] Third-party licenses and notices complete.
- [ ] Security and restore drill passed, vulnerabilities handled.
- [ ] Native test evidence stored and report schema validated.
- [ ] Documentation, examples and screenshots reflect actual app behavior.
- [ ] CI results reviewed; no ignored failures or falsely labeled skips.

## Version support

At minimum, explicitly identify tested engine/platform combinations. Provide last-known-working adapter version, test evidence and migration guidance. Apply SemVer to public APIs/report schemas after 1.0.

## Maintenance

Triage security reports first, then broken adapters caused by upstream updates, then performance. Establish maintainer review capacity before encouraging external contributions. Document deprecations one release in advance where possible.
