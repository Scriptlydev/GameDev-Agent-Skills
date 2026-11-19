#!/usr/bin/env python3
"""G01 scene-doctor: read-only analysis of Godot 4 text scenes and resources.

Only one command exists: ``inspect``. The original project is never written to.
Native validation (optional) runs the Godot executable on a disposable copy of
the project, with an isolated HOME/XDG profile, and is reported separately from
static parsing. Standard library only (Python 3.10+).

Exit codes: 0 pass/warn, 1 fail, 2 refused (unsafe or invalid input),
3 blocked/not_tested (no usable engine), 4 internal error or timeout.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import platform
import posixpath
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"
SKILL_ID = "G01"
TOOL_VERSION = "0.1.0"
SUPPORTED_ENGINE_VERSIONS = ("4.5.1",)  # Track A target (ADR-004)
SCENE_SUFFIXES = (".tscn", ".tres")
SKIP_DIRS = {".godot", ".git", ".import"}
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_SCANNED_FILES = 50_000
EVIDENCE_LIMIT = 200
EXIT = {"pass": 0, "warn": 0, "fail": 1, "refused": 2, "blocked": 3, "not_tested": 3, "error": 4}
NATIVE_MARK = "G01_SCENE_DOCTOR"
CHECK_SCRIPT = Path(__file__).with_name("godot_check_scenes.gd")

HEADER_ATTR = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*("(?:[^"\\]|\\.)*"|[^\s\]]+(?:\([^)]*\))?)')
REF_OR_STRING = re.compile(r'"(?:[^"\\]|\\.)*"|\b(?P<kind>Ext|Sub)Resource\(\s*(?:"(?P<sid>[^"]*)"|(?P<nid>\d+))\s*\)')
UID_RE = re.compile(r'uid://[a-z0-9]+')
VERSION_RE = re.compile(r'^(\d+)\.(\d+)(?:\.(\d+))?\.([a-z0-9_]+)')

# Stable diagnostic catalog: code -> (severity, short title). See references/DIAGNOSTICS.md.
CODES = {
    "G01-E001": ("error", "parse_error"),
    "G01-E002": ("error", "ext_resource_missing"),
    "G01-E003": ("error", "script_missing"),
    "G01-E004": ("error", "ext_resource_path_unsafe"),
    "G01-E005": ("error", "undefined_ext_resource_id"),
    "G01-E006": ("error", "undefined_sub_resource_id"),
    "G01-E007": ("error", "invalid_scene_structure"),
    "G01-E008": ("error", "malformed_resource_declaration"),
    "G01-E009": ("error", "duplicate_resource_id"),
    "G01-E010": ("error", "symlink_escape"),
    "G01-E011": ("error", "unsupported_format_version"),
    "G01-E012": ("error", "path_case_mismatch"),
    "G01-E013": ("error", "main_scene_missing"),
    "G01-E020": ("error", "native_load_failed"),
    "G01-E021": ("error", "native_engine_error"),
    "G01-W001": ("warning", "stale_path_resolved_by_uid"),
    "G01-W002": ("warning", "connection_node_missing"),
    "G01-W003": ("warning", "symlink_not_followed"),
    "G01-W004": ("warning", "file_skipped"),
    "G01-W005": ("warning", "unknown_format_version"),
    "G01-W010": ("warning", "untested_engine_version"),
    "G01-W021": ("warning", "native_engine_warning"),
    "G01-I001": ("info", "unused_ext_resource"),
    "G01-I002": ("info", "uid_only_reference"),
}

SUGGESTIONS = {
    "G01-E002": "Restore the referenced file, or re-point the ext_resource in the Godot editor (Project > Tools > Orphan Resource Explorer / dependency editor).",
    "G01-E003": "Restore the script or detach/re-attach the correct script on the node in the Godot editor.",
    "G01-E004": "Reference only files inside the project with a res:// path; move the asset into the project first.",
    "G01-E005": "Declare the [ext_resource] with this id or fix the ExtResource(...) id in the property.",
    "G01-E006": "Declare the [sub_resource] with this id or fix the SubResource(...) id.",
    "G01-E007": "Re-save the scene from the Godot editor; each scene needs exactly one root and parents declared before children.",
    "G01-E010": "Replace the symlink by a real file inside the project; scene-doctor does not follow links outside the root.",
    "G01-E011": "Open the file with a matching Godot major version; Godot 3 (format=2) is out of scope for G01.",
    "G01-E012": "Fix the letter case of the path; it breaks on case-sensitive filesystems and in exports.",
    "G01-E013": "Set Project Settings > Application > Run > Main Scene to an existing scene.",
    "G01-W001": "Re-save the scene in the editor so the text path matches the file the UID points to.",
}


class Refusal(Exception):
    """Unsafe or invalid input: stop before reading project content."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def now_iso() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clip(text: str, limit: int = EVIDENCE_LIMIT) -> str:
    text = text.replace("\r", "")
    return text if len(text) <= limit else text[: limit - 1] + "…"


@dataclass
class Section:
    tag: str
    attrs: dict[str, str]
    line: int
    props: list[tuple[str, str, int]] = field(default_factory=list)


