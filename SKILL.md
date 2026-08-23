---
name: image-to-markdown
description: Convert an ordered folder of images, an image, or a PDF into one faithful Markdown document using Mistral OCR. Use when the user wants OCR transcription and structure preservation, not summarization or rewriting.
---

# Image to Markdown

Use this skill to faithfully transcribe screenshots, scanned pages, or PDFs.
Preserve the OCR provider's Markdown; do not correct, complete, summarize,
translate, or infer text.

Before the first OCR run, execute the following command from this skill
directory:

    python3 scripts/ocr_to_markdown.py --check-prerequisites

If it exits 3, ask the user once: "Do you confirm that you have a usable
Mistral API account and sufficient balance for this OCR task?" Do not request
or expose an API key in that question. Only after an affirmative answer,
execute:

    python3 scripts/ocr_to_markdown.py --confirm-prerequisites

This writes only a confirmation timestamp and schema version to the local
Codex state directory. When the status command exits 0, skip this
account-and-balance question on future uses. Users can require confirmation
again with:

    python3 scripts/ocr_to_markdown.py --reset-prerequisites

Before submitting content, confirm that the user permits uploading it to Mistral
unless that permission is already explicit. Explain that Mistral OCR is an
external service. Do not print the API key or image/PDF content.

1. Confirm the input path and output directory. Sort folders naturally by
   filename; PDFs retain their returned page order.
2. Require MISTRAL_API_KEY or a user-provided --api-key; never store it in a
   project file.
3. Run scripts/ocr_to_markdown.py INPUT --output-dir OUTPUT_DIR from this
   skill directory. Add --omit-source-markers only when the user asks for a
   clean merged document; otherwise retain markers for traceability.
4. Do not overwrite existing output without the user's confirmation; use
   --overwrite only after that confirmation.
5. If the process exits 1, return the completed output.md and explain that
   ocr-errors.json lists failed items. If it exits 2, resolve the input,
   credential, or output-path problem before retrying.
6. State that the result is an OCR transcription and direct the user to source
   markers or the original inputs for verification of doubtful text.
