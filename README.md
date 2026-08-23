# Image to Markdown

Faithfully convert an ordered folder of images, a single image, or a PDF into
one traceable Markdown document using Mistral OCR.

Image to Markdown is a zero-dependency Python utility packaged as a Codex
Skill. It preserves the OCR provider's Markdown and does not summarize,
translate, correct, or infer text.

## Features

- Natural filename ordering for image folders and preserved page order for PDFs.
- Markdown output with optional source markers for auditability.
- Partial-success output with a machine-readable error manifest.
- No third-party Python dependencies.
- Offline tests that do not require a Mistral API key.

## Privacy

OCR requests upload the selected images or PDF to Mistral, an external service.
Use this tool only when you are authorized to upload that material. The tool
does not store API keys or print them in its output.

## Install as a Codex Skill

Clone the repository into your Codex skills directory:

    git clone https://github.com/ric604189-design/image-to-markdown-skill.git \
      ~/.codex/skills/image-to-markdown

Invoke it in Codex as image-to-markdown.

## Configure

Create a Mistral API key, then export it only in the shell session that runs
OCR:

    export MISTRAL_API_KEY="your-key"

Do not commit a key or place it in a project file.

## Use

From the repository root:

    python3 scripts/ocr_to_markdown.py ./screenshots --output-dir ./output

Supported input is PNG, JPG, JPEG, WEBP, GIF, and PDF. The command writes
output.md and includes a source marker before each processed input by default.
Use --omit-source-markers only when a clean merged document is required.

If one or more items fail, the command retains completed output, writes
ocr-errors.json, and exits with status 1. It exits with status 2 for invalid
input, missing credentials, or a protected existing output path.

## Development

Run the offline test suite and validate the Skill:

    python3 -B -m unittest discover -s tests -t . -v
    python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .

Read CONTRIBUTING.md before contributing, SECURITY.md to report vulnerabilities,
and CHANGELOG.md for release history.

## License

MIT. See LICENSE.
