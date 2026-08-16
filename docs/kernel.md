# Kernel

**Version:** 0.1.1 · Full spec: [knowledge-architecture.md](knowledge-architecture.md)

Keep **protocol**, **identity**, **evidence**, **belief**, **decision**, **attention**, and **history** in different homes. Create a file only when it has a real inhabitant.

**Stop early if that is enough.** A personal or solo repo often needs only `README.md` + `AGENTS.md`. Nothing else here applies until a second person, a second agent, or a decision you would hate to re-litigate shows up.

## Three systems

| System | Job | Do not mix with |
|---|---|---|
| Protocol | How to operate here | Beliefs, history, or a second tool bible |
| Cognition | What we are, believe, chose, are doing | Raw sources or generated dumps |
| Compilation | Compounding picture of sources | The protocol file or the issue tracker |

## Authority

| Level | Meaning | Agents |
|---|---|---|
| 0 | Unverified (`capture/`, chat, `PLAN.md`) | Write. Never cite as fact. |
| 1 | Draft (proposed ADR, unreviewed wiki page) | Create, labeled. |
| 2 | Reviewed (accepted ADR, architecture) | Propose edits. Do not silently rewrite. |
| 3 | Generated (OpenAPI, types, migrations) | Read. Never hand-edit. Prefer over prose. |
| 4 | Constitutional (identity, `AGENTS.md` hard rules, license) | Do not change unless asked. |

Promotion 1→2: a named human accepts it against the bar in the full spec §19. Agents cannot self-promote.

## Day one

- Human door: `README.md`
- If any agent will work here: `AGENTS.md` (short; real commands; routing table of files that exist)
- Software / unknown tools: compatibility pack — `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` as **pointers** to `AGENTS.md`, not copies

## Two clocks

- `PLAN.md` — this agent loop. Overwrite. Do not commit empty.
- `docs/now.md` — this week. Commit. Date it. Stale if older than your cadence.

## Grow only when earned

Decisions, architecture, schema-intent, skills, wiki, capture, changelog, contributing — on first real inhabitant. Never `FILES.md`, `hot-cache.md`, `TODO`+`BACKLOG`+`NOW`, empty `docs/decisions/`, or a Karpathy wiki in a plain product app.

## Agent loop

Read `AGENTS.md` → `docs/now.md` if it exists → accepted decisions as constraints → generated artifacts over prose → targeted test before done → **propose** doc patches; do not silently edit Level 2–4.

Lint: `python3 scripts/lint_knowledge.py --strict`  
Init (Tier 1 only): `python3 scripts/lint_knowledge.py --init --test "…"`  
Version / re-vendor pin: `python3 scripts/lint_knowledge.py --version`  
Tests: `python3 -m unittest tests.test_lint_knowledge`
