# Contributing

This repository is a specification plus a small linter. Changes should keep the kernel small.

## Before you open a PR

1. Read [docs/kernel.md](docs/kernel.md). Change the full spec only if the kernel is not enough.
2. Run `python3 -m unittest tests.test_lint_knowledge` and `python3 scripts/lint_knowledge.py --strict`.
3. If you change a loader fact in §18, update **Tool table review-by** and add a changelog line.
4. Do not add empty template directories. Do not add a second copy of `AGENTS.md` into a tool file.
5. A PR that sets a decision to `Status: accepted` must have the `human-accepted` label. A PR that deletes an accepted or superseded decision must have `human-removed`. `--allow-promotion` does not allow deletions. The labels are human claims, not a review.

## What belongs where

- Wording and examples → patch the spec or kernel; add a `CHANGELOG.md` patch line.
- A new *kind* of information → a decision file first (`docs/decisions/`), then the spec. That is a constitutional change.
- Linter rules → `scripts/lint_knowledge.py` plus a unit test for the new failure. `--init` must not grow empty rings.

## Decisions

Accepted decisions are not rewritten in place. Supersede them with a new numbered file and update `docs/decisions/_index.md`.

## Tags and history

**Published tags are never moved.** `v0.1.0` and `v0.1.1` are frozen. Strangers’ agents pin `raw.githubusercontent.com/.../v0.1.1/scripts/lint_knowledge.py` (and older pins to `v0.1.0` docs). A moved tag silently changes what they fetch.

- Ship later fixes as `v0.1.2` or later. Do not `git tag -f` and do not force-push a tag that already exists on GitHub.
- Do not rewrite `main` history once a tag that outsiders pin has been published.
- README apply blocks that pin a version should keep pinning that frozen tag until you intentionally bump the pin in a new release.

## Review gates and repository settings

Tree lint and the decision gate are separate commands. `--strict` includes stale attention and the dated tool survey by design. Review content before `--touch-now` (alias `--fix`); it changes only a stale date. A contributor may report stale attention for the maintainer to refresh rather than fabricating a review date.

Create labels `human-accepted`, `human-removed`, `human-edited`, and `adoption` in repository settings. Acceptance, removal, and edits have separate allow flags. Protected edits include clarifications, demotions, and supersession metadata; the label is permission for review, not permission to invert an accepted choice in place.

Configure branch rules to require the `lint` matrix jobs and `promotion`, require code-owner approval for protected files, dismiss stale approvals after new commits, and restrict bypass/direct pushes. The checked-in workflow and CODEOWNERS do not activate those settings automatically. Restrict who can set human-review labels. Labels alone do not establish who reviewed a change.

PR CI runs the gate from both the base revision and proposed tree. The base checker cannot be weakened by changing only the PR's script; the proposed checker exercises new rules. A base release predating edit protection cannot enforce that new rule until the repaired checker is merged. Workflow edits still require protected human review.

For `--promotion-diff`, supply a full-context unified diff (`git diff --unified=1000000`); an unknown pre-image status is conservatively protected. `--promotion-base` resolves the merge base with HEAD, uses full context, includes staged/unstaged tracked changes, and never runs external diff/textconv helpers. Add new files to the index before local gate validation. CI operates on committed files.

## Release checklist

1. Run the full tests on supported Python versions (3.10 and 3.12 in CI), strict tree lint, and a clean temporary Tier 1 init using the actual distributed script path.
2. Review the adoption prompt, kernel, and linter together; the chosen immutable ref must contain a compatible set. Historical links and older tags may legitimately remain in history.
3. Replace the development version with the intended release version in the script, kernel, specification, README, and changelog. Set `PIN_URL` to that release only when preparing its publication; do not claim the URL is live before publishing it.
4. Review the diff and proposed decisions with a named human. Publish a new tag only after the release is authorized. Never move an existing tag.
5. Verify the published artifact's download and end-to-end init, then advertise that ref in adoption instructions. Start a development version and an Unreleased changelog section only when actual linter or specification changes need a future release. Do not open an empty development cycle for release bookkeeping, portfolio updates, or ADR acceptance. Keep `pin` pointing to the last published artifact until the next release.

A version identifies an intended artifact; it is not an integrity checksum. Restoring a vendored copy from its existing pin is not an upgrade. Release notes must call out any new failing lint rule so adopters can evaluate CI impact.
