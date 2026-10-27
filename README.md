# Knowledge Architecture

**0.1.3.dev0 (unreleased)** — a typed system for project knowledge that humans and coding agents share. Latest published release: **v0.1.2**. Published tags are immutable.

Start with [docs/kernel.md](docs/kernel.md). The [full specification](docs/knowledge-architecture.md) defines the model; the [implementation prompt](docs/implement-prompt.md) applies it elsewhere.

Keep protocol, cognition, and source compilation in separate homes. Create a file only when it has a real inhabitant. For a personal or solo repository, `README.md` + `AGENTS.md` may be enough.

This repository [uses the architecture on itself](docs/this-repo.md).

## Requirements

Python **3.10+**, standard library only. Git is needed for `--promotion-base`. There is no install step or app server.

## Fast Tier 1

From the target repository, download the pinned release and supply the real test command:

```bash
curl -fsSL --create-dirs -o scripts/lint_knowledge.py \
  https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.1.2/scripts/lint_knowledge.py
python3 scripts/lint_knowledge.py --root . --init --test "pytest"
python3 scripts/lint_knowledge.py --strict
```

Or use this checkout against an existing target directory:

```bash
python3 scripts/lint_knowledge.py --root /absolute/path/to/target --init --test "pytest"
python3 /absolute/path/to/target/scripts/lint_knowledge.py --strict
```

Init creates a missing README, an `AGENTS.md` hub, three tool pointers, and a vendored linter. It does not create empty `docs/` rings. Existing files are preserved; `--force` replaces protocol, pointers, and the linter but preserves README. `--no-compat` omits the pointers.

Commands inferred from manifests are hints; review them before use. Existing repositories with documentation need the inspect/apply flow below.

## Apply to an existing repository

Give the agent the kernel, implementation prompt, and full specification **from the same checkout or immutable commit**:

```text
Apply the supplied Knowledge Architecture to the current target repository.
Phase 1 only: inspect, map existing files, report proposed changes and conflicts,
and stop without writing. Preserve existing role locations and local instructions.
```

After reviewing the report, authorize Phase 2. New decisions remain `proposed`; a named human accepts them.

Use `v0.1.2` for the kernel, implementation prompt, full spec, and linter. Historical `v0.1.0` templates lack some frontmatter required by the `v0.1.1` linter. Do not combine those pins as a working adoption recipe. The `v0.1.2` artifact set includes the template fixes.

## Vendored versions

```bash
python3 scripts/lint_knowledge.py --version --format json
```

`version` identifies this script; `pin` points to the last **published** linter, currently `v0.1.2`. A development version can differ from that artifact. Downloading the installed copy's `pin` restores its published baseline; it does not discover an upgrade.

To upgrade, choose a published release explicitly, inspect its changes, and vendor that release's script. Use the same release's adoption documents. Copies do not auto-update; version strings are not checksums. Published tags are never moved.

## Tiers

| Tier | Add when | Contents |
|---|---|---|
| 1 | Agents work here | Human door, protocol hub, pointers |
| 2 | Work needs shared attention | Dated `docs/now.md` |
| 3 | First durable choice | Decisions and their index |

## Validate

```bash
python3 -m unittest tests.test_lint_knowledge
python3 scripts/lint_knowledge.py --strict
python3 scripts/lint_knowledge.py --promotion-base main --format json
```

Tree lint and the decision gate are separate modes. JSON retains `{ "ok", "errors", "warnings", "fixed" }`. Strict lint includes clock checks; `--touch-now` (alias `--fix`) refreshes only a stale date, not the content.

The gate uses the merge base with HEAD and includes local staged/unstaged changes. New acceptance requires `human-accepted`; protected deletion requires `human-removed`; editing an accepted/superseded decision requires `human-edited`. A partial diff without the old status is conservatively protected. See [CONTRIBUTING.md](CONTRIBUTING.md) for CI setup and limitations.

## License and adoption

[MIT](LICENSE). [Contributing](CONTRIBUTING.md). [Security](SECURITY.md).

[Adopter listings](ADOPTERS.md) are not proof of completed field validation. Report adoption through the [issue template](.github/ISSUE_TEMPLATE/adopted.md).

[Model activity](model-activity/_index.md) is development history for this repository, not part of the architecture.
