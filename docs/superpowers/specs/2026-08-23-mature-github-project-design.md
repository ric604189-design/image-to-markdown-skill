# Mature GitHub Project Design

## Objective

Turn Image to Markdown into a maintainable public open-source repository while
preserving its identity as a zero-dependency Codex Skill. It must remain
installable by copying its directory into a Codex skills location.

## Scope

- Add a repository README that states purpose, capabilities, privacy boundary,
  installation, configuration, and local use.
- Add an MIT license and concise project governance documents: contributing,
  security, code of conduct, and changelog.
- Add GitHub Actions continuous integration that runs the existing offline unit
  tests on supported Python versions.
- Add issue and pull-request templates to make maintenance requests actionable.
- Set repository metadata and topics to support discovery.

## Non-goals

- Publishing a PyPI package, adding third-party dependencies, or building a
  hosted OCR service.
- Storing user credentials, executing a live OCR request in CI, or adding
  telemetry.
- Changing the OCR provider, the API contract, or the output format.

## Repository Structure

- README.md is the public entry point; it links to the skill instructions and
  documents Mistral upload consent and the required environment variable.
- LICENSE contains the MIT license.
- CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, and CHANGELOG.md define
  contribution, behavior, disclosure, and release expectations.
- .github/workflows/test.yml runs unittest and the built-in skill validator on
  Python 3.11 through 3.14 without access to API credentials.
- .github/ISSUE_TEMPLATE/ and .github/pull_request_template.md collect
  reproduction data, privacy context, and verification evidence.

## CI Data Flow

Pull request or push to main → checkout → select each supported Python
version → run offline tests → validate Skill metadata → report status. CI never
receives a Mistral key and never uploads files.

## Release Process

The maintainer records user-visible changes in CHANGELOG.md, runs local
offline checks, creates an annotated version tag, and publishes a GitHub
Release whose notes are derived from the changelog. Releases are source-only;
the stable installation method remains copying the repository directory into
the Codex skills directory.

## Verification

- The existing unit tests pass on the local supported interpreter.
- The skill validator succeeds.
- YAML workflow syntax is structurally valid and contains no credentials.
- Git status is clean after documentation and automation changes.
- The remote repository exposes the metadata and default branch.
