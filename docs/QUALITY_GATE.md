# Quality gates and definition of done

## Four honest statuses

1. **SPECIFIED** — docs are written only.
2. **IMPLEMENTED / UNVERIFIED** — code exists but required engine tests not executed.
3. **ALPHA VERIFIED** — one pinned version, fixture tests and integration proof exist.
4. **BETA / STABLE** — declared environments passed, regression coverage, security review, install docs and real user feedback as applicable.

## Per-skill acceptance checklist

- [ ] Name/frontmatter passes Agent Skills validation.
- [ ] Exact triggering and non-triggering cases documented.
- [ ] Version detection and graceful refusal tested.
- [ ] Positive fixture produces expected structured report.
- [ ] Negative fixture produces expected diagnostic code and correct exit status.
- [ ] Non-destructive default verified by pre-/post-run hashes.
- [ ] No secrets or personal paths in published examples/logs.
- [ ] Dependency license notices reviewed and preserved.
- [ ] Windows and/or Linux native integration executed for each claimed supported platform.
- [ ] Failure modes tested: no engine, corrupt project, timeout, unsupported version.
- [ ] For write-enabled skills: explicit approval, snapshot, changed-file list, rollback dry-run and verified recovery.
- [ ] README examples replayed on a clean environment.
- [ ] Evidence artifacts (commands, versions, logs, screenshot when relevant) attached to PR.
- [ ] Security reviewer sign-off for high-risk abilities.

## Mandatory release gates

- **Alpha:** 1 complete E2E demo, no unapproved writes, CI lint/unit checks, truthful status.
- **Public beta:** 6+ verified skills, clear pinned versions, demo fixture, vulnerability reporting process, license review.
- **v1:** all 30 verified on declared versions, installation smoke tests, upgrade checks, recovery drill, release notes, maintenance plan.

## Evaluation framework

Use at least 3 fixtures per skill: normal, broken, adversarial. Measure false positives, false negatives, useful error messages, unintended file modifications and recovery outcomes. Do not set unmeasured performance SLAs. Every future performance claim must give hardware, input fixture, version and reproducible command.
