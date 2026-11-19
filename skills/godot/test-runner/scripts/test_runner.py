#!/usr/bin/env python3
"""G07 built-in Godot test runner. Stdlib only; native tests run on a copy.

Safety/report helpers copied from G01 (same repository, MIT); no G01 import.
"""
from __future__ import annotations
import argparse
import datetime as _dt
import hashlib
import json
import math
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"
SKILL_ID = "G07"
TOOL_VERSION = "0.1.0"
EVIDENCE_LIMIT = 200
VERSION_RE = re.compile(r"^(\d+)\.(\d+)(?:\.(\d+))?\.([a-z0-9_]+)")
MARK = "G07_TEST_RUNNER"
EXIT = {"pass": 0, "warn": 0, "fail": 1, "refused": 2, "blocked": 3, "not_tested": 3, "error": 4}
CHECK_SCRIPT = Path(__file__).with_name("g07_runner.gd")

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


def canonical_root(raw: str) -> Path:
    if not raw or "\x00" in raw:
        raise Refusal("G07-R001", "Project root is empty or contains a NUL byte.")
    candidate = Path(raw).expanduser()
    try:
        root = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        raise Refusal("G07-R001", "Project root does not exist or cannot be resolved.") from None
    if not root.is_dir():
        raise Refusal("G07-R001", "Project root is not a directory.")
    if root == Path(root.anchor):
        raise Refusal("G07-R002", "Refusing to analyze a filesystem root.")
    marker = root / "project.godot"
    if marker.is_symlink() or not marker.is_file():
        raise Refusal("G07-R003", "No regular project.godot file at the project root; not a Godot project.")
    return root


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


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
    # Keep stdout separate: an unterminated project print must not corrupt stderr markers.
    # File-backed capture bounds RAM even when a test floods output.
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                proc.kill()
            proc.wait()
            rc = None
        stdout.seek(0)
        stderr.seek(0)
        out = stdout.read(2 * 1024 * 1024).decode('utf-8', errors='replace')
        err = stderr.read(2 * 1024 * 1024).decode('utf-8', errors='replace')
        return rc, out + '\n' + err


def parse_version(text: str) -> tuple[str | None, tuple[int, int, int] | None]:
    for raw in text.splitlines():
        match = VERSION_RE.match(raw.strip())
        if match:
            major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3) or 0)
            return raw.strip(), (major, minor, patch)
    return None, None


def isolated_env(home: Path) -> dict[str, str]:
    home.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k in ("PATH", "LANG", "LC_ALL", "TZ")}
    env.update({"HOME": str(home), "XDG_CONFIG_HOME": str(home / "config"), "XDG_DATA_HOME": str(home / "data"),
                "XDG_CACHE_HOME": str(home / "cache"), "TMPDIR": str(home / "tmp")})
    (home / "tmp").mkdir(exist_ok=True)
    return env


def save_log(report: dict[str, Any], evidence_dir: Path | None, name: str, text: str, purpose: str) -> None:
    if evidence_dir is None:
        return
    target = evidence_dir / name
    if target.is_symlink():
        raise OSError("Refusing symlinked evidence file")
    target.write_text(text, encoding="utf-8")
    report["artifacts"].append({"path": name, "purpose": purpose, "sha256": sha256_file(target), "privacy": "redacted"})


def new_report(alias: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION, "run_id": "g07-" + uuid.uuid4().hex[:12], "skill_id": SKILL_ID,
        "status": "error", "verified": False, "engine": "godot", "engine_version": None,
        "project_root_redacted": alias, "started_at": now_iso(), "completed_at": None,
        "input_hashes": {}, "findings": [], "actions": [], "tests": [], "artifacts": [],
        "rollback": {"available": False, "verified": False, "reason": "read-only inspection; nothing to roll back"},
        "errors": [],
        "tool": {"name": "godot-test-runner", "version": TOOL_VERSION, "mode": "run", "read_only": True},
        "environment": {"os": platform.system(), "os_release": platform.release(),
                        "python": platform.python_version(), "engine_binary_sha256": None},
        "summary": {},
    }


def safe_output_path(raw: str | None, root: Path | None, label: str) -> Path | None:
    if not raw:
        return None
    path = Path(raw).expanduser().resolve()
    if root is not None and (path == root or is_inside(path, root)):
        raise Refusal("G07-R004", f"{label} must be outside the project root (read-only guarantee).")
    return path


CODES = {
    'G07-E001': 'test_script_load_failed', 'G07-E002': 'test_failed',
    'G07-E003': 'test_runtime_error', 'G07-E004': 'engine_crash',
    'G07-W001': 'no_tests_collected', 'G07-W002': 'test_skipped',
    'G07-W010': 'untested_engine_version',
}


def finding(report, code, file=None, message=''):
    report['findings'].append({'code': code, 'severity': 'warning' if '-W' in code else 'error',
                               'summary': CODES[code], 'file': file, 'line': None,
                               'evidence': clip(message)})


def error(report, code, message):
    report['errors'].append({'code': code, 'message': message, 'retryable': False})


