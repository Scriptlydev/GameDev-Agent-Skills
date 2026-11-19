# Testing strategy

## Test pyramid

**Static tests:** YAML frontmatter validity, schema validation, path safety, style and allowed dependencies. **Unit tests:** adapters, parsers, diagnostics, report rendering, snapshot logic using synthetic fixtures. **Integration tests:** real engine CLI/editor on tiny licensed fixtures. **End-to-end tests:** agent selects skill, executes on fixture, produces report, requests approval where needed, rolls back correctly.

## Minimum fixture matrix

| Suite | Positive fixture | Negative fixture | Security fixture |
|---|---|---|---|
| Godot | minimal 4.5.1 scene | missing resource path | `..` traversal and untrusted script content |
| Unity | minimal scene + prefab | broken reference or compiler error | path outside project or extra tool privilege |
| Blender | cube/rig test `.blend` | broken UV/rig export | disallowed Python execution and remote socket exposure |
| Universal | small synthetic git repo | conflicting changes | secret leak / malicious README |

## Observability

Every CI/test result includes tool versions, OS, command, fixture hash, expected/actual assertions and logs. Private data must never leave the test environment. Skipped due to missing software is **skipped/not tested**, not a pass.

## Branch protection proposal

On public launch: required docs/schema checks + unit tests on all PRs; selected native-editor checks on a dedicated runner; approval by a separate reviewer for write-capable workflows. Do not require impossible GPU/editor tests on all outside contributors; trusted maintainers run release-specific validations.

## Regression tracking

Each issue links a minimal synthetic reproduction, skill version, exact tool version and expected/actual outcome. Regressions fail release gating until resolved or clearly marked as unsupported.