@dataclass
class Context:
    root: Path
    findings: list[dict[str, Any]] = field(default_factory=list)
    uid_map: dict[str, str] = field(default_factory=dict)
    scanned: list[str] = field(default_factory=list)
    input_hashes: dict[str, str] = field(default_factory=dict)
    symlinks: list[str] = field(default_factory=list)

    def add(self, code: str, summary: str, file: str | None = None, line: int | None = None,
            evidence: str = "", source: str = "static") -> None:
        severity = CODES[code][0]
        item = {"code": code, "severity": severity, "title": CODES[code][1], "summary": summary,
                "file": file, "line": line, "evidence": clip(evidence), "source": source}
        if code in SUGGESTIONS:
            item["suggestion"] = SUGGESTIONS[code]
        self.findings.append(item)


# --------------------------------------------------------------------------- paths

def canonical_root(raw: str) -> Path:
    if not raw or "\x00" in raw:
        raise Refusal("G01-R001", "Project root is empty or contains a NUL byte.")
    candidate = Path(raw).expanduser()
    try:
        root = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        raise Refusal("G01-R001", "Project root does not exist or cannot be resolved.") from None
    if not root.is_dir():
        raise Refusal("G01-R001", "Project root is not a directory.")
    if root == Path(root.anchor):
        raise Refusal("G01-R002", "Refusing to analyze a filesystem root.")
    marker = root / "project.godot"
    if marker.is_symlink() or not marker.is_file():
        raise Refusal("G01-R003", "No regular project.godot file at the project root; not a Godot project.")
    return root


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def res_path(root: Path, path: Path) -> str:
    return "res://" + path.relative_to(root).as_posix()


def resolve_res(root: Path, raw: str) -> tuple[str, Path | None, str | None]:
    """Map a res:// path to a filesystem path inside root without following escapes.

    Returns (kind, path, detail) where kind is ok, unsafe, uid or user.
    """
    if raw.startswith("uid://"):
        return "uid", None, None
    if raw.startswith("user://"):
        return "user", None, None
    if not raw.startswith("res://"):
        return "unsafe", None, "path is not a res:// project path"
    rel = raw[len("res://"):]
    if "\\" in rel or "\x00" in rel:
        return "unsafe", None, "path contains a backslash or NUL byte"
    norm = posixpath.normpath(rel) if rel else "."
    if norm.startswith("/") or norm == ".." or norm.startswith("../") or re.match(r"^[A-Za-z]:", norm):
        return "unsafe", None, "path escapes the project root"
    return "ok", root.joinpath(*[p for p in norm.split("/") if p not in ("", ".")]), None


def case_mismatch(root: Path, target: Path) -> str | None:
    """Return the real relative path if target exists only with different letter case."""
    rel_parts = target.relative_to(root).parts
    current = root
    real_parts: list[str] = []
    for part in rel_parts:
        try:
            names = os.listdir(current)
        except OSError:
            return None
        if part in names:
            match = part
        else:
            lowered = [n for n in names if n.lower() == part.lower()]
            if len(lowered) != 1:
                return None
            match = lowered[0]
        real_parts.append(match)
        current = current / match
    real = "/".join(real_parts)
    return real if real != "/".join(rel_parts) and current.exists() else None


# --------------------------------------------------------------------------- walk

def walk_project(ctx: Context) -> tuple[list[Path], list[Path]]:
    scenes: list[Path] = []
    sidecars: list[Path] = []
    count = 0
    for dirpath, dirnames, filenames in os.walk(ctx.root, followlinks=False):
        current = Path(dirpath)
        if current != ctx.root and (current / ".gdignore").exists():
            dirnames[:] = []
            continue
        kept = []
        for name in sorted(dirnames):
            full = current / name
            if name in SKIP_DIRS:
                continue
            if full.is_symlink():
                record_symlink(ctx, full)
                continue
            kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames):
            full = current / name
            count += 1
            if count > MAX_SCANNED_FILES:
                ctx.add("G01-W004", f"Stopped scanning after {MAX_SCANNED_FILES} files.", None, None)
                return scenes, sidecars
            if full.is_symlink():
                record_symlink(ctx, full)
                continue
            if name.endswith(SCENE_SUFFIXES):
                scenes.append(full)
            elif name.endswith((".uid", ".import")):
                sidecars.append(full)
    return scenes, sidecars


def record_symlink(ctx: Context, link: Path) -> None:
    rel = res_path(ctx.root, link)
    ctx.symlinks.append(rel)
    try:
        target = link.resolve(strict=False)
    except (OSError, RuntimeError):
        target = None
    if target is None or not is_inside(target, ctx.root):
        ctx.add("G01-E010", "Symbolic link points outside the project root and was not followed.", rel)
    else:
        ctx.add("G01-W003", "Symbolic link inside the project was not followed; native validation is disabled.", rel)


