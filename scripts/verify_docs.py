#!/usr/bin/env python3
"""Lightweight, dependency-free documentation validation. Does not claim skills work."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs' / 'skill_manifest_planned.json'
EXPECTED = {'godot': 8, 'unity': 8, 'blender': 8, 'universal': 6}
LINK_PATTERN = re.compile(r'(?<!\!)\[[^\]]+\]\(([^)]+)\)')


def check_manifest(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    path = root / 'docs' / 'skill_manifest_planned.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return [f'Manifest cannot be read: {exc}']
    items = data.get('skills')
    if not isinstance(items, list):
        return ['Manifest skills must be a list']
    ids = [item.get('id') for item in items]
    specs = [item.get('spec_path') for item in items]
    names = [item.get('name') for item in items]
    for label, values in [('id', ids), ('spec_path', specs), ('name', names)]:
        if len(values) != len(set(values)):
            errors.append(f'Duplicate {label} in manifest')
    if len(items) != 30:
        errors.append(f'Expected 30 planned skills, found {len(items)}')
    counts = Counter(item.get('collection') for item in items)
    if counts != EXPECTED:
        errors.append(f'Collection totals mismatch: {dict(counts)}')
    for item in items:
        rel = item.get('spec_path', '')
        if not rel or Path(rel).is_absolute() or '..' in Path(rel).parts:
            errors.append(f'Unsafe spec path: {rel}')
        elif not (root / rel).is_file():
            errors.append(f'Missing specification: {rel}')
        status = item.get('status')
        if status == 'implemented_unverified':
            impl = item.get('implementation_path', '')
            if not impl or Path(impl).is_absolute() or '..' in Path(impl).parts or not (root / impl).is_file():
                errors.append(f'Implemented skill {item.get("id")} lacks a valid implementation_path')
        elif status != 'specified_not_implemented':
            # 'verified'/'stable' need native evidence on the target engine; not accepted by this check yet.
            errors.append(f'Unexpected implementation status for {item.get("id")}')
    return errors


def check_local_links(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for file in root.rglob('*.md'):
        if '.git' in file.parts:
            continue
        body = file.read_text(encoding='utf-8')
        for ref in LINK_PATTERN.findall(body):
            target = ref.strip().split(' ', 1)[0].strip('<>')
            if not target or target.startswith(('#', 'https://', 'http://', 'mailto:')):
                continue
            target = unquote(target.split('#')[0])
            if not target:
                continue
            resolved = (file.parent / target).resolve()
            if not resolved.is_relative_to(root.resolve()):
                errors.append(f'{file.relative_to(root)}: link escapes repository: {target}')
            elif not resolved.exists():
                errors.append(f'{file.relative_to(root)}: missing target {target}')
    return errors


def main() -> int:
    errors = check_manifest() + check_local_links()
    for error in errors:
        print(f'ERROR: {error}', file=sys.stderr)
    if errors:
        print(f'{len(errors)} documentation issue(s) found.', file=sys.stderr)
        return 1
    print('PASS: manifest and local documentation links validated. No skill is marked verified or stable.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
