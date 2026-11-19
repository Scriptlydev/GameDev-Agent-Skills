# Installation, packaging and developer onboarding plan

**Not an installation guide for released software:** the package currently consists of planning documents only.

## Proposed developer prerequisites

- Git and Python 3.11+ for the future core CLI (provisional; not yet implemented).
- Godot 4.5.1 for first CLI fixture tests, isolated project copy.
- Optional Godot 4.7+ for Godot AI adapter integration; do not upgrade over 4.5.1.
- Blender with Python scripting for future read-only model inspection.
- Licensed Unity Editor and its Test Framework for future Unity fixture tests.
- `uv` and optional MCP clients only as explicitly authorized tools.

## First installation test plan

1. Clone the public repo after it is created; read `AGENTS.md` and support matrix.
2. Create an isolated Python virtual environment; install locked project requirements (to be added in implementation phase).
3. Copy the synthetic Godot fixture into a scratch directory.
4. Detect Godot binary and check version.
5. Execute G01 read-only inspection; confirm JSON output and untouched input fixture.
6. Shut down child processes and remove only explicitly created temporary files.
7. Repeat on a fresh Windows and Linux environment before declaring support.

## MCP path

Install each third-party MCP tool following its *current official upstream documentation*. Prefer pinned tagged releases, avoid unreviewed `curl | sh`/`irm | iex` execution from unknown URLs and never open ports publicly. Maintain a reference installation manifest rather than silently changing global agent settings.

## Distribution options to decide after proof of concept

- Pure Agent Skills directories + optional Python package CLI.
- `pipx`/`uv tool` installer for shared read-only analysis utilities.
- No giant fork or bundled editor binaries.
- Adapter packages may be optional extras, not hard required dependencies.

## User documentation requirements before public beta

Each supported client needs exact skill discovery steps, current tested version, permissions, uninstall and common failure scenarios. No client compatibility is claimed until run on that specific client.
