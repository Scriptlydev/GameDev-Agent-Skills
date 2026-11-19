"""G07 fake-engine control-flow tests; native evidence is opt-in, never inferred."""
from __future__ import annotations
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/godot/test-runner'
SCRIPT = SKILL / 'scripts/test_runner.py'
FIXTURES = ROOT / 'tests/fixtures/godot/test_runner'
SPEC = importlib.util.spec_from_file_location('g07_test_runner', SCRIPT)
tr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tr)

STUB = r'''#!{python}
import json, os, re, subprocess, sys, time
from pathlib import Path
MODE = {mode!r}
VERSION = {version!r}
a = sys.argv[1:]
if '--version' in a:
    if MODE == 'version_timeout': time.sleep(60)
    print(VERSION)
    sys.exit(5 if MODE == 'bad_version_exit' else 0)
ws = Path(a[a.index('--path') + 1])
assert not (ws / '.git').exists() and not (ws / '.godot').exists()
assert Path(os.environ['HOME']).parent == ws.parent
assert 'GODOT_BIN' not in os.environ and 'SECRET_TEST_VALUE' not in os.environ
if '--import' in a:
    if MODE == 'import_timeout': time.sleep(60)
    if MODE == 'import_crash': sys.exit(7)
    if MODE == 'mutate':
        (ws / 'project.godot').write_text('changed in disposable workspace')
    sys.exit(0)
if MODE == 'crash': sys.exit(9)
if MODE == 'signal': os.kill(os.getpid(), 9)
if MODE == 'timeout':
    subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
    time.sleep(60)
config = json.loads((ws / a[a.index('--') + 1].removeprefix('res://')).read_text())
def emit(kind, value):
    print('G07_TEST_RUNNER ' + kind + ' ' + json.dumps(value), file=sys.stderr, flush=True)
if MODE == 'malformed':
    print('G07_TEST_RUNNER START not-json', file=sys.stderr)
    sys.exit(0)
if MODE == 'leak':
    print(str(ws) + ' ' + os.environ['HOME'] + ' token=synthetic-secret Bearer synthetic-bearer')
    print('x' * 70000)
for file in config['files']:
    text = (ws / file.removeprefix('res://')).read_text()
    if 'this is invalid' in text:
        emit('LOAD_ERROR', file)
        continue
    methods = re.findall(r'^func (test_\w+)\(\):\n(.*?)(?=^func |\Z)', text, re.M | re.S)
    for method, body in sorted(methods):
        identity = file + '::' + method
        if config['filter'] not in identity: continue
        emit('START', identity)
        if MODE == 'pending': continue
        if 'nonexistent_method' in body:
            print('SCRIPT ERROR: Invalid call on null', file=sys.stderr)
            if MODE != 'runtime_end': continue
        result, message = 'pass', ''
        found = re.search(r'return "([^"]*)"', body)
        if found:
            message = found.group(1)
            # The passing fixture has a guarded return for its hook assertion.
            if 'if not ready:' not in body:
                result = 'skipped' if message.startswith('SKIP:') else 'fail'
        if MODE == 'nonstring': result, message = 'fail', 'non-string return'
        if MODE == 'leak': message = str(ws) + ' token=synthetic-secret ' + 'm' * 500
        emit('END', dict(id=identity, result=result, message=message, duration_ms=1.25))
if MODE != 'nodone': print('G07_TEST_RUNNER DONE', file=sys.stderr)
'''


