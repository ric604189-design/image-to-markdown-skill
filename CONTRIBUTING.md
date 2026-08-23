# Contributing

Thank you for improving Image to Markdown.

## Project boundaries

- Keep the project zero-dependency unless a change genuinely requires otherwise.
- Never commit API keys, private images, PDFs, or OCR output.
- Preserve faithful transcription; summarization, translation, and inferred
  corrections are outside scope.

## Before opening a pull request

1. Make focused changes and explain their user-visible effect.
2. Run the offline checks:

       python3 -B -m unittest discover -s tests -t . -v
       python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .

3. Add or update tests when behavior changes.
4. State any impact on the Mistral service boundary.
5. Update CHANGELOG.md for user-visible changes.

## Releases

Maintainers release validated source by creating an annotated semantic-version
tag and a GitHub Release. The stable installation method remains copying the
repository directory into a Codex skills directory.
