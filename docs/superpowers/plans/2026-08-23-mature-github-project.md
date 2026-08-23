# Mature GitHub Project Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development
(recommended) or executing-plans to implement this plan task-by-task. Steps use
checkbox (- [ ]) syntax for tracking.

**Goal:** Package Image to Markdown as a maintainable public open-source
repository without changing its zero-dependency OCR behavior.

**Architecture:** Root documentation explains use, privacy, and maintenance;
GitHub configuration handles contributor intake and offline CI. The existing
Skill and Python script remain the product source of truth.

**Tech Stack:** Markdown, YAML, GitHub Actions, Python standard-library
unittest, and the Codex Skill validator.

---

## File Structure

- README.md — project overview, install, configuration, use, and privacy.
- LICENSE — MIT license.
- CHANGELOG.md — release history.
- CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md — project governance.
- .github/workflows/test.yml — no-secret CI checks.
- .github/ISSUE_TEMPLATE/ and .github/pull_request_template.md — contribution
  templates.

### Task 1: Add public documentation

**Files:**
- Create: README.md
- Create: LICENSE
- Create: CHANGELOG.md

- [ ] **Step 1: Create README.md with this content**

~~~markdown
# Image to Markdown

Faithfully convert an ordered folder of images, a single image, or a PDF into
one traceable Markdown document using Mistral OCR.

Image to Markdown is a zero-dependency Python utility packaged as a Codex
Skill. It preserves provider Markdown and does not summarize, translate,
correct, or infer text.

## Features

- Natural filename ordering for image folders and retained PDF page order.
- Markdown output with source markers for auditability.
- Partial-success output with a machine-readable error manifest.
- No third-party Python dependencies.

## Privacy

OCR requests upload the selected images or PDF to Mistral, an external service.
Use it only when you are authorized to upload that material. The tool does not
store API keys or print them in its output.

## Install as a Codex Skill

Clone this repository into your Codex skills directory:

    git clone https://github.com/ric604189-design/image-to-markdown-skill.git \
      ~/.codex/skills/image-to-markdown

Invoke it in Codex as image-to-markdown.

## Configure and use

Export a Mistral API key only in the shell session that runs OCR:

    export MISTRAL_API_KEY="your-key"

From the repository root:

    python3 scripts/ocr_to_markdown.py ./screenshots --output-dir ./output

Supported input is PNG, JPG, JPEG, WEBP, GIF, and PDF. The command writes
output.md and source markers by default. Use --omit-source-markers only when a
clean merged document is required.

On item-level failures it retains completed output, writes ocr-errors.json, and
exits with status 1. It exits with status 2 for invalid input, missing
credentials, or a protected existing output path.

## Development

    python3 -B -m unittest discover -s tests -t . -v
    python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .

Read CONTRIBUTING.md, SECURITY.md, and CHANGELOG.md before contributing.

## License

MIT. See LICENSE.
~~~

- [ ] **Step 2: Create LICENSE with the standard MIT text**

~~~text
MIT License

Copyright (c) 2026 ric604189-design

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
~~~

- [ ] **Step 3: Create CHANGELOG.md**

~~~markdown
# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog and this project uses semantic versioning.

## [Unreleased]

## [0.1.0] - 2026-08-23

### Added

- Mistral OCR conversion for ordered images and PDFs.
- Traceable merged Markdown output and partial-failure manifest.
- Offline unit tests and Codex Skill metadata.
~~~

- [ ] **Step 4: Verify public documentation**

Run: rg -n "MISTRAL_API_KEY|ocr_to_markdown.py|CONTRIBUTING.md|SECURITY.md|CHANGELOG.md" README.md

Expected: The README contains configuration, command usage, and governance
links.

### Task 2: Add governance and contribution templates

**Files:**
- Create: CONTRIBUTING.md
- Create: CODE_OF_CONDUCT.md
- Create: SECURITY.md
- Create: .github/ISSUE_TEMPLATE/bug_report.yml
- Create: .github/ISSUE_TEMPLATE/feature_request.yml
- Create: .github/pull_request_template.md

- [ ] **Step 1: Create governance documents**

~~~markdown
<!-- CONTRIBUTING.md -->
# Contributing

Keep the project zero-dependency unless a change genuinely requires otherwise.
Never commit API keys, private images, PDFs, or OCR output. Preserve faithful
transcription; summarization, translation, and inferred corrections are outside
scope.

