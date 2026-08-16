# Contributing

This repository is a specification plus a small linter. Changes should keep the kernel small.

## Before you open a PR

1. Read [docs/kernel.md](docs/kernel.md). Change the full spec only if the kernel is not enough.
2. Run `python3 -m unittest tests.test_lint_knowledge` and `python3 scripts/lint_knowledge.py --strict`.
3. If you change a loader fact in §18, update **Tool table review-by** and add a changelog line.
4. Do not add empty template directories. Do not add a second copy of `AGENTS.md` into a tool file.

## What belongs where

- Wording and examples → patch the spec or kernel; add a `CHANGELOG.md` patch line.
- A new *kind* of information → a decision file first (`docs/decisions/`), then the spec. That is a constitutional change.
- Linter rules → `scripts/lint_knowledge.py` plus a test-ish note in the PR (what it now fails on).

## Decisions

Accepted decisions are not rewritten in place. Supersede them with a new numbered file and update `docs/decisions/_index.md`.

## Tags and history

**Published tags are never moved.** `v0.1.0` is frozen. Strangers’ agents pin `raw.githubusercontent.com/.../v0.1.0/docs/...`. A moved tag silently changes what they fetch.

- Ship fixes as `v0.1.1` or later. Do not `git tag -f` and do not force-push a tag that already exists on GitHub.
- Do not rewrite `main` history once a tag that outsiders pin has been published.
- README apply blocks that pin a version should keep pinning that frozen tag until you intentionally bump the pin in a new release.