def read_text(ctx: Context, path: Path) -> str | None:
    rel = res_path(ctx.root, path)
    try:
        size = path.stat().st_size
    except OSError as exc:
        ctx.add("G01-W004", f"File could not be read: {exc.strerror}.", rel)
        return None
    if size > MAX_FILE_BYTES:
        ctx.add("G01-W004", f"File larger than {MAX_FILE_BYTES} bytes was skipped.", rel)
        return None
    try:
        raw = path.read_bytes()
    except OSError as exc:
        ctx.add("G01-W004", f"File could not be read: {exc.strerror}.", rel)
        return None
    ctx.input_hashes[rel] = hashlib.sha256(raw).hexdigest()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        ctx.add("G01-E001", "File is not valid UTF-8 text (binary .scn/.res files are out of scope).", rel)
        return None


def build_uid_map(ctx: Context, scenes: list[Path], sidecars: list[Path], texts: dict[Path, str]) -> None:
    for path in sidecars:
        try:
            if path.stat().st_size > 65536:
                continue
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = UID_RE.search(body)
        if match:
            ctx.uid_map[match.group(0)] = res_path(ctx.root, path.with_suffix(""))
    for path in scenes:
        body = texts.get(path)
        if not body:
            continue
        first = body.lstrip().split("\n", 1)[0]
        match = re.search(r'\buid="(uid://[a-z0-9]+)"', first)
        if match:
            ctx.uid_map[match.group(1)] = res_path(ctx.root, path)


# --------------------------------------------------------------------------- parser

def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return bytes(value[1:-1], "utf-8").decode("unicode_escape", errors="replace") if "\\" in value else value[1:-1]
    return value


def parse_sections(ctx: Context, rel: str, text: str) -> list[Section] | None:
    """Parse Godot's text resource format into sections. Returns None on fatal parse error."""
    sections: list[Section] = []
    i = 0
    line = 1
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\n":
            line += 1
            i += 1
            continue
        if ch in " \t\r":
            i += 1
            continue
        if ch == ";":  # comment line
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "[":
            start_line = line
            j = i + 1
            in_str = escape = False
            while j < n:
                c = text[j]
                if in_str:
                    if escape:
                        escape = False
                    elif c == "\\":
                        escape = True
                    elif c == '"':
                        in_str = False
                elif c == '"':
                    in_str = True
                elif c == "]":
                    break
                elif c == "\n":
                    break
                j += 1
            if j >= n or text[j] != "]":
                ctx.add("G01-E001", "Section header is not closed with ']'.", rel, start_line,
                        text[i:min(n, i + 80)].split("\n", 1)[0])
                return None
            header = text[i + 1:j].strip()
            tag, _, rest = header.partition(" ")
            if not re.fullmatch(r"[a-z_]+", tag):
                ctx.add("G01-E001", "Invalid section tag.", rel, start_line, header)
                return None
            attrs = {k: v for k, v in HEADER_ATTR.findall(rest)}
            sections.append(Section(tag, attrs, start_line))
            i = j + 1
            continue
        # property: key = value (value may span lines)
        j = text.find("=", i)
        eol = text.find("\n", i)
        if j == -1 or (eol != -1 and eol < j):
            ctx.add("G01-E001", "Expected 'key = value' or a [section] header.", rel, line,
                    text[i:eol if eol != -1 else n])
            return None
        key = text[i:j].strip()
        if not sections:
            ctx.add("G01-E001", "Property found before the file header.", rel, line, key)
            return None
        k = j + 1
        depth = 0
        in_str = escape = False
        start_line = line
        while k < n:
            c = text[k]
            if in_str:
                if escape:
                    escape = False
                elif c == "\\":
                    escape = True
                elif c == '"':
                    in_str = False
                elif c == "\n":
                    line += 1
            else:
                if c == '"':
                    in_str = True
                elif c in "([{":
                    depth += 1
                elif c in ")]}":
                    depth -= 1
                elif c == "\n":
                    if depth <= 0:
                        break
                    line += 1
            k += 1
        if in_str or depth > 0:
            ctx.add("G01-E001", "Unterminated string or bracket in property value.", rel, start_line, key)
            return None
        sections[-1].props.append((key, text[j + 1:k].strip(), start_line))
        i = k
    return sections


# --------------------------------------------------------------------------- checks

