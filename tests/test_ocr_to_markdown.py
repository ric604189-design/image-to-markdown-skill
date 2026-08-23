import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts.ocr_to_markdown import (
    PREREQUISITES_VERSION,
    collect_inputs,
    confirm_prerequisites,
    main,
    merge_pages,
    prerequisites_confirmed,
    process_inputs,
    reset_prerequisites,
)


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


class PrerequisiteTests(unittest.TestCase):
    def run_mode(self, arguments, state_path):
        with (
            patch("scripts.ocr_to_markdown.PREREQUISITES_PATH", state_path),
            patch.object(sys, "argv", ["ocr_to_markdown.py", *arguments]),
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()),
        ):
            return main()

    def test_absent_state_is_unconfirmed(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertFalse(prerequisites_confirmed(Path(directory) / "state.json"))

    def test_malformed_state_is_unconfirmed(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text("{", encoding="utf-8")
            self.assertFalse(prerequisites_confirmed(state_path))

    def test_invalid_timestamp_is_unconfirmed(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text(
                '{"version": 1, "confirmed_at": "not-a-timestamp"}',
                encoding="utf-8",
            )
            self.assertFalse(prerequisites_confirmed(state_path))

    def test_confirmation_records_only_version_and_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            confirm_prerequisites(state_path)
            record = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(set(record), {"version", "confirmed_at"})
            self.assertEqual(record["version"], PREREQUISITES_VERSION)
            self.assertTrue(record["confirmed_at"])
            self.assertTrue(prerequisites_confirmed(state_path))

    def test_reset_removes_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            confirm_prerequisites(state_path)
            self.assertTrue(reset_prerequisites(state_path))
            self.assertFalse(state_path.exists())
            self.assertFalse(reset_prerequisites(state_path))

    def test_cli_modes_confirm_check_and_reset_without_api_key(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            self.assertEqual(
                self.run_mode(["--check-prerequisites"], state_path), 3
            )
            self.assertEqual(
                self.run_mode(["--confirm-prerequisites"], state_path), 0
            )
            self.assertEqual(
                self.run_mode(["--check-prerequisites"], state_path), 0
            )
            self.assertEqual(
                self.run_mode(["--reset-prerequisites"], state_path), 0
            )
            self.assertEqual(
                self.run_mode(["--check-prerequisites"], state_path), 3
            )

    def test_ocr_mode_requires_confirmation_before_api_key_or_input_access(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            self.assertEqual(
                self.run_mode(
                    [
                        "not-read.png",
                        "--output-dir",
                        directory,
                        "--api-key",
                        "test-key",
                    ],
                    state_path,
                ),
                3,
            )


if __name__ == "__main__":
    unittest.main()
