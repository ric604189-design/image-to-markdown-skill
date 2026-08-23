# First-Use Prerequisite Confirmation Design

## Objective

Ask a user only once to confirm that they have a usable Mistral API account and
sufficient balance before their first Image to Markdown OCR run. Do not repeat
that account-and-balance reminder after confirmation.

## Decision

The confirmation is an informed user attestation, not an automated account or
balance check. The Mistral API credential is neither read nor stored by the
confirmation flow.

## State

Store a small JSON record at:

    ~/.codex/state/image-to-markdown/prerequisites.json

The record contains a schema version and a UTC confirmation timestamp. It
contains no API key, balance, input path, document content, or OCR output.

## Behavior

1. Before an OCR run, the Skill invokes a local prerequisite-status command.
2. If no valid record exists, it asks the user to confirm they have a usable
   Mistral API account and sufficient balance.
3. Only after affirmative confirmation does the Skill invoke the local
   confirmation command and proceed with normal per-run upload authorization.
4. If the record is valid, the account-and-balance prompt is skipped.
5. Users may invoke a reset command to remove the record and require a new
   confirmation.

## Interface

The existing command gains three non-OCR modes:

- --check-prerequisites returns success when the record is valid and a distinct
  nonzero status when it is absent or invalid.
- --confirm-prerequisites writes the confirmation record and prints its path.
- --reset-prerequisites removes the record if present and prints whether a
  record was removed.

These modes do not require an input path, output directory, API key, or network
access. Normal OCR mode keeps its existing required input and output arguments.

## Constraints

- Do not make a Mistral API request to test balance or validity.
- Do not treat a present API key as user confirmation.
- A malformed record is treated as unconfirmed and may be replaced only after
  a new user confirmation.
- The existing user authorization before each external upload remains required.

## Verification

- Unit tests cover absent, valid, malformed, confirmed, and reset state.
- Existing OCR tests continue to pass.
- The prerequisite modes are verified with no API key and no network access.
- Skill validation succeeds and the repository remains free of credential
  values.