def check_file(ctx: Context, path: Path, text: str) -> list[str]:
    """Return res:// paths of declared ext_resources that are unsafe (used to gate native runs)."""
    rel = res_path(ctx.root, path)
    ctx.scanned.append(rel)
    sections = parse_sections(ctx, rel, text)
    if sections is None:
        return []
    if not sections:
        ctx.add("G01-E001", "File is empty.", rel, 1)
        return []
    expected = "gd_scene" if path.suffix == ".tscn" else "gd_resource"
    head = sections[0]
    if head.tag != expected:
        ctx.add("G01-E001", f"First section must be [{expected} ...].", rel, head.line, f"[{head.tag}]")
        return []
    fmt = unquote(head.attrs.get("format", ""))
    if fmt in ("1", "2"):
        ctx.add("G01-E011", f"format={fmt} is a Godot 3 text format; G01 supports Godot 4 (format=3/4).", rel, head.line)
        return []
    if fmt not in ("3", "4"):
        ctx.add("G01-W005", f"Unknown or missing format version '{fmt}'.", rel, head.line)

    unsafe: list[str] = []
    ext_ids: dict[str, Section] = {}
    sub_ids: dict[str, Section] = {}
    used_ext: set[str] = set()
    for sec in sections[1:]:
        if sec.tag == "ext_resource":
            rid = unquote(sec.attrs.get("id", ""))
            raw_path = unquote(sec.attrs.get("path", "")) if "path" in sec.attrs else ""
            if not rid or ("path" not in sec.attrs and "uid" not in sec.attrs):
                ctx.add("G01-E008", "[ext_resource] needs an id and a path.", rel, sec.line)
                continue
            if rid in ext_ids:
                ctx.add("G01-E009", f"Duplicate ext_resource id '{rid}'.", rel, sec.line)
            ext_ids[rid] = sec
            if not raw_path:
                ctx.add("G01-I002", "ext_resource has only a UID; its target cannot be checked statically.", rel, sec.line)
                continue
            if check_ext_path(ctx, rel, sec, raw_path):
                unsafe.append(raw_path)
        elif sec.tag == "sub_resource":
            rid = unquote(sec.attrs.get("id", ""))
            if not rid or "type" not in sec.attrs:
                ctx.add("G01-E008", "[sub_resource] needs a type and an id.", rel, sec.line)
                continue
            if rid in sub_ids:
                ctx.add("G01-E009", f"Duplicate sub_resource id '{rid}'.", rel, sec.line)
            sub_ids[rid] = sec

    def scan_refs(sec: Section, value: str, line: int, is_header: bool = False) -> None:
        # One left-to-right scan: string literals are consumed whole, so a reference
        # written inside a string (e.g. a Label text) is never taken as a real one.
        for match in REF_OR_STRING.finditer(value):
            kind = match.group("kind")
            if not kind:
                continue
            rid = match.group("sid") if match.group("sid") is not None else match.group("nid")
            if kind == "Ext":
                used_ext.add(rid)
                if rid not in ext_ids:
                    ctx.add("G01-E005", f"ExtResource(\"{rid}\") is not declared in this file.", rel, line, value)
            elif rid not in sub_ids:
                ctx.add("G01-E006", f"SubResource(\"{rid}\") is not declared in this file.", rel, line, value)

    for sec in sections[1:]:
        for key in ("instance", "instance_placeholder"):
            if key in sec.attrs:
                scan_refs(sec, sec.attrs[key], sec.line, True)
        for _key, value, line in sec.props:
            scan_refs(sec, value, line)

    for rid, sec in ext_ids.items():
        if rid not in used_ext:
            ctx.add("G01-I001", f"ext_resource '{rid}' is declared but never used.", rel, sec.line)

    if path.suffix == ".tscn":
        check_structure(ctx, rel, sections, head)
    return unsafe


def check_ext_path(ctx: Context, rel: str, sec: Section, raw_path: str) -> bool:
    """Validate one ext_resource path. Returns True if the path is unsafe."""
    kind, target, detail = resolve_res(ctx.root, raw_path)
    rtype = unquote(sec.attrs.get("type", ""))
    if kind == "unsafe":
        ctx.add("G01-E004", f"Unsafe ext_resource path: {detail}.", rel, sec.line, raw_path)
        return True
    if kind == "user":
        ctx.add("G01-W004", "user:// reference is outside the project and was not checked.", rel, sec.line, raw_path)
        return False
    if kind == "uid" or target is None:
        return False
    # Refuse symlink escapes on every component of the path.
    probe = ctx.root
    for part in target.relative_to(ctx.root).parts:
        probe = probe / part
        if probe.is_symlink():
            real = probe.resolve(strict=False)
            if not is_inside(real, ctx.root):
                ctx.add("G01-E010", "ext_resource path goes through a symlink that leaves the project.", rel, sec.line, raw_path)
                return True
    if target.is_file():
        return False
    uid = unquote(sec.attrs.get("uid", ""))
    if uid and uid in ctx.uid_map:
        ctx.add("G01-W001", f"Path is stale but the UID resolves to {ctx.uid_map[uid]}.", rel, sec.line, raw_path)
        return False
    real = case_mismatch(ctx.root, target)
    if real:
        ctx.add("G01-E012", f"Path differs only by letter case from res://{real}.", rel, sec.line, raw_path)
        return False
    if rtype == "Script":
        ctx.add("G01-E003", f"Script {raw_path} does not exist.", rel, sec.line, raw_path)
    else:
        label = f"{rtype} " if rtype else ""
        ctx.add("G01-E002", f"Missing {label}resource {raw_path}.", rel, sec.line, raw_path)
    return False


