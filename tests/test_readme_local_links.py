"""Regression tests for README repository-local link integrity."""
import tempfile
import unittest
from pathlib import Path
from scripts.check_readme_local_links import broken_local_links


class LocalMarkdownLinkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.doc = self.root / "README.md"
        (self.root / "assets").mkdir()
        (self.root / "assets" / "hero vector.svg").write_text("<svg/>", encoding="utf-8")
        (self.root / "docs").mkdir()

    def test_existing_file_and_directory(self):
        content = "![hero](assets/hero%20vector.svg) [docs](docs/)"
        self.assertEqual(broken_local_links(content, self.doc, self.root), [])

    def test_external_and_fragment_destinations_are_excluded(self):
        content = "[upstream](https://example.com/a) [mail](mailto:a@b.c) [heading](#intro)"
        self.assertEqual(broken_local_links(content, self.doc, self.root), [])

    def test_nonexistent_relative_path_fails(self):
        result = broken_local_links("[bad](docs/missing.md)", self.doc, self.root)
        self.assertEqual(result, ["missing local target: docs/missing.md"])

    def test_escape_outside_repo_fails(self):
        result = broken_local_links("[unsafe](../outside.md)", self.doc, self.root)
        self.assertEqual(result, ["link escapes repository: ../outside.md"])

    def test_nonfile_uri_and_absolute_path_fail(self):
        result = broken_local_links("[unsafe](file:///etc/passwd) [absolute](/etc/passwd)", self.doc, self.root)
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