def tests_path(root: Path, raw: str) -> Path:
    rel = raw.removeprefix('res://')
    if (not raw.startswith('res://') or not rel or '\\' in rel or '\x00' in rel
            or ':' in rel or rel.startswith('/') or any(p in ('..', '.', '') for p in rel.split('/'))):
        raise Refusal('G07-R005', 'Unsafe tests directory; use res:// followed by an in-project directory.')
    path = root / rel
    if any(p.is_symlink() for p in [path, *path.parents] if is_inside(p, root)):
        raise Refusal('G07-R005', 'Symlinked tests directory refused.')
    if path.exists() and not path.is_dir():
        raise Refusal('G07-R005', 'Tests directory is not a directory.')
    return path


def clean_text(value: str, redact: Redactor) -> str:
    value = redact(value)
    value = re.sub(r'(?i)\b(token|password|secret|api[_-]?key)(\s*[=:]\s*)[^\s,;]+',
                   r'\1\2<redacted>', value)
    return re.sub(r'(?i)\bBearer\s+\S+', 'Bearer <redacted>', value)


def parse_results(report, log: str, redact: Redactor) -> bool:
    """Markers share stderr with engine errors, retaining their relative order.

    A runtime error may abort the test before END, or return null to its caller.
    In either case an active SCRIPT ERROR takes precedence over a null result.
    """
    active = None
    runtime = False
    done = False
    incomplete = False
    seen = set()

    def finish(item=None):
        nonlocal active, runtime, incomplete
        if active is None:
            return
        if item is None and not runtime:
            incomplete = True
            active = None
            return
        result = 'error' if runtime or item is None else item.get('result')
        if result not in ('pass', 'fail', 'skipped', 'error'):
            raise ValueError('Invalid test result')
        message = 'GDScript runtime error' if runtime else ('Missing END marker' if item is None else item.get('message', ''))
        duration = 0 if item is None else item.get('duration_ms', 0)
        if not isinstance(message, str) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration < 0:
            raise ValueError('Invalid test result fields')
        report['tests'].append({'id': clip(clean_text(active, redact), 1000), 'result': result,
                                'message': clip(clean_text(message, redact)), 'duration_ms': duration})
        code = {'fail': 'G07-E002', 'error': 'G07-E003', 'skipped': 'G07-W002'}.get(result)
        if code:
            finding(report, code, clip(clean_text(active.split('::')[0], redact), 1000),
                    clip(clean_text(message, redact)))
        active, runtime = None, False

    for raw in log.splitlines():
        line = raw.strip()
        if line.startswith(MARK + ' START '):
            finish()
            item = json.loads(line.split(' START ', 1)[1])
            if not isinstance(item, str) or item in seen:
                raise ValueError('Invalid or duplicate test id')
            seen.add(item)
            active = item
        elif line.startswith('SCRIPT ERROR:') and active is not None:
            runtime = True
        elif line.startswith(MARK + ' END '):
            item = json.loads(line.split(' END ', 1)[1])
            if not isinstance(item, dict) or item.get('id') != active or active is None:
                raise ValueError('Unmatched test END')
            finish(item)
        elif line.startswith(MARK + ' LOAD_ERROR '):
            path = json.loads(line.split(' LOAD_ERROR ', 1)[1])
            if not isinstance(path, str):
                raise ValueError('Invalid load error')
            finding(report, 'G07-E001', clip(clean_text(path, redact), 1000))
        elif line == MARK + ' DONE':
            finish()
            done = True
    finish()
    return done and not incomplete


def native_run(report, root, files, engine, args, evidence, redact):
    with tempfile.TemporaryDirectory(prefix='g07-work-') as temporary:
        work = Path(temporary)
        redact.pairs.insert(0, (str(work), '<workdir>'))
        redact.pairs.insert(0, (str(engine), '<godot>'))
        env = isolated_env(work / 'home')

        def invoke(cmd, name, cwd):
            report['actions'].append({'tool': [clean_text(s, redact) for s in cmd],
                                      'intent': name, 'approved': True,
                                      'target': 'disposable workspace', 'changed_files': []})
            rc, log = run_engine(cmd, env, cwd, args.timeout)
            save_log(report, evidence, name + '.log', clip(clean_text(log, redact), 65536), name)
            if rc is None:
                error(report, 'G07-X003', 'Engine timeout; process group killed.')
            return rc, log

        rc, out = invoke([str(engine), '--headless', '--version'], 'version', work)
        if rc is None:
            return 'error', False
        version_text, version = parse_version(out)
        report['engine_version'] = clip(clean_text(version_text, redact)) if version_text else None
        report['environment']['engine_binary_sha256'] = sha256_file(engine)
        if rc != 0 or not version or version[0] != 4:
            error(report, 'G07-B002', 'Engine did not identify itself as Godot 4.')
            return 'blocked', False
        supported = version == (4, 5, 1)
        if not supported:
            if not args.allow_untested_engine:
                error(report, 'G07-B003', 'Untested engine version; explicit opt-in required.')
                return 'blocked', False
            finding(report, 'G07-W010')

        ws = work / 'project'
        shutil.copytree(root, ws, symlinks=True, ignore=shutil.ignore_patterns('.godot', '.git'))
        # Random names avoid overwriting even a synthetic project-owned runner.
        token = uuid.uuid4().hex
        runner = '__g07_' + token + '.gd'
        config = '__g07_' + token + '.json'
        shutil.copyfile(CHECK_SCRIPT, ws / runner)
        (ws / config).write_text(json.dumps({'files': files, 'filter': args.filter}), encoding='utf-8')
        rc, _ = invoke([str(engine), '--headless', '--path', str(ws), '--import'], 'import', ws)
        if rc is None:
            return 'error', False
        if rc != 0:
            finding(report, 'G07-E001', message='Project import failed; see import.log.')
        cmd = [str(engine), '--headless', '--path', str(ws), '--script', 'res://' + runner, '--', 'res://' + config]
        rc, log = invoke(cmd, 'tests', ws)
        try:
            done = parse_results(report, log, redact)
        except (ValueError, TypeError):
            error(report, 'G07-X001', 'Malformed native runner protocol.')
            return 'error', False
        if rc is None:
            return 'error', False
        if rc != 0 or not done:
            finding(report, 'G07-E004', message='Nonzero engine exit or missing DONE marker.')
            return 'fail', False
        if any(f['severity'] == 'error' for f in report['findings']):
            return 'fail', supported
        if not report['tests']:
            finding(report, 'G07-W001')
            return 'not_tested', supported
        return ('warn' if report['findings'] else 'pass'), supported


