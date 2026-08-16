# Knowledge Architecture

**v0.1.1** (unreleased) — a typed system for project knowledge that humans and coding agents share.

`v0.1.0` is frozen. This tree is the next patch. Do not move the old tag.

Start here: **[docs/kernel.md](docs/kernel.md)** (one page).  
Full spec: [docs/knowledge-architecture.md](docs/knowledge-architecture.md).  
Sources: [spec §20](docs/knowledge-architecture.md#20-sources).

Protocol, cognition, and compilation stay in different homes. Files are created only when they have a real inhabitant.

This repository **uses the architecture on itself**. See [docs/this-repo.md](docs/this-repo.md).

**Personal or solo repo?** `README.md` + `AGENTS.md` is enough.

## Fast Tier 1

Works on this tree. No tag required:

```bash
python3 /path/to/knowledge-architecture/scripts/lint_knowledge.py --init --root . --install "pip install -e ." --test "pytest"
python3 scripts/lint_knowledge.py --version
python3 scripts/lint_knowledge.py --strict
```

`--init` will not invent `docs/` or empty decision folders. Existing messy repos still need the inspect flow below.

After `v0.1.1` is tagged, you may fetch the script from the `pin` URL that `--version --format json` prints, instead of using a clone.

## Upgrade a vendored linter

`--init` copies the script. Copies do not auto-update.

```bash
python3 scripts/lint_knowledge.py --version --format json
curl -fsSL -o scripts/lint_knowledge.py \
  "$(python3 scripts/lint_knowledge.py --version --format json | python3 -c 'import json,sys; print(json.load(sys.stdin)["pin"])')"
python3 scripts/lint_knowledge.py --version
```

Diff a local patch before replacing: `curl -fsSL "$PIN" | diff -u scripts/lint_knowledge.py -`.

## Tiers

| Tier | Time | What you get |
|---|---|---|
| **1** | `--init` | `AGENTS.md` hub + three pointer files. No `docs/` folder. Most repos stop here. |
| **2** | when work is ongoing | + `docs/now.md`, optional linter in CI |
| **3** | first real decision | + `docs/decisions/` |

## Apply to an existing repo (dry-run first)

Open a Frontier AI session **in the target repository**. The agent must **inspect and stop** until you say apply. Prefer a branch, not `main`.

The inspect/apply prompt stays pinned to the frozen tag so a stranger’s agent does not fetch a moving `main`:

```text
Apply the Knowledge Architecture from https://github.com/AndysTMC/knowledge-architecture
Phase 1 only (inspect, do not write files).

1. Fetch https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.1.0/docs/kernel.md
2. Fetch https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.1.0/docs/implement-prompt.md
3. Fetch https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.1.0/docs/knowledge-architecture.md
4. Report the mapping, what you would create, what you would defer, and conflicts. Then stop.
```

After you approve: “Phase 2 — apply Tier 1 on branch `docs/architecture`.”

Implement file only: https://github.com/AndysTMC/knowledge-architecture/blob/v0.1.0/docs/implement-prompt.md

## Check a repo

```bash
python3 scripts/lint_knowledge.py --strict
python3 -m unittest tests.test_lint_knowledge
```

JSON (stable in v0.1.x): `{ "ok", "errors", "warnings", "fixed" }`.

A PR that lands `Status: accepted` on a decision needs the `human-accepted` label. A PR that deletes an accepted or superseded decision needs `human-removed`. One label does not cover the other.

## License

MIT. See [LICENSE](LICENSE). How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).  
Using this in a product repo? Open an [adoption issue](https://github.com/AndysTMC/knowledge-architecture/issues/new?template=adopted.md) and we can list you in [ADOPTERS.md](ADOPTERS.md).

Continuing *this* repo with another model: [model-activity/](model-activity/) (not part of the spec).