class Base(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='g07-test-')
        self.addCleanup(self.temp.cleanup)
        self.tmp = Path(self.temp.name)

    def stub(self, mode='ok', version='4.5.1.stable.official.fake'):
        path = self.tmp / ('engine-' + mode)
        path.write_text(STUB.format(python=sys.executable, mode=mode, version=version))
        path.chmod(0o755)
        return path

    def cli(self, fixture='passing', mode='ok', version='4.5.1.stable.official.fake', extra=(), project=None, engine=None):
        project = project or FIXTURES / fixture
        engine = engine or self.stub(mode, version)
        cmd = [sys.executable, '-I', str(SCRIPT), 'run', str(project), '--godot', str(engine),
               '--report', str(self.tmp / 'report.json'), '--evidence-dir', str(self.tmp / 'logs'), *extra]
        env = dict(os.environ, SECRET_TEST_VALUE='must-not-reach-engine')
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20, cwd=self.tmp, env=env)
        self.assertTrue(proc.stdout.startswith('{'), proc.stderr)
        report = json.loads(proc.stdout)
        return proc.returncode, report

    def codes(self, report):
        return [f['code'] for f in report['findings'] + report['errors']]

    def copied(self, fixture='passing'):
        project = self.tmp / 'project'
        shutil.copytree(FIXTURES / fixture, project)
        return project