Before a pull request, run:

    python3 -B -m unittest discover -s tests -t . -v
    python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .

Explain behavior changes, tests, and external-service impact. Update
CHANGELOG.md for user-visible changes.

<!-- CODE_OF_CONDUCT.md -->
# Code of Conduct

Participants must contribute respectfully, protect private information, and
focus discussion on evidence and the work. Harassment, discrimination, threats,
deliberate disruption, and publication of private information are unacceptable.

Report conduct concerns privately through the route in SECURITY.md. Maintainers
may remove content or participation when necessary to protect the community.

<!-- SECURITY.md -->
# Security Policy

Security fixes apply to the latest main branch.

Do not open a public issue for a suspected vulnerability or credential exposure.
Use GitHub private vulnerability reporting. If it is unavailable, contact the
repository owner privately through GitHub. Include revision, safe reproduction
steps, impact, and mitigation; never attach keys or private OCR material.
~~~

- [ ] **Step 2: Create issue and pull-request templates**

~~~yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug report
description: Report a reproducible problem without uploading private OCR input.
title: "[Bug]: "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: "Do not include API keys, private documents, or OCR output."
  - type: input
    id: revision
    attributes:
      label: Revision or release
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: Reproduction steps
      description: Use a sanitized fixture or describe the input shape.
    validations:
      required: true

# .github/ISSUE_TEMPLATE/feature_request.yml
name: Feature request
description: Propose a focused Skill or OCR workflow improvement.
title: "[Feature]: "
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem to solve
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: Proposed behavior
    validations:
      required: true

# .github/pull_request_template.md
## Summary

## Verification

- [ ] Offline unit tests pass.
- [ ] Skill validator passes.
- [ ] No API key, private input, or OCR output was committed.
- [ ] CHANGELOG.md is updated when the change affects users.
~~~

- [ ] **Step 3: Verify privacy guidance**

Run: rg -n "API keys|private|Reproduction|Offline unit tests" CONTRIBUTING.md SECURITY.md .github

Expected: Governance and templates all provide privacy or verification guidance.

### Task 3: Add offline continuous integration

**Files:**
- Create: .github/workflows/test.yml

- [ ] **Step 1: Create the CI workflow**

~~~yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  test-python-311:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -B -m unittest discover -s tests -t . -v
      - run: python -c "from pathlib import Path; assert 'TO' + 'DO' not in Path('SKILL.md').read_text()"
  test-python-312:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -B -m unittest discover -s tests -t . -v
  test-python-313:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: python -B -m unittest discover -s tests -t . -v
  test-python-314:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
      - run: python -B -m unittest discover -s tests -t . -v
~~~

- [ ] **Step 2: Confirm no credentials or outbound commands are configured**

Run: rg -n "MISTRAL_API_KEY|api-key|curl|wget|gh " .github/workflows/test.yml

Expected: No matches.

### Task 4: Set repository metadata and complete verification

**Files:**
- Modify: GitHub repository ric604189-design/image-to-markdown-skill metadata

- [ ] **Step 1: Set repository description and topics**

Run:

    gh repo edit ric604189-design/image-to-markdown-skill \
      --description "Faithful image and PDF OCR to traceable Markdown with Mistral OCR." \
      --add-topic codex-skill --add-topic ocr --add-topic markdown \
      --add-topic mistral-ocr --add-topic document-processing --enable-issues

Expected: Public repository metadata identifies the Codex-Skill OCR use case.

- [ ] **Step 2: Run final offline checks**

Run:

    python3 -B -m unittest discover -s tests -t . -v
    python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
    git diff --check
    rg -n --hidden --glob '!.git/**' 'ghp_|github_pat_|MISTRAL_API_KEY=.*[A-Za-z0-9]' .

Expected: Tests and validation pass, whitespace checks are clean, and the
credential-pattern search finds no committed secret.

- [ ] **Step 3: Commit, push, and verify GitHub metadata**

Run:

    git add README.md LICENSE CHANGELOG.md CONTRIBUTING.md CODE_OF_CONDUCT.md \
      SECURITY.md .github
    git commit -m "docs: package project for open-source collaboration"
    git push origin HEAD
    gh repo view ric604189-design/image-to-markdown-skill \
      --json description,repositoryTopics,hasIssuesEnabled,visibility,url

Expected: The current branch is pushed and the public repository exposes the
description, five topics, and enabled Issues.
