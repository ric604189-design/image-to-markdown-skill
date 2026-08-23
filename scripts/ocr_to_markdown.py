from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf"}
API_URL = "https://api.mistral.ai/v1/ocr"
PREREQUISITES_VERSION = 1
PREREQUISITES_PATH = (
    Path.home()
    / ".codex"
    / "state"
    / "image-to-markdown"
    / "prerequisites.json"
)


def prerequisites_confirmed(state_path: Path) -> bool:
    try:
        record = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if (
        not isinstance(record, dict)
        or record.get("version") != PREREQUISITES_VERSION
        or not isinstance(record.get("confirmed_at"), str)
        or not record["confirmed_at"]
    ):
        return False
    try:
        datetime.fromisoformat(record["confirmed_at"])
    except ValueError:
        return False
    return True


def confirm_prerequisites(state_path: Path) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "version": PREREQUISITES_VERSION,
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
    }
    state_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def reset_prerequisites(state_path: Path) -> bool:
    if not state_path.exists():
        return False
    state_path.unlink()
    return True


def natural_key(path: Path) -> list[object]:
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", path.name)
    ]


def collect_inputs(source: Path) -> list[Path]:
    if source.is_file():
        if source.suffix.casefold() not in SUPPORTED_SUFFIXES:
            raise ValueError("Unsupported input type: {}".format(source.suffix))
        return [source]
    if not source.is_dir():
        raise ValueError("Input does not exist: {}".format(source))
    inputs = [
        path
        for path in source.iterdir()
        if path.is_file() and path.suffix.casefold() in SUPPORTED_SUFFIXES
    ]
    if not inputs:
        raise ValueError("No supported images or PDFs found")
    return sorted(inputs, key=natural_key)


def data_url(source: Path) -> str:
    mime_type, _ = mimetypes.guess_type(source.name)
    if mime_type is None:
        raise ValueError("Cannot determine MIME type: {}".format(source.name))
    encoded = base64.b64encode(source.read_bytes()).decode("ascii")
    return "data:{};base64,{}".format(mime_type, encoded)


def submit_document(source: Path, api_key: str) -> str:
    document_type = "document_url" if source.suffix.casefold() == ".pdf" else "image_url"
    payload = {
        "model": "mistral-ocr-latest",
        "document": {"type": document_type, document_type: data_url(source)},
    }
    request = Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer {}".format(api_key), "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError("HTTP {}: {}".format(error.code, detail)) from error
    except URLError as error:
        raise RuntimeError("Network error: {}".format(error.reason)) from error
    pages = body.get("pages")
    if not isinstance(pages, list) or not pages:
        raise RuntimeError("OCR response contains no pages")
    markdown = [
        page.get("markdown")
        for page in pages
        if isinstance(page, dict) and isinstance(page.get("markdown"), str)
    ]
    if not markdown:
        raise RuntimeError("OCR response contains no Markdown")
    return "\n\n".join(markdown)


def process_inputs(
    inputs: Iterable[Path], api_key: str
) -> tuple[list[tuple[Path, str]], list[dict[str, str]]]:
    completed: list[tuple[Path, str]] = []
    errors: list[dict[str, str]] = []
    for source in inputs:
        try:
            completed.append((source, submit_document(source, api_key)))
        except (OSError, RuntimeError, ValueError) as error:
            errors.append({"source": source.name, "error": str(error)})
    return completed, errors


def merge_pages(pages: Iterable[tuple[Path, str]], source_markers: bool) -> str:
    blocks = []
    for source, markdown in pages:
        if source_markers:
            blocks.append("<!-- source: {} -->\n\n{}".format(source.name, markdown.strip()))
        else:
            blocks.append(markdown.strip())
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert images or PDFs to one Markdown file with Mistral OCR."
    )
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--api-key", default=os.environ.get("MISTRAL_API_KEY"))
    parser.add_argument("--omit-source-markers", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check-prerequisites", action="store_true")
    modes.add_argument("--confirm-prerequisites", action="store_true")
    modes.add_argument("--reset-prerequisites", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check_prerequisites:
        if prerequisites_confirmed(PREREQUISITES_PATH):
            print("Prerequisites confirmed.")
            return 0
        print("Prerequisite confirmation is required.", file=sys.stderr)
        return 3
    if args.confirm_prerequisites:
        try:
            confirm_prerequisites(PREREQUISITES_PATH)
        except OSError as error:
            print(str(error), file=sys.stderr)
            return 2
        print(PREREQUISITES_PATH)
        return 0
    if args.reset_prerequisites:
        try:
            removed = reset_prerequisites(PREREQUISITES_PATH)
        except OSError as error:
            print(str(error), file=sys.stderr)
            return 2
        print(
            "Prerequisite confirmation reset."
            if removed
            else "No confirmation record found."
        )
        return 0
    if not args.input or args.output_dir is None:
        print("Input and --output-dir are required for OCR.", file=sys.stderr)
        return 2
    if not prerequisites_confirmed(PREREQUISITES_PATH):
        print(
            "Prerequisite confirmation is required. Confirm before running OCR.",
            file=sys.stderr,
        )
        return 3
    if not args.api_key:
        print(
            "Mistral API key is required. Set MISTRAL_API_KEY or pass --api-key.",
            file=sys.stderr,
        )
        return 2
    try:
        inputs = collect_inputs(args.input)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        output = args.output_dir / "output.md"
        manifest = args.output_dir / "ocr-errors.json"
        if (output.exists() or manifest.exists()) and not args.overwrite:
            raise ValueError(
                "Output files already exist; rerun with --overwrite to replace them"
            )
        completed, errors = process_inputs(inputs, args.api_key)
        if completed:
            output.write_text(
                merge_pages(completed, not args.omit_source_markers), encoding="utf-8"
            )
        if errors:
            manifest.write_text(
                json.dumps({"errors": errors}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(
                "OCR completed with {} failure(s); see {}".format(len(errors), manifest),
                file=sys.stderr,
            )
            return 1
        print(output)
        return 0
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