def check_structure(ctx: Context, rel: str, sections: list[Section], head: Section) -> None:
    nodes = [s for s in sections if s.tag == "node"]
    if not nodes:
        ctx.add("G01-E007", "Scene has no node; a scene needs exactly one root node.", rel, head.line)
        return
    known: set[str] = set()
    opaque: set[str] = set()  # instanced subtrees: children may come from another scene
    root_name = None
    for sec in nodes:
        name = unquote(sec.attrs.get("name", ""))
        if not name:
            ctx.add("G01-E007", "[node] without a name.", rel, sec.line)
            continue
        if "parent" not in sec.attrs:
            if root_name is not None:
                ctx.add("G01-E007", f"Second root node '{name}': a scene has exactly one root.", rel, sec.line)
                continue
            root_name = name
            path = "."
        else:
            if root_name is None:
                ctx.add("G01-E007", f"Node '{name}' declares a parent before any root node.", rel, sec.line)
                continue
            parent = unquote(sec.attrs["parent"])
            if parent != "." and parent not in known and not under_opaque(parent, opaque):
                ctx.add("G01-E007", f"Parent '{parent}' of node '{name}' is not declared earlier in the scene.",
                        rel, sec.line, parent)
            path = name if parent == "." else f"{parent}/{name}"
        if path in known:
            ctx.add("G01-E007", f"Duplicate node path '{path}'.", rel, sec.line)
        known.add(path)
        if "instance" in sec.attrs or "instance_placeholder" in sec.attrs:
            opaque.add(path)
    for sec in sections:
        if sec.tag != "connection":
            continue
        for key in ("from", "to"):
            target = unquote(sec.attrs.get(key, ""))
            if not target:
                ctx.add("G01-E008", f"[connection] without '{key}'.", rel, sec.line)
            elif target != "." and target not in known and not under_opaque(target, opaque):
                ctx.add("G01-W002", f"Connection '{key}' node '{target}' does not exist in this scene.", rel, sec.line, target)


def under_opaque(path: str, opaque: set[str]) -> bool:
    if "." in opaque:  # inherited scene: everything may come from the base scene
        return True
    parts = path.split("/")
    return any("/".join(parts[:i]) in opaque for i in range(1, len(parts) + 1))


def check_project(ctx: Context) -> None:
    text = read_text(ctx, ctx.root / "project.godot")
    if text is None:
        return
    section = ""
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
        elif section == "application" and line.startswith("run/main_scene="):
            value = unquote(line.split("=", 1)[1].strip())
            kind, target, _detail = resolve_res(ctx.root, value)
            if kind == "uid":
                if value not in ctx.uid_map:
                    ctx.add("G01-I002", "Main scene is a UID that could not be resolved statically.", "res://project.godot", number, value)
            elif kind != "ok" or target is None:
                ctx.add("G01-E004", "Main scene path is not inside the project.", "res://project.godot", number, value)
            elif not target.is_file():
                ctx.add("G01-E013", f"Main scene {value} does not exist.", "res://project.godot", number, value)


# --------------------------------------------------------------------------- audit

def snapshot(root: Path) -> dict[str, str]:
    """Hash every file (tracked or not) under root without following symlinks."""
    result: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        for name in dirnames:
            full = current / name
            if full.is_symlink():
                result[full.relative_to(root).as_posix() + "/"] = "symlink:" + os.readlink(full)
        dirnames[:] = [d for d in dirnames if not (current / d).is_symlink()]
        for name in filenames:
            full = current / name
            rel = full.relative_to(root).as_posix()
            if full.is_symlink():
                result[rel] = "symlink:" + os.readlink(full)
            else:
                try:
                    result[rel] = sha256_file(full)
                except OSError as exc:
                    result[rel] = f"unreadable:{exc.errno}"
    return result


def diff_snapshots(before: dict[str, str], after: dict[str, str]) -> list[str]:
    changed = [k for k in before if after.get(k) != before[k]]
    added = [k for k in after if k not in before]
    return sorted(changed + added)


# --------------------------------------------------------------------------- engine

class Redactor:
    def __init__(self, pairs: list[tuple[str, str]]):
        self.pairs = sorted([(a, b) for a, b in pairs if a], key=lambda p: -len(p[0]))

    def __call__(self, text: str) -> str:
        for raw, alias in self.pairs:
            text = text.replace(raw, alias)
        return text


def find_engine(explicit: str | None) -> Path | None:
    candidates = [explicit] if explicit else [os.environ.get("GODOT_BIN"), shutil.which("godot4"), shutil.which("godot")]
    for item in candidates:
        if not item:
            continue
        path = Path(item).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return path.resolve()
        if explicit:
            return None
    return None


def run_engine(cmd: list[str], env: dict[str, str], cwd: Path, timeout: float) -> tuple[int | None, str]:
    proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, start_new_session=True)
    try:
        out, _ = proc.communicate(timeout=timeout)
        return proc.returncode, out.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            proc.kill()
        out, _ = proc.communicate()
        return None, out.decode("utf-8", errors="replace")


def parse_version(text: str) -> tuple[str | None, tuple[int, int, int] | None]:
    for raw in text.splitlines():
        match = VERSION_RE.match(raw.strip())
        if match:
            major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3) or 0)
            return raw.strip(), (major, minor, patch)
    return None, None


def engine_messages(log: str) -> list[tuple[str, str, str | None]]:
    """Extract (level, message, current_file) from a Godot log using our BEGIN markers."""
    messages = []
    current = None
    for raw in log.splitlines():
        line = raw.strip()
        if line.startswith(NATIVE_MARK + " BEGIN "):
            current = line.split(" BEGIN ", 1)[1].strip()
            continue
        if line.startswith(NATIVE_MARK):
            continue
        for prefix, level in (("SCRIPT ERROR:", "error"), ("ERROR:", "error"), ("WARNING:", "warning")):
            if line.startswith(prefix):
                messages.append((level, line[len(prefix):].strip(), current))
                break
    return messages


