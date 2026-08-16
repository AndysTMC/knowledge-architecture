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
