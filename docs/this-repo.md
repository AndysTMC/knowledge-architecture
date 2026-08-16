---
type: belief
status: active
updated: 2026-08-17
---

# This repository as a reference layout

This repo is a **specification**, not a product app. It uses the architecture on itself so the file tree is a worked example of the kernel + the rings this project has earned.

| Path | Kind | Why it exists |
|---|---|---|
| `README.md` | Identity (door) | Human on-ramp |
| `docs/kernel.md` | Protocol (short) | One-page spec |
| `docs/knowledge-architecture.md` | Belief (full spec) | On-demand ring |
| `AGENTS.md` | Protocol | How agents work here |
| `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` | Protocol pointers | Compatibility pack |
| `docs/identity.md` | Identity | Constitution |
| `docs/now.md` | Attention | This week |
| `docs/decisions/` | Decision | Binding choices |
| `docs/this-repo.md` | Belief | Map of the example |
| `docs/implement-prompt.md` | Procedure | Apply elsewhere |
| `model-activity/` | *This project only* | Handoff notes for the next model. Not a ring of the architecture. |
| `CHANGELOG.md` | History (release) | User-facing versions |
| `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `ADOPTERS.md` | Interfaces | Public project |
| `scripts/lint_knowledge.py` | Tool | Mechanical checks |
| `tests/` | Tool tests | Fixture repos and unit tests for the linter |

**Not here (birth rule):** `docs/wiki/`, `docs/schema.md`, `docs/skills/`, `FILES.md`, `hot-cache.md`, `TODO.md`.

`model-activity/` is outside the architecture. Adopters should not create it.

Day-one state of this project was README + spec drafts only. The rings above were added when they had inhabitants (a public repo, a real linter, accepted decisions).
