# Demo and evaluation storyboard (not filmed yet)

## Demo 1 — Godot broken scene

- Present small public synthetic Godot scene whose resource path was deliberately broken.
- Show the exact invocation of G01, the failed file reference, the JSON diagnostic code and the unchanged original file hashes.
- Repair the fixture manually, re-run, show actual clean parse and tool versions.
- Time and benchmark claims only after measurements and repeatability checks.

## Demo 2 — Blender faulty asset

- Inspect a safe sample mesh with degenerate faces and/or a missing UV layer using B01/B03 once implemented.
- Show the finding, fix proposal and preservation of original asset.
- Run headless `bpy` validation and capture a reproducible report.

## Demo 3 — Unity missing prefab

- Use a redistributable test project with a deliberately broken prefab reference.
- Show evidence and exact editor version from Y02/Y03 once implemented.
- Do not record or announce this demo until integration is actually tested.

## Public proof assets

Demo script, OS/editor version, commands, raw sanitized result, checksums, repository tag, public fixture source and screenshots/video only from authentic recordings.
