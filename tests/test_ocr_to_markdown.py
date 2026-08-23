import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ocr_to_markdown import collect_inputs, merge_pages, process_inputs


class OcrToMarkdownTests(unittest.TestCase):
    def test_collect_inputs_uses_natural_filename_order(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("page-10.png", "page-2.png", "page-1.png", "notes.txt"):
                (root / name).write_bytes(b"x")
            self.assertEqual(
                [path.name for path in collect_inputs(root)],
                ["page-1.png", "page-2.png", "page-10.png"],
            )

    def test_merge_pages_adds_source_markers(self):
        result = merge_pages(
            [(Path("page-1.png"), "# One"), (Path("page-2.png"), "Two")],
            source_markers=True,
        )
        self.assertEqual(
            result,
            "<!-- source: page-1.png -->\n\n# One\n\n<!-- source: page-2.png -->\n\nTwo\n",
        )

    @patch("scripts.ocr_to_markdown.submit_document")
    def test_process_inputs_preserves_completed_items_and_errors(self, submit_document):
        submit_document.side_effect = ["First", RuntimeError("HTTP 429")]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = root / "1.png", root / "2.png"
            first.write_bytes(b"a")
            second.write_bytes(b"b")
            completed, errors = process_inputs([first, second], "secret")
        self.assertEqual(completed, [(first, "First")])
        self.assertEqual(errors, [{"source": "2.png", "error": "HTTP 429"}])


if __name__ == "__main__":
    unittest.main()
