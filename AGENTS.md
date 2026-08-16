# Agent protocol

## Commands

- Lint: `python3 scripts/lint_knowledge.py --strict`
- Lint JSON (CI): `python3 scripts/lint_knowledge.py --strict --format json`
- Version / pin: `python3 scripts/lint_knowledge.py --version --format json`
- Refresh `docs/now.md` date: `python3 scripts/lint_knowledge.py --fix`
- Scaffold Tier 1 elsewhere: `python3 scripts/lint_knowledge.py --init --test "…"`
- Promotion hook: `python3 scripts/lint_knowledge.py --promotion-base <sha>`
- Linter tests: `python3 -m unittest tests.test_lint_knowledge`

There is no install or app server. This repository is a specification.

## Hard rules

- Do not add a dependency or a new tool-specific rulebook without an explicit ask.
- Do not commit secrets, credentials, or `.env` values.
- Minimal diffs. Touch only what the task requires.
- For work that will edit more than two files, write `PLAN.md` first (gitignored).
- Run `python3 scripts/lint_knowledge.py` before calling the task done.
- Do not silently edit accepted files in `docs/decisions/` or flip a draft to accepted.

## Authority

- Level 0 (not facts): `PLAN.md`, chat
- Level 1 (draft) and Level 3 (generated): see [docs/kernel.md](docs/kernel.md) § Authority
- Level 2 (constraints): accepted files in `docs/decisions/`
- Level 4 (do not edit unless asked): this file, `docs/identity.md`, `docs/kernel.md` (kernel wording is constitutional), `LICENSE`

## Write permissions

- `PLAN.md`: write.
- Proposed decisions: create; leave `proposed`.
- Accepted decisions, architecture, `docs/now.md`, this file, identity, kernel, license: propose a patch. Do not apply silently.
- `Status: proposed` → `accepted`: a named human only. On a PR, add the `human-accepted` label.
- Do not delete an accepted or superseded decision; supersede it. On a PR, add the `human-removed` label. The promotion hook enforces both (`--allow-promotion` / `--allow-deletion`).

## Where to read

| Need | File |
|---|---|
| One-page kernel | docs/kernel.md |
| Full specification | docs/knowledge-architecture.md |
| What this repo is | README.md, docs/identity.md |
| What we are doing now | docs/now.md |
| Why a choice was made | docs/decisions/ |
| How this repo is laid out | docs/this-repo.md |
| How to apply the spec elsewhere | docs/implement-prompt.md |
| Notes for the next model on *this* repo | model-activity/ (not part of the spec) |

## After you finish

Propose, do not silently apply: a `docs/now.md` patch, a decision draft if you chose something, a `CHANGELOG.md` line if the spec changed.
