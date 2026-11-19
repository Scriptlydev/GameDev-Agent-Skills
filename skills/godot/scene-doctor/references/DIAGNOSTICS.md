# G01 scene-doctor diagnostic codes

Codes are stable within schema 0.1.x. `source` is `static` (text parsing) or
`native` (Godot engine output on a disposable copy).

| Code | Severity | Title | Trigger |
|---|---|---|---|
| G01-E001 | error | parse_error | Unclosed header, invalid tag, property outside a section, unterminated value, non-UTF-8 file, wrong first section. |
| G01-E002 | error | ext_resource_missing | `[ext_resource]` path does not exist (non-script). |
| G01-E003 | error | script_missing | `[ext_resource type="Script"]` path does not exist. |
| G01-E004 | error | ext_resource_path_unsafe | Path is not `res://`, escapes the root with `..`, is absolute, a URL, or contains `\`/NUL. Never opened. |
| G01-E005 | error | undefined_ext_resource_id | `ExtResource("id")` used but not declared in the file. |
| G01-E006 | error | undefined_sub_resource_id | `SubResource("id")` used but not declared in the file. |
| G01-E007 | error | invalid_scene_structure | No root, several roots, unnamed node, parent not declared earlier, duplicate node path. |
| G01-E008 | error | malformed_resource_declaration | `ext_resource`/`sub_resource`/`connection` missing a required attribute. |
| G01-E009 | error | duplicate_resource_id | Same id declared twice. |
| G01-E010 | error | symlink_escape | Symlink (file, dir or path component) resolving outside the root. |
| G01-E011 | error | unsupported_format_version | `format=1/2` (Godot 3). |
| G01-E012 | error | path_case_mismatch | Path exists only with different letter case. |
| G01-E013 | error | main_scene_missing | `application/run/main_scene` points to a missing file. |
| G01-E020 | error | native_load_failed | `ResourceLoader.load` returned null in the native check. |
| G01-E021 | error | native_engine_error | Godot printed `ERROR:`/`SCRIPT ERROR:` mentioning a `res://` path. |
| G01-W001 | warning | stale_path_resolved_by_uid | Text path missing but the `uid` maps to an existing file (`.uid`, `.import` or header uid). |
| G01-W002 | warning | connection_node_missing | `[connection]` from/to node not found in the scene. |
| G01-W003 | warning | symlink_not_followed | Symlink inside the root; not followed, native check disabled. |
| G01-W004 | warning | file_skipped | Unreadable, oversized, `user://`, or scan limit reached. |
| G01-W005 | warning | unknown_format_version | Missing or unknown `format=`. |
| G01-W010 | warning | untested_engine_version | Native check ran on a Godot 4 version outside the tested set. |
| G01-W021 | warning | native_engine_warning | Godot printed `WARNING:` mentioning a `res://` path. |
| G01-I001 | info | unused_ext_resource | Declared ext_resource never referenced. |
| G01-I002 | info | uid_only_reference | Reference by UID only; not resolvable statically. |

Run-level errors (in `errors[]`, not `findings[]`):

| Code | Meaning |
|---|---|
| G01-R001..R004 | Input refused: bad root, filesystem root, no `project.godot`, output inside project. Exit 2. |
| G01-B001 | No Godot executable found. |
| G01-B002 | Executable is not Godot 4.x. |
| G01-B003 | Untested Godot 4 version without `--allow-untested-engine`. |
| G01-B004 | Native check refused: symlinks or unsafe references present. |
| G01-X000..X003 | Internal error, engine execution failure, project changed during run, timeout. |

Limits (known, not hidden): instanced sub-scenes are opaque (children/connections
under an `instance=` node are not checked against the instanced scene); UID-only
references are not resolved without `.uid`/`.import` sidecars; binary resources
are not parsed.