def native_validate(ctx: Context, report: dict[str, Any], engine: Path, args: argparse.Namespace,
                    redact: Redactor, evidence_dir: Path | None) -> str:
    """Run Godot on a disposable copy. Returns native outcome: ok, failed, blocked, timeout, error."""
    version_env = isolated_env(Path(tempfile.mkdtemp(prefix="g01-home-")))
    rc, out = run_engine([str(engine), "--headless", "--version"], version_env, Path(version_env["HOME"]), 30)
    shutil.rmtree(version_env["HOME"], ignore_errors=True)
    version_text, version = parse_version(out)
    report["engine_version"] = version_text
    report["environment"]["engine_binary_sha256"] = sha256_file(engine)
    record_test(report, "engine_version", "godot --headless --version", "a Godot 4.x version string",
                version_text or clip(redact(out)), "pass" if version and version[0] == 4 else "fail")
    if not version or version[0] != 4:
        report["errors"].append({"code": "G01-B002", "message": "Engine is not Godot 4.x; refusing native validation.", "retryable": False})
        return "blocked"
    short = f"{version[0]}.{version[1]}.{version[2]}"
    supported = short in SUPPORTED_ENGINE_VERSIONS
    if not supported:
        if not args.allow_untested_engine:
            report["errors"].append({"code": "G01-B003", "message": f"Godot {short} is not a tested version ({', '.join(SUPPORTED_ENGINE_VERSIONS)}). Re-run with --allow-untested-engine to try it; the result stays unverified.", "retryable": True})
            return "blocked"
        ctx.add("G01-W010", f"Godot {short} has not been validated for G01 (tested target: {', '.join(SUPPORTED_ENGINE_VERSIONS)}); native result is informative only.", None, None, version_text or "", "native")
    report["_engine_supported"] = supported

    rc_help, help_text = run_engine([str(engine), "--headless", "--help"], version_env | {"HOME": tempfile.gettempdir()}, Path(tempfile.gettempdir()), 30)
    recovery = "--recovery-mode" in help_text

    workdir = Path(tempfile.mkdtemp(prefix="g01-workspace-"))
    try:
        ws = workdir / "project"
        shutil.copytree(ctx.root, ws, symlinks=True, ignore=shutil.ignore_patterns(".godot", ".git"))
        redact.pairs.insert(0, (str(ws), "<workspace>"))
        redact.pairs.insert(0, (str(workdir), "<workdir>"))
        env = isolated_env(workdir / "home")
        token = uuid.uuid4().hex[:8]
        script_name = f"__g01_check_{token}.gd"
        list_name = f"__g01_scenes_{token}.txt"
        shutil.copyfile(CHECK_SCRIPT, ws / script_name)
        (ws / list_name).write_text("\n".join(ctx.scanned) + "\n", encoding="utf-8")

        import_cmd = [str(engine), "--headless", "--path", str(ws)] + (["--recovery-mode"] if recovery else []) + ["--import"]
        rc1, log1 = run_engine(import_cmd, env, ws, args.timeout)
        shown1 = "godot --headless --path <workspace>" + (" --recovery-mode" if recovery else "") + " --import"
        report["actions"].append({"tool": shown1, "intent": "import resources in a disposable copy", "approved": True,
                                  "target": "workspace copy", "changed_files": []})
        save_log(report, evidence_dir, "godot-import.log", redact(log1), "native import log (redacted)")
        if rc1 is None:
            record_test(report, "native_import", shown1, "exit 0 within timeout", f"timeout after {args.timeout}s", "fail")
            return "timeout"
        record_test(report, "native_import", shown1, "exit 0", f"exit {rc1}", "pass" if rc1 == 0 else "fail")

        check_cmd = [str(engine), "--headless", "--path", str(ws), "--script", f"res://{script_name}", "--", f"res://{list_name}"]
        shown2 = f"godot --headless --path <workspace> --script res://{script_name} -- res://{list_name}"
        rc2, log2 = run_engine(check_cmd, env, ws, args.timeout)
        report["actions"].append({"tool": shown2, "intent": "load each scanned scene/resource without instantiating it",
                                  "approved": True, "target": "workspace copy", "changed_files": []})
        save_log(report, evidence_dir, "godot-check.log", redact(log2), "native load-check log (redacted)")
        if rc2 is None:
            record_test(report, "native_load_check", shown2, "exit 0 within timeout", f"timeout after {args.timeout}s", "fail")
            return "timeout"

        results = {}
        done = False
        for raw in log2.splitlines():
            line = raw.strip()
            if line.startswith(NATIVE_MARK + " RESULT "):
                try:
                    item = json.loads(line.split(" RESULT ", 1)[1])
                    results[item.get("path")] = item
                except ValueError:
                    continue
            elif line == NATIVE_MARK + " DONE":
                done = True
        complete = done and rc2 == 0 and all(p in results for p in ctx.scanned)
        record_test(report, "native_load_check", shown2, f"exit 0, DONE marker, {len(ctx.scanned)} result(s)",
                    f"exit {rc2}, done={done}, results={len(results)}", "pass" if complete else "fail")
        for path in ctx.scanned:
            item = results.get(path)
            if item and not item.get("loaded"):
                ctx.add("G01-E020", "Godot could not load this file.", path, None, json.dumps(item, sort_keys=True), "native")
        seen = set()
        for level, message, current in engine_messages(log1) + engine_messages(log2):
            clean = redact(message)
            if "res://" not in clean or clean in seen or script_name in clean or list_name in clean:
                continue
            seen.add(clean)
            ctx.add("G01-E021" if level == "error" else "G01-W021", "Godot reported: " + clip(clean, 160), current, None, clean, "native")
        return "ok" if (complete and rc1 == 0) else "failed"
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def isolated_env(home: Path) -> dict[str, str]:
    home.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k in ("PATH", "LANG", "LC_ALL", "TZ")}
    env.update({"HOME": str(home), "XDG_CONFIG_HOME": str(home / "config"), "XDG_DATA_HOME": str(home / "data"),
                "XDG_CACHE_HOME": str(home / "cache"), "TMPDIR": str(home / "tmp")})
    (home / "tmp").mkdir(exist_ok=True)
    return env


