# Knowledge Architecture

**0.2.0** — a typed system for project knowledge that humans and coding agents share. Latest published release: **v0.2.0**. Published tags are immutable.

Most repositories that coding agents work in end up with conflicting `AGENTS.md`, `CLAUDE.md`, TODO, and notes files, and nothing tells an agent which of them is true. This project gives each kind of knowledge one home: how to operate, what we decided, what we are doing now. Each kind has an authority level, and a small linter keeps the result honest.

- **[Kernel](docs/kernel.md)**: the one-page version. Start here.
- **[Full specification](docs/knowledge-architecture.md)**: the model, the layout, and the edge cases.
- **[Implementation prompt](docs/implement-prompt.md)**: hand it to an agent to apply the spec to a repository.
- **`scripts/lint_knowledge.py`**: a single file that checks the tree, scaffolds a new repository, and gates decision changes in pull requests.

This repository [applies the architecture to itself](docs/this-repo.md).

## Requirements

Python **3.10+**, standard library only. Git is needed for the decision gate. There is nothing to install.

## Use it in a repository

Pick the case that matches the target repository. Always use the same release (`v0.2.0` below) for the linter and the documents.

### 1. New repository, or no agent files yet

From the target repository, run:

```bash
curl -fsSL --create-dirs -o scripts/lint_knowledge.py \
  https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.2.0/scripts/lint_knowledge.py
python3 scripts/lint_knowledge.py --init --test "pytest"
python3 scripts/lint_knowledge.py --strict
```

Replace `pytest` with the real test command; `--install`, `--dev`, and `--lint-command` are optional. Init creates a README if there is none, an `AGENTS.md` hub, the three tool pointers (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`), and the vendored linter. It never creates empty `docs/` folders, and it never overwrites existing files unless you pass `--force`; `--force` still keeps your README. Commands that init infers from manifests are hints, so read `AGENTS.md` before committing it.

### 2. Existing repository with its own docs, never adopted

Init cannot map what is already there, so let an agent do it in two phases. Give it these three files from the same tag:

- `https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.2.0/docs/kernel.md`
- `https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.2.0/docs/implement-prompt.md`
- `https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.2.0/docs/knowledge-architecture.md`

Then send this:

```text
Apply the supplied Knowledge Architecture to the current target repository.
Phase 1 only: inspect, map existing files, report proposed changes and conflicts,
and stop without writing. Preserve existing role locations and local instructions.
```

Review the report, then authorize Phase 2. The agent keeps files that already play a role, such as an existing `adr/` folder, and points `AGENTS.md` at them. Any decision it writes stays `proposed` until a named human accepts it.

### 3. Repository that already uses it (upgrading)

1. Check what you have: `python3 scripts/lint_knowledge.py --version --format json`. Copies never update themselves.
2. Read the [changelog](CHANGELOG.md) entries between that version and the target release, especially the lines on new failures.
3. Re-vendor the target release's script: the same `curl` as in case 1, with that tag.
4. Run `python3 scripts/lint_knowledge.py --strict` and fix what it reports. Do **not** re-run `--init --force` on a hub you have customized, because it replaces `AGENTS.md`.
5. Carry template changes over by hand where they apply. For 0.2.0, add a `Knowledge lint` line running `python3 scripts/lint_knowledge.py --strict` to the Commands section of `AGENTS.md`, and the `human-edited` rule to its write permissions.
6. If you run the decision gate in CI, update the workflow too. The spec's §8 has a minimal adopter workflow.

## Growing past Tier 1

| Tier | Add when | Contents |
|---|---|---|
| 1 | Agents work here | `README.md`, `AGENTS.md` hub, tool pointers |
| 2 | Work needs shared attention | Dated `docs/now.md` |
| 3 | First choice you would hate to re-litigate | `docs/decisions/` and its `_index.md` |

Create a file only when it has a real inhabitant. A personal or solo repository may need nothing beyond Tier 1.

## Everyday commands

```bash
python3 scripts/lint_knowledge.py --strict          # check the tree (include in CI)
python3 scripts/lint_knowledge.py --touch-now       # re-date docs/now.md after reviewing it
python3 scripts/lint_knowledge.py --promotion-base main --format json   # decision gate
```

`--strict` treats warnings as errors and includes the attention clock: a `docs/now.md` older than 14 days fails. The decision gate fails when a pull request accepts, edits, or deletes a protected decision without the matching label: `human-accepted`, `human-edited`, or `human-removed`. JSON output is `{ "ok", "errors", "warnings", "fixed" }`. For a package with its own rings, add `--root <package>`.

## Versions

`--version` reports the embedded version. `pin` is the URL of the last **published** linter, currently `v0.2.0`. Restoring from a pin is not an upgrade: choose a newer tag explicitly. Version strings are not checksums, and published tags are never moved.

## Working on this repository

```bash
python3 -m unittest tests.test_lint_knowledge
python3 scripts/lint_knowledge.py --strict
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the release checklist and CI setup, and [AGENTS.md](AGENTS.md) for agent rules. [Model activity](model-activity/_index.md) is this repository's development history, not part of the architecture.

## License and adoption

[MIT](LICENSE). [Security](SECURITY.md). Report an adoption with the [issue template](.github/ISSUE_TEMPLATE/adopted.md); [adopter listings](ADOPTERS.md) are not proof of completed field validation.
