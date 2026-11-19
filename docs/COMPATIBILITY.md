# Compatibility & upstream dependency matrix

**As-of:** 2026-11-19. **These are documentation targets, not tested claims for our project.** Check upstream releases before installing.

| Integration | Source | Upstream license | Published requirement / note | Our verification |
|---|---|---|---|---|
| Agent Skills | https://agentskills.io/specification | specification site; repo license separate | `SKILL.md` YAML frontmatter format | Format documented, not runtime-tested |
| Godot CLI track A | https://godotengine.org/ | engine license separately | Target Godot **4.5.1** in disposable workspaces | NOT TESTED |
| Godot AI v4 track B | https://github.com/hi-godot/godot-ai | MIT | **Godot 4.7+** as of check date | NOT TESTED |
| Alternative Godot MCP | https://github.com/hybridindie/godot-mcp | MIT | versions/compatibility must be validated independently | NOT TESTED |
| Unity MCP | https://github.com/CoplayDev/unity-mcp | MIT | upstream README: Unity 2021.3 LTS–6.x, Python 3.10+ | NOT TESTED |
| Blender MCP | https://github.com/ahujasid/mcp-for-blender | MIT | Blender Python execution; security caveats | NOT TESTED |
| Blender headless | https://www.blender.org/ | Blender GPL for engine; separate rights in outputs | fixture-based `bpy` inspection proposed | NOT TESTED |

## Version testing discipline

- Pin exact release/tag/commit and record SHA in test evidence.
- Each CI job names its editor version and environment.
- `supported` means installed, exercised, verified, with test reports.
- `planned` or `candidate` means no compatibility guarantee.
- Never overwrite the owner's installed Godot 4.5.1 plugin with a 4.7+ addon.
- Record Windows/Linux behavior independently; a version supported on one platform is not automatically supported on another.

## Security flags

- Godot AI 4.x uses authenticated local connections; adopt its current recommended configuration, do not assume old config formats.
- Blender MCP can execute arbitrary Python; its remote server may lack authentication or encryption. Use local loopback only or a properly secured tunnel, and never expose its port on the public internet.
- Before upgrades, read upstream security notices and test on copies.