class CliTests(Base):
    def test_fixture_results_and_totals(self):
        matrix = [('passing', 0, 'pass', (3, 0, 0, 0), None),
                  ('failing', 1, 'fail', (1, 1, 0, 0), 'G07-E002'),
                  ('skipped', 0, 'warn', (1, 0, 1, 0), 'G07-W002'),
                  ('parse_error', 1, 'fail', (0, 0, 0, 0), 'G07-E001'),
                  ('runtime_error', 1, 'fail', (1, 0, 0, 1), 'G07-E003'),
                  ('empty', 3, 'not_tested', (0, 0, 0, 0), 'G07-W001')]
        for fixture, expected_rc, status, counts, code in matrix:
            with self.subTest(fixture=fixture):
                rc, rep = self.cli(fixture)
                self.assertEqual((rc, rep['status']), (expected_rc, status))
                self.assertEqual(tuple(rep['summary'][k] for k in ('pass', 'fail', 'skipped', 'error')), counts)
                # Zero collected tests verifies nothing (not_tested is never verified).
                self.assertEqual(rep['verified'], status != 'not_tested')
                self.assertTrue(rep['audit']['unchanged'])
                if code: self.assertIn(code, self.codes(rep))
                self.assertEqual(json.loads((self.tmp / 'report.json').read_text()), rep)
                self.assertEqual(rep['schema_version'], '0.1.0')
                self.assertEqual(rep['skill_id'], 'G07')
                self.assertEqual(len(rep['environment']['engine_binary_sha256']), 64)
                for test in rep['tests']:
                    self.assertEqual(set(test), {'id', 'result', 'message', 'duration_ms'})
                for artifact in rep['artifacts']:
                    self.assertEqual(tr.sha256_file(self.tmp / 'logs' / artifact['path']), artifact['sha256'])

    def test_versions(self):
        for version, flags, code, rc in [
            ('4.7.2.stable.fake', (), 'G07-B003', 3),
            ('4.7.2.stable.fake', ('--allow-untested-engine',), 'G07-W010', 0),
            ('3.6.0.stable.fake', (), 'G07-B002', 3),
            ('garbage', (), 'G07-B002', 3)]:
            with self.subTest(version=version, flags=flags):
                result, rep = self.cli(version=version, extra=flags)
                self.assertEqual(result, rc)
                self.assertFalse(rep['verified'])
                self.assertIn(code, self.codes(rep))
                if flags: self.assertEqual(rep['status'], 'warn')

    def test_engine_failure_paths(self):
        for mode, expected, code in [('crash', 1, 'G07-E004'), ('signal', 1, 'G07-E004'),
                                     ('nodone', 1, 'G07-E004'), ('pending', 1, 'G07-E004'),
                                     ('malformed', 4, 'G07-X001'), ('import_crash', 1, 'G07-E001'),
                                     ('bad_version_exit', 3, 'G07-B002')]:
            with self.subTest(mode=mode):
                rc, rep = self.cli(mode=mode)
                self.assertEqual(rc, expected)
                self.assertIn(code, self.codes(rep))
                if mode != 'import_crash': self.assertFalse(rep['verified'])
                if mode in ('crash', 'signal', 'pending'): self.assertEqual(rep['tests'], [])

    def test_timeouts_include_version_and_import(self):
        for mode in ('timeout', 'version_timeout', 'import_timeout'):
            with self.subTest(mode=mode):
                start = time.monotonic()
                rc, rep = self.cli('crash_or_hang', mode=mode, extra=('--timeout', '0.2'))
                self.assertLess(time.monotonic() - start, 5)
                self.assertEqual(rc, 4)
                self.assertIn('G07-X003', self.codes(rep))
                self.assertFalse(rep['verified'])

    def test_runtime_error_with_end_is_not_passed(self):
        rc, rep = self.cli('runtime_error', mode='runtime_end')
        self.assertEqual(rc, 1)
        self.assertEqual(rep['summary']['error'], 1)
        self.assertEqual(rep['summary']['pass'], 1)

    def test_non_string_return(self):
        rc, rep = self.cli(mode='nonstring')
        self.assertEqual(rc, 1)
        self.assertTrue(all(t['message'] == 'non-string return' for t in rep['tests']))

    def test_filter_and_recursive_sorted_selection(self):
        rc, rep = self.cli(extra=('--filter', '::test_third'))
        self.assertEqual(rc, 0)
        self.assertEqual([t['id'] for t in rep['tests']], ['res://tests/nested/test_beta.gd::test_third'])
        rc, rep = self.cli(extra=('--filter', 'never_matches'))
        self.assertEqual((rc, rep['status']), (3, 'not_tested'))
        self.assertIn('G07-W001', self.codes(rep))

    def test_custom_tests_dir(self):
        project = self.copied()
        (project / 'tests').rename(project / 'checks')
        rc, rep = self.cli(project=project, extra=('--tests-dir', 'res://checks'))
        self.assertEqual(rc, 0)
        self.assertEqual(rep['summary']['pass'], 3)

    def test_no_engine_and_non_executable(self):
        for engine in (self.tmp / 'absent', self.tmp / 'not-executable'):
            if engine.name == 'not-executable': engine.write_text('data')
            rc, rep = self.cli(engine=engine)
            self.assertEqual(rc, 3)
            self.assertIn('G07-B001', self.codes(rep))

    def test_engine_exec_failure(self):
        engine = self.tmp / 'invalid-executable'
        engine.write_text('invalid executable format')
        engine.chmod(0o755)
        rc, rep = self.cli(engine=engine)
        self.assertEqual(rc, 4)
        self.assertIn('G07-X001', self.codes(rep))

    def test_mutation_only_affects_workspace(self):
        project = self.copied()
        (project / 'untracked.txt').write_text('keep me')
        for directory in ('.godot', '.git'):
            (project / directory).mkdir()
            (project / directory / 'keep').write_text('original cache')
        before = tr.snapshot(project)
        rc, rep = self.cli(project=project, mode='mutate')
        self.assertEqual(rc, 0)
        self.assertEqual(tr.snapshot(project), before)
        self.assertTrue(rep['audit']['unchanged'])
        self.assertEqual(rep['audit']['files_before'], len(before))

    def test_clipped_redacted_logs_and_messages(self):
        project = self.copied()
        rc, rep = self.cli(project=project, mode='leak')
        self.assertEqual(rc, 0)
        logs = ''.join(p.read_text() for p in (self.tmp / 'logs').iterdir())
        published = json.dumps(rep) + logs
        for private in (str(project), str(Path.home()), str(self.tmp), 'synthetic-secret', 'synthetic-bearer'):
            self.assertNotIn(private, published)
        self.assertLessEqual((self.tmp / 'logs/tests.log').stat().st_size, 65540)
        self.assertTrue(all(len(t['message']) <= 200 for t in rep['tests']))

    def test_unsafe_roots(self):
        for project, code in [(self.tmp / 'absent', 'G07-R001'), (self.tmp, 'G07-R003'),
                              (Path(Path.cwd().anchor), 'G07-R002')]:
            with self.subTest(code=code):
                rc, rep = self.cli(project=project)
                self.assertEqual(rc, 2)
                self.assertIn(code, self.codes(rep))
        path = self.tmp / 'regular-file'
        path.write_text('not a directory')
        rc, rep = self.cli(project=path)
        self.assertEqual(rc, 2)
        self.assertIn('G07-R001', self.codes(rep))

    def test_unsafe_tests_dirs_and_timeout(self):
        for value in ('res://../x', 'res://tests/../tests', '/tmp', 'https://example.invalid/x',
                      'res:///absolute', 'res://C:/x', 'res://tests\\x', 'res://tests//nested', 'res://'):
            with self.subTest(value=value):
                rc, rep = self.cli('unsafe', extra=('--tests-dir', value))
                self.assertEqual(rc, 2)
                self.assertIn('G07-R005', self.codes(rep))
        for value in ('0', '-1', '901', 'nan', 'inf'):
            with self.subTest(timeout=value):
                rc, rep = self.cli(extra=('--timeout', value))
                self.assertEqual(rc, 2)
                self.assertIn('G07-R006', self.codes(rep))

    def test_output_paths_inside_root_and_symlink_alias(self):
        project = self.copied()
        alias = self.tmp / 'alias'
        alias.symlink_to(project, target_is_directory=True)
        for option, output in [('--report', project / 'report.json'),
                               ('--evidence-dir', project / 'logs'), ('--report', alias / 'report.json'), ('--report', '')]:
            with self.subTest(option=option, output=output):
                before = tr.snapshot(project)
                rc, rep = self.cli(project=project, extra=(option, str(output)))
                self.assertEqual(rc, 2)
                self.assertIn('G07-R004', self.codes(rep))
                self.assertEqual(before, tr.snapshot(project))

    def test_symlinks_refused_even_in_excluded_dirs(self):
        for name in ('file_link', '.godot', '.git'):
            with self.subTest(name=name):
                project = self.tmp / name.replace('.', 'dot')
                shutil.copytree(FIXTURES / 'passing', project)
                (project / name).symlink_to(self.tmp / 'does-not-exist')
                rc, rep = self.cli(project=project)
                self.assertEqual(rc, 3)
                self.assertIn('G07-B004', self.codes(rep))
        project = self.copied('unsafe')
        (project / 'tests').symlink_to(self.tmp, target_is_directory=True)
        rc, rep = self.cli(project=project)
        self.assertEqual(rc, 2)
        self.assertIn('G07-R005', self.codes(rep))

    def test_symlink_project_marker_and_tests_file(self):
        project = self.copied('unsafe')
        marker = project / 'project.godot'
        marker.unlink()
        marker.symlink_to(FIXTURES / 'passing/project.godot')
        rc, rep = self.cli(project=project)
        self.assertEqual(rc, 2)
        self.assertIn('G07-R003', self.codes(rep))
        marker.unlink()
        marker.write_text('config_version=5')
        (project / 'tests').write_text('not a directory')
        rc, rep = self.cli(project=project)
        self.assertEqual(rc, 2)
        self.assertIn('G07-R005', self.codes(rep))

    def test_symlinked_evidence_file_does_not_write_original(self):
        project = self.copied()
        evidence = self.tmp / 'logs'
        evidence.mkdir()
        (evidence / 'version.log').symlink_to(project / 'project.godot')
        before = tr.snapshot(project)
        rc, rep = self.cli(project=project)
        self.assertEqual(rc, 4)
        self.assertIn('G07-X001', self.codes(rep))
        self.assertEqual(before, tr.snapshot(project))


