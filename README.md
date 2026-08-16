# Knowledge Architecture

**v0.1.0** — a typed system for project knowledge that humans and coding agents share. This tag is frozen.

Start here: **[docs/kernel.md](docs/kernel.md)** (one page).  
Full spec: [docs/knowledge-architecture.md](docs/knowledge-architecture.md).

Protocol, cognition, and compilation stay in different homes. Files are created only when they have a real inhabitant.

This repository **uses the architecture on itself**. See [docs/this-repo.md](docs/this-repo.md).

**Personal or solo repo?** `README.md` + `AGENTS.md` is enough. Do not adopt the rest until you need it.

## Tiers

| Tier | Time | What you get |
|---|---|---|
| **1** | ~10 min | `AGENTS.md` hub + three pointer files. No `docs/` folder. Most repos stop here. |
| **2** | when work is ongoing | + `docs/now.md`, optional linter in CI |
| **3** | first real decision | + `docs/decisions/` |

## Apply (dry-run first)

Open a Frontier AI session **in the target repository**. The agent must **inspect and stop** until you say apply. Prefer a branch, not `main`.

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

**Offline / no GitHub fetch:** vendor the three files first, then point the agent at the local copies.

```bash
mkdir -p .knowledge-arch
curl -fsSL -o .knowledge-arch/kernel.md \
  https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.1.0/docs/kernel.md
curl -fsSL -o .knowledge-arch/implement-prompt.md \
  https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.1.0/docs/implement-prompt.md
curl -fsSL -o .knowledge-arch/knowledge-architecture.md \
  https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.1.0/docs/knowledge-architecture.md
```

## Check a repo

```bash
python3 scripts/lint_knowledge.py --strict
python3 -m unittest tests.test_lint_knowledge
```

JSON (stable in v0.1.x): `{ "ok", "errors", "warnings", "fixed" }`.

## License

MIT. See [LICENSE](LICENSE). How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).  
Using this in a product repo? Open an [adoption issue](https://github.com/AndysTMC/knowledge-architecture/issues/new?template=adopted.md) and we can list you in [ADOPTERS.md](ADOPTERS.md).

Continuing *this* repo with another model: [model-activity/](model-activity/) (not part of the spec).