def record_test(report: dict[str, Any], name: str, command: str, expected: str, observed: str, result: str,
                evidence: str = "") -> None:
    report["tests"].append({"name": name, "command": command, "expected": expected, "observed": observed,
                            "result": result, "evidence": evidence})


def save_log(report: dict[str, Any], evidence_dir: Path | None, name: str, text: str, purpose: str) -> None:
    if evidence_dir is None:
        return
    target = evidence_dir / name
    target.write_text(text, encoding="utf-8")
    report["artifacts"].append({"path": name, "purpose": purpose, "sha256": sha256_file(target), "privacy": "redacted"})


# --------------------------------------------------------------------------- inspect

def new_report(alias: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "run_id": "g01-" + uuid.uuid4().hex[:12], "skill_id": SKILL_ID,
        "status": "error", "verified": False, "engine": "godot", "engine_version": None,
        "project_root_redacted": alias, "started_at": now_iso(), "completed_at": None,
        "input_hashes": {}, "findings": [], "actions": [], "tests": [], "artifacts": [],
        "rollback": {"available": False, "verified": False, "reason": "read-only inspection; nothing to roll back"},
        "errors": [],
        "tool": {"name": "scene-doctor", "version": TOOL_VERSION, "mode": "inspect", "read_only": True},
        "environment": {"os": platform.system(), "os_release": platform.release(),
                        "python": platform.python_version(), "engine_binary_sha256": None},
        "summary": {},
    }


def safe_output_path(raw: str | None, root: Path | None, label: str) -> Path | None:
    if not raw:
        return None
    path = Path(raw).expanduser().resolve()
    if root is not None and (path == root or is_inside(path, root)):
        raise Refusal("G01-R004", f"{label} must be outside the project root (read-only guarantee).")
    return path


