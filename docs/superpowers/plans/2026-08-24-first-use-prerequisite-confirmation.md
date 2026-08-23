# First-Use Prerequisite Confirmation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development
(recommended) or executing-plans to implement this plan task-by-task. Steps use
checkbox (- [ ]) syntax for tracking.

**Goal:** Require and persist one user attestation of a usable Mistral account
and sufficient balance before the first OCR run, without storing a credential.

**Architecture:** The OCR command owns local JSON-state reading and writing so
direct CLI usage cannot bypass the prerequisite. The Skill checks that state,
asks the user only when absent, and confirms it after an affirmative response.

**Tech Stack:** Python standard library, unittest, JSON, argparse, and Codex
Skill Markdown.

---

## File Structure

- scripts/ocr_to_markdown.py — prerequisite state functions, CLI modes, and
  enforcement before normal OCR.
- tests/test_ocr_to_markdown.py — unit and CLI-mode tests using temporary
  state paths only.
- SKILL.md — first-use prompt, confirmation command, no-repeat rule, reset
  guidance.
- README.md — user-facing prerequisite and reset documentation.

### Task 1: Write failing tests for local confirmation state

**Files:**
- Modify: tests/test_ocr_to_markdown.py
- Modify: scripts/ocr_to_markdown.py

- [ ] **Step 1: Add these imports and test cases**

~~~python
import json
import sys
from unittest.mock import patch

from scripts.ocr_to_markdown import (
    PREREQUISITES_VERSION,
    confirm_prerequisites,
    prerequisites_confirmed,
    reset_prerequisites,
)


class PrerequisiteTests(unittest.TestCase):
    def test_absent_state_is_unconfirmed(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertFalse(prerequisites_confirmed(Path(directory) / "state.json"))

    def test_malformed_state_is_unconfirmed(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text("{", encoding="utf-8")
            self.assertFalse(prerequisites_confirmed(state_path))

    def test_invalid_confirmation_timestamp_is_unconfirmed(self):
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
~~~

- [ ] **Step 2: Run the new tests before implementation**

Run: python3 -B -m unittest tests.test_ocr_to_markdown.PrerequisiteTests -v

Expected: FAIL with an import error for the prerequisite-state functions.

### Task 2: Implement prerequisite state and safe CLI modes

**Files:**
- Modify: scripts/ocr_to_markdown.py

- [ ] **Step 1: Add state definitions and functions after API_URL**

~~~python
from datetime import datetime, timezone

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
~~~

- [ ] **Step 2: Make input and output optional at parse time and add a mutually exclusive mode group**

~~~python
parser.add_argument("input", nargs="?", type=Path)
parser.add_argument("--output-dir", type=Path)
modes = parser.add_mutually_exclusive_group()
modes.add_argument("--check-prerequisites", action="store_true")
modes.add_argument("--confirm-prerequisites", action="store_true")
modes.add_argument("--reset-prerequisites", action="store_true")
~~~

- [ ] **Step 3: Handle modes at the beginning of main**

~~~python
if args.check_prerequisites:
    if prerequisites_confirmed(PREREQUISITES_PATH):
        print("Prerequisites confirmed.")
        return 0
    print("Prerequisite confirmation is required.", file=sys.stderr)
    return 3
if args.confirm_prerequisites:
    confirm_prerequisites(PREREQUISITES_PATH)
    print(PREREQUISITES_PATH)
    return 0
if args.reset_prerequisites:
    removed = reset_prerequisites(PREREQUISITES_PATH)
    print("Prerequisite confirmation reset." if removed else "No confirmation record found.")
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
~~~

Keep the existing API-key validation immediately after this block. Use args.input
and args.output_dir for the remaining OCR code.

- [ ] **Step 4: Run the full test suite**

Run: python3 -B -m unittest discover -s tests -t . -v

Expected: Existing OCR tests and five prerequisite-state tests pass without a
network request.

### Task 3: Teach the Skill about first-use confirmation

**Files:**
- Modify: SKILL.md
- Modify: README.md

- [ ] **Step 1: Replace the beginning of the operating procedure with these rules**

~~~markdown
Before the first OCR run, execute:

    python3 scripts/ocr_to_markdown.py --check-prerequisites

If it exits 3, ask exactly once: "Do you confirm that you have a usable Mistral
API account and sufficient balance for this OCR task?" Do not request or expose
the API key in the confirmation. Only after an affirmative answer, execute:

    python3 scripts/ocr_to_markdown.py --confirm-prerequisites

The command writes only confirmation metadata to the local Codex state
directory. When the status command exits 0, skip this account-and-balance
question on future uses. Users can reset it with:

    python3 scripts/ocr_to_markdown.py --reset-prerequisites
~~~

Place these rules before the existing per-run upload-permission instruction.

- [ ] **Step 2: Add a First use section to README.md**

~~~markdown
## First use

Before the first OCR run, confirm that you have a usable Mistral API account
and sufficient balance. The Skill asks for this confirmation once, then stores
only a confirmation timestamp and schema version in the local Codex state
directory. It does not store your API key or balance.

To require the confirmation again:

    python3 scripts/ocr_to_markdown.py --reset-prerequisites
~~~

- [ ] **Step 3: Verify guidance and modes**

Run:

    python3 -B scripts/ocr_to_markdown.py --check-prerequisites
    rg -n "check-prerequisites|confirm-prerequisites|reset-prerequisites|sufficient balance" SKILL.md README.md

Expected: Before confirmation, the command exits 3 without network access and
the documentation describes all three modes.

### Task 4: Validate and release the change

**Files:**
- Modify: CHANGELOG.md

- [ ] **Step 1: Add an Unreleased entry**

~~~markdown
### Added

- One-time local confirmation before the first OCR run that the user has a
  usable Mistral API account and sufficient balance.
~~~

- [ ] **Step 2: Run final safety checks**

Run:

    python3 -B -m unittest discover -s tests -t . -v
    python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
    git diff --check
    if rg -n --hidden --glob '!.git/**' 'ghp_|github_pat_' .; then exit 1; fi

Expected: Tests and Skill validation pass, whitespace is clean, and the
credential-token search produces no matches.

- [ ] **Step 3: Commit, push, and open a pull request**

Run:

    git add SKILL.md README.md CHANGELOG.md scripts/ocr_to_markdown.py \
      tests/test_ocr_to_markdown.py
    git commit -m "feat: confirm Mistral prerequisites once"
    git push -u origin first-use-prerequisites
    gh pr create --base main --head first-use-prerequisites \
      --title "feat: confirm Mistral prerequisites once"

Expected: The branch is published for review with offline checks documented in
the pull request.