class HelperTests(Base):
    def test_audit_detects_actual_original_mutation(self):
        project = self.copied()
        engine = self.stub()
        args = tr.argparse.Namespace(project=str(project), godot=str(engine), report=str(self.tmp / 'report.json'),
                                    evidence_dir=None, tests_dir='res://tests', filter='', timeout=1,
                                    allow_untested_engine=False)
        def mutate(*args):
            (project / 'untracked-change.txt').write_text('concurrent edit')
            return 'pass', True
        with mock.patch.object(tr, 'native_run', side_effect=mutate):
            report, outcome = tr.run(args)
        self.assertEqual(outcome, 'error')
        self.assertFalse(report['verified'])
        self.assertIn('G07-X002', self.codes(report))
        self.assertIn('untracked-change.txt', report['audit']['changed'])

    def test_empty_and_nul_root_refused(self):
        for value in ('', '\x00'):
            with self.assertRaises(tr.Refusal) as caught:
                tr.canonical_root(value)
            self.assertEqual(caught.exception.code, 'G07-R001')
        with self.assertRaises(tr.Refusal):
            tr.tests_path(self.tmp, 'res://tests\x00')

    def test_isolated_environment(self):
        with mock.patch.dict(os.environ, {'TOKEN': 'not inherited'}):
            env = tr.isolated_env(self.tmp / 'home')
        self.assertNotIn('TOKEN', env)
        for key in ('HOME', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME', 'TMPDIR'):
            self.assertTrue(tr.is_inside(Path(env[key]), self.tmp / 'home'))

    def test_find_engine_precedence_and_fallback(self):
        engine = self.stub()
        with mock.patch.dict(os.environ, {'GODOT_BIN': str(engine)}):
            self.assertEqual(tr.find_engine(None), engine)
            self.assertIsNone(tr.find_engine(str(self.tmp / 'missing')))
        with mock.patch.dict(os.environ, {'GODOT_BIN': ''}), mock.patch.object(tr.shutil, 'which', return_value=str(engine)):
            self.assertEqual(tr.find_engine(None), engine)

    def test_invalid_protocol_is_rejected(self):
        for payload in ({'id': 'a', 'result': 'invented'}, {'id': 'a', 'result': 'pass', 'duration_ms': -1}):
            log = tr.MARK + ' START "a"\n' + tr.MARK + ' END ' + json.dumps(payload)
            with self.assertRaises(ValueError):
                tr.parse_results(tr.new_report('<project>'), log, tr.Redactor([]))

    def test_frontmatter_and_codes_and_stdlib(self):
        text = (SKILL / 'SKILL.md').read_text()
        self.assertTrue(text.startswith('---\nname: test-runner\n'))
        self.assertIn('status: implemented_unverified', text)
        doc = (SKILL / 'references/DIAGNOSTICS.md').read_text()
        for code in set(tr.CODES) | set(re.findall(r'G07-[RBX]\d{3}', SCRIPT.read_text())):
            self.assertIn(code, doc)
        imports = set(re.findall(r'^(?:import|from) ([a-z_]+)', SCRIPT.read_text(), re.M))
        self.assertTrue(imports <= set(sys.stdlib_module_names) | {'__future__'})
        self.assertNotIn('shell=True', SCRIPT.read_text())


@unittest.skipUnless(os.environ.get('GODOT_BIN'), 'GODOT_BIN unset: real Godot 4.5.1 NOT TESTED')
class RealGodotTests(Base):
    def test_passing_native(self):
        before = tr.snapshot(FIXTURES / 'passing')
        rc, report = self.cli(engine=Path(os.environ['GODOT_BIN']))
        self.assertEqual((rc, report['status']), (0, 'pass'))
        self.assertTrue(report['verified'])
        self.assertEqual(report['summary']['pass'], 3)
        self.assertEqual(before, tr.snapshot(FIXTURES / 'passing'))

    def test_failing_native(self):
        rc, report = self.cli('failing', engine=Path(os.environ['GODOT_BIN']))
        self.assertEqual((rc, report['status']), (1, 'fail'))
        self.assertTrue(report['verified'])
        self.assertIn('G07-E002', self.codes(report))
        self.assertEqual(report['summary']['pass'], 1)
        self.assertEqual(report['summary']['fail'], 1)
