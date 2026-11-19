"""Static documentation checks only; no runtime skill functionality is claimed."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('verify_docs', ROOT / 'scripts' / 'verify_docs.py')
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


class DocumentationIntegrityTests(unittest.TestCase):
    def test_manifest(self):
        self.assertEqual(module.check_manifest(), [])

    def test_local_links(self):
        self.assertEqual(module.check_local_links(), [])


if __name__ == '__main__':
    unittest.main()