def inspect(args: argparse.Namespace) -> tuple[dict[str, Any], str]:
    report = new_report(args.alias)
    try:
        root = canonical_root(args.project)
        report_path = safe_output_path(args.report, root, "--report")
        evidence_dir = safe_output_path(args.evidence_dir, root, "--evidence-dir")
    except Refusal as refusal:
        report["status"] = "blocked"
        report["errors"].append({"code": refusal.code, "message": refusal.message, "retryable": False})
        report["completed_at"] = now_iso()
        return report, "refused"
    if evidence_dir is not None:
        evidence_dir.mkdir(parents=True, exist_ok=True)
    redact = Redactor([(str(root), args.alias), (str(Path.home()), "~")])

    before = snapshot(root)
    ctx = Context(root=root)
    scenes, sidecars = walk_project(ctx)
    texts: dict[Path, str] = {}
    for path in scenes:
        body = read_text(ctx, path)
        if body is not None:
            texts[path] = body
    build_uid_map(ctx, scenes, sidecars, texts)
    unsafe: list[str] = []
    for path in scenes:
        if path in texts:
            unsafe += check_file(ctx, path, texts[path])
    check_project(ctx)
    static_errors = sum(1 for f in ctx.findings if f["severity"] == "error")
    record_test(report, "static_parse", "scene_doctor.py inspect (static pass)",
                "all .tscn/.tres parsed and references checked", f"{len(ctx.scanned)} file(s), {static_errors} error finding(s)",
                "pass")

    native = "not_requested"
    engine = None
    if args.static_only:
        native = "not_requested"
        record_test(report, "native_validation", "skipped (--static-only)", "native Godot validation", "not run", "skipped")
    else:
        engine = find_engine(args.godot)
        if engine is None:
            native = "no_engine"
            report["errors"].append({"code": "G01-B001", "message": "No Godot executable found (--godot, GODOT_BIN, godot4, godot). Native validation is blocked.", "retryable": True})
            record_test(report, "native_validation", "godot --headless ...", "native Godot validation", "engine unavailable", "skipped")
        elif ctx.symlinks or unsafe:
            native = "unsafe"
            report["errors"].append({"code": "G01-B004", "message": "Native validation refused: the project contains symlinks or unsafe references.", "retryable": False})
            record_test(report, "native_validation", "godot --headless ...", "native Godot validation", "refused for safety", "skipped")
        else:
            report["engine"] = "godot"
            try:
                native = native_validate(ctx, report, engine, args, redact, evidence_dir)
            except OSError as exc:
                native = "error"
                report["errors"].append({"code": "G01-X001", "message": f"Engine execution failed: {exc.strerror}", "retryable": True})

    after = snapshot(root)
    changed = diff_snapshots(before, after)
    record_test(report, "non_destructive", "sha256 of every file under the project root before/after",
                "no file added, removed or changed", f"{len(before)} file(s) before, {len(changed)} difference(s)",
                "pass" if not changed else "fail", ", ".join(changed[:20]))
    if changed:
        report["errors"].append({"code": "G01-X002", "message": "Project files changed during the run (concurrent edit or tool defect). Review the listed paths.", "retryable": False})

    report["findings"] = sorted(ctx.findings, key=lambda f: ({"error": 0, "warning": 1, "info": 2}[f["severity"]], f["file"] or "", f["line"] or 0, f["code"]))
    report["input_hashes"] = dict(sorted(ctx.input_hashes.items()))
    errors = sum(1 for f in ctx.findings if f["severity"] == "error")
    warnings = sum(1 for f in ctx.findings if f["severity"] == "warning")
    supported = report.pop("_engine_supported", False)

    if changed or native == "error":
        status = "error"
    elif native == "timeout":
        status = "error"
        report["errors"].append({"code": "G01-X003", "message": f"Godot did not finish within {args.timeout}s.", "retryable": True})
    elif errors:
        status = "fail"
    elif native == "ok":
        status = "warn" if warnings else "pass"
    elif native == "failed":
        status = "fail"
    elif native in ("no_engine", "blocked"):
        status = "blocked"
    else:
        status = "not_tested"
    report["status"] = status
    report["verified"] = bool(native == "ok" and supported and not changed)
    report["summary"] = {"files_scanned": len(ctx.scanned), "errors": errors, "warnings": warnings,
                         "info": sum(1 for f in ctx.findings if f["severity"] == "info"), "native": native}
    report["completed_at"] = now_iso()
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report, status


def markdown_summary(report: dict[str, Any]) -> str:
    lines = [f"# G01 scene-doctor — {report['status'].upper()}", "",
             f"- Project: `{report['project_root_redacted']}`  • verified: **{str(report['verified']).lower()}**",
             f"- Engine: {report['engine_version'] or 'not run'}"]
    summary = report.get("summary") or {}
    if summary:
        lines.append(f"- Files scanned: {summary.get('files_scanned')} • errors {summary.get('errors')} • warnings {summary.get('warnings')} • native: {summary.get('native')}")
    for err in report["errors"]:
        lines.append(f"- Blocker `{err['code']}`: {err['message']}")
    if report["findings"]:
        lines += ["", "| Code | Severity | Location | Summary |", "|---|---|---|---|"]
        for f in report["findings"]:
            loc = (f["file"] or "-") + (f":{f['line']}" if f.get("line") else "")
            lines.append(f"| {f['code']} | {f['severity']} | `{loc}` | {f['summary'].replace('|', '/')} |")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scene_doctor.py", description="G01 scene-doctor (read-only).")
    sub = parser.add_subparsers(dest="command", required=True)
    insp = sub.add_parser("inspect", help="Analyze a Godot 4 project without modifying it.")
    insp.add_argument("project", help="Path to the authorized project root (contains project.godot).")
    insp.add_argument("--godot", help="Path to the Godot 4 executable (default: $GODOT_BIN, godot4, godot).")
    insp.add_argument("--static-only", action="store_true", help="Skip native Godot validation (status stays not_tested).")
    insp.add_argument("--allow-untested-engine", action="store_true", help="Allow a Godot 4 version other than the tested target; never verified.")
    insp.add_argument("--timeout", type=float, default=180.0, help="Seconds allowed per Godot invocation (default 180).")
    insp.add_argument("--report", help="Write the JSON report to this file (must be outside the project).")
    insp.add_argument("--evidence-dir", help="Write redacted Godot logs here (must be outside the project).")
    insp.add_argument("--alias", default="<project>", help="Logical name used instead of the real project path.")
    insp.add_argument("--format", choices=("json", "markdown"), default="json", help="stdout format.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.timeout <= 0 or args.timeout > 3600:
        print("--timeout must be between 0 and 3600 seconds", file=sys.stderr)
        return EXIT["refused"]
    try:
        report, outcome = inspect(args)
    except Exception as exc:  # emit valid JSON even on internal failure
        report = new_report(args.alias)
        report["errors"].append({"code": "G01-X000", "message": f"Internal error: {type(exc).__name__}", "retryable": False})
        report["completed_at"] = now_iso()
        outcome = "error"
    sys.stdout.write(markdown_summary(report) if args.format == "markdown" else json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return EXIT[outcome]


if __name__ == "__main__":
    raise SystemExit(main())