def run(args):
    report = new_report('<project>')
    outcome = 'error'
    report_path = None
    try:
        if not math.isfinite(args.timeout) or not 0 < args.timeout <= 900:
            raise Refusal('G07-R006', 'Timeout must be finite, greater than 0 and at most 900 seconds.')
        root = canonical_root(args.project)
        report_path = safe_output_path(args.report, root, '--report')
        if report_path is None:
            raise Refusal('G07-R004', 'Report output path must not be empty.')
        evidence = safe_output_path(args.evidence_dir, root, '--evidence-dir')
        directory = tests_path(root, args.tests_dir)
    except (Refusal, OSError, ValueError, RuntimeError) as exc:
        error(report, getattr(exc, 'code', 'G07-R004'), getattr(exc, 'message', 'Invalid output path.'))
        report['status'] = 'blocked'
        report['completed_at'] = now_iso()
        return report, 'refused'

    redact = Redactor([(str(root), '<project>'), (str(Path.home()), '<home>')])
    before = snapshot(root)
    try:
        if any(v.startswith('symlink:') for v in before.values()):
            error(report, 'G07-B004', 'Project contains symlinks; native run refused.')
            outcome = 'blocked'
        elif any(v.startswith('unreadable:') for v in before.values()):
            error(report, 'G07-X001', 'Project audit could not read every file.')
        else:
            files = sorted('res://' + p.relative_to(root).as_posix() for p in directory.rglob('test_*.gd')
                           if p.is_file() and not any(n in ('.godot', '.git') for n in p.relative_to(root).parts))
            engine = find_engine(args.godot)
            if engine is None:
                error(report, 'G07-B001', 'No Godot executable found.')
                outcome = 'blocked'
            else:
                if evidence is not None:
                    evidence.mkdir(parents=True, exist_ok=True)
                outcome, verified = native_run(report, root, files, engine, args, evidence, redact)
                report['verified'] = verified
    except (OSError, ValueError, shutil.Error):
        error(report, 'G07-X001', 'Engine execution or workspace setup failed.')
        outcome = 'error'
    finally:
        after = snapshot(root)
        changed = diff_snapshots(before, after)
        report['audit'] = {'files_before': len(before), 'files_after': len(after),
                           'changed': [clip(clean_text(p, redact), 1000) for p in changed], 'unchanged': not changed}
        report['input_hashes'] = {clean_text(k, redact): v for k, v in before.items() if re.fullmatch('[0-9a-f]{64}', v)}
        if changed:
            error(report, 'G07-X002', 'Original project changed during execution.')
            outcome = 'error'
        if outcome in ('error', 'not_tested', 'blocked') or changed:
            report['verified'] = False
    report['status'] = outcome
    report['summary'] = {key: sum(t['result'] == key for t in report['tests']) for key in ('pass', 'fail', 'skipped', 'error')}
    report['summary']['total'] = len(report['tests'])
    report['completed_at'] = now_iso()
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    except OSError:
        error(report, 'G07-X001', 'Could not write report outside project.')
        report['status'] = outcome = 'error'
        report['verified'] = False
    return report, outcome


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    cmd = sub.add_parser('run')
    cmd.add_argument('project')
    cmd.add_argument('--godot')
    cmd.add_argument('--allow-untested-engine', action='store_true')
    cmd.add_argument('--tests-dir', default='res://tests')
    cmd.add_argument('--filter', default='')
    cmd.add_argument('--timeout', type=float, default=120)
    cmd.add_argument('--report', required=True)
    cmd.add_argument('--evidence-dir')
    report, outcome = run(parser.parse_args(argv))
    print(json.dumps(report, indent=2))
    return EXIT[outcome]


if __name__ == '__main__':
    raise SystemExit(main())
