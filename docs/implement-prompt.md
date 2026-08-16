# Prompt: implement the Knowledge Architecture in this repository

## If you were given a GitHub or git URL to this file

You are working in a **target** repository. This file lives in a **different** repository (the specification).

1. Fetch **this file in full**. If you were given a `github.com/.../blob/...` link, use the matching `raw.githubusercontent.com` URL (or the raw view).
2. Fetch the sibling **kernel** and **specification** from the same repo and branch: `docs/kernel.md`, then `docs/knowledge-architecture.md`.
3. Treat the specification as the source of truth. The kernel is the always-on summary. This prompt is the procedure. If they disagree, the specification wins. Optionally copy `scripts/lint_knowledge.py` into the target if the human wants CI.
4. Apply the procedure to the **current working tree**. Do **not** clone the specification repository over the target. Do not replace the target `README.md` with the specification repo’s README. Do not copy `model-activity/` (that folder is only for developing *this* spec repo).
5. Then follow everything below.

Canonical URLs (branch `main`):

- Spec repo: https://github.com/AndysTMC/knowledge-architecture
- Kernel (one page): https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/main/docs/kernel.md
- This prompt: https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/main/docs/implement-prompt.md
- Specification: https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/main/docs/knowledge-architecture.md

If those fetches fail, follow this prompt alone.

Prefer **pinned** URLs (`.../v0.1.0/docs/...` on `raw.githubusercontent.com`) when the human asked for a vendor/offline copy. Do not fetch from `main` if they pinned a tag.

## Fast path (greenfield Tier 1 only)

If the target has **no** `AGENTS.md` / `CLAUDE.md` yet and the human only wants the kernel, do **not** absorb the full spec. Fetch the linter from the `v0.1.1` pin (or copy it from a clone) and run:

```bash
python3 lint_knowledge.py --init --install "<real>" --test "<real>"
python3 lint_knowledge.py --version
python3 lint_knowledge.py --strict
```

Then stop and report. `--init` must not create `docs/decisions/`, `docs/wiki/`, or `docs/now.md`. If the repo already has docs or agent files, ignore this path and do Phase 1.

## Phases (do not skip Phase 1)

**Phase 1 — inspect only.** Produce the implementation report (mapping, would-create, would-defer, conflicts). Do **not** write files. Stop and wait.

**Phase 2 — apply.** Only after the human says to apply. Prefer a new branch (`docs/architecture` or `knowledge-arch`) and a single PR. Do not commit to the default branch unless they asked.

**Done** when `python3 scripts/lint_knowledge.py --strict` would pass on the target (copy the script if it is not there). If the human did not want the linter vendored, still satisfy every check it would run.

---

You are implementing an existing Knowledge Architecture in **this** (the target) repository. You are not inventing a documentation system. You are not creating a starter kit of empty Markdown files.

If `docs/knowledge-architecture.md` is already in the target, or you fetched it in the step above, read it first. If it is not available, follow this prompt as the specification.

## Goal

Leave the repo with:

1. A thin human door (`README.md`).
2. A short agent protocol (`AGENTS.md`) **if** any coding agent will work here, filled with **this repo’s real commands**, not placeholders.
3. The **compatibility pack** so popular CLIs/IDEs load the same hub: `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` (pointers only). Extra tool files only if that tool is already in the repo.
4. Additional docs **only** when this repo has already earned them.
5. No parallel universe of unused files. No second copy of the rules.

Success is a correct kernel plus honest deferrals — not a complete-looking tree.

## Non-negotiable rules

**Birth rule.** Do not create a file or directory until it has a real inhabitant. Empty `docs/decisions/`, empty `docs/wiki/`, empty `docs/skills/`, and `0000-template.md` are failures.

**One router.** The routing table lives in `AGENTS.md` if that file exists, otherwise in `README.md`. Do not also create `MAP.md`, `FILES.md`, `hot-cache.md`, `AI_CONTEXT.md`, `NOTES.md`, `TODO.md`, `BACKLOG.md`, or `SCRATCHPAD.md`.

**Map, then create.** If a file already plays a role, keep it. Point at it. Do not duplicate it under the default name.

| Existing file (examples) | Treat as |
|---|---|
| `PROJECT.md`, `VISION.md` | Identity |
| `ARCHITECTURE.md`, `docs/architecture.md`, `DESIGN.md` (system shape, not pixels) | Current-shape belief |
| `adr/`, `docs/adr/`, `docs/decisions/` | Decisions |
| `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `LICENSE` | Interfaces — leave them |
| `CLAUDE.md`, `.claude/`, `.cursor/`, `.github/copilot-instructions.md` | Tool presence — pointer only |
| OpenAPI, Prisma, SQL migrations, protobufs, Zod | Generated schema. Do not transcribe fields |

**Roles are the API. Paths below are defaults.** If the repo already uses a stronger path for a role, keep that path and route to it.

**Do not add CI, git hooks, linters, or dependencies** unless the human asked.

**Do not rewrite product code** except the smallest `.gitignore` change if you gitignore `PLAN.md`.

**Do not gut a working README.** Thin it only if it has become a second wiki. Always keep the first successful run/read path.

## The model you are implementing

Three systems, kept distinct:

- **Protocol** — how a stranger or agent operates here. Human-authored. `AGENTS.md`.
- **Cognition** — identity, beliefs, decisions, current attention. Humans write; agents may draft under review.
- **Compilation** — an LLM-maintained wiki of *sources*. Only if this project accumulates sources. Not a software docs tree.

Seven kinds of information. Do not mix two kinds in one new file:

| Kind | Question | Default home | Create when |
|---|---|---|---|
| Protocol | How do we operate? | `AGENTS.md` + thin pointers | Any agent will work here |
| Identity | What is this, why, not-for-what? | `README.md`; `docs/identity.md` if that overflows | Scope/non-goals/ownership no longer fit in README |
| Evidence | What did a source say? | `docs/wiki/raw/` | Wiki ring is earned |
| Belief | What do we claim? | `docs/architecture.md` (and `docs/schema.md` for data-model *intent*) | Someone must explain current shape / why the model looks this way |
| Decision | What did we choose? | `docs/decisions/NNNN-slug.md` | At least one choice you would hate to re-litigate |
| Attention | What are we doing now? | `docs/now.md` (project), `PLAN.md` (session, usually gitignored) | Current intent is not fully expressed by the tracker, or there is no tracker |
| History | What happened that git will not tell you? | `docs/log.md` | A belief flip or external event that would otherwise vanish |

Authority (put a short form in `AGENTS.md`):

| Level | Meaning | Examples | Agents may |
|---|---|---|---|
| 0 | Unverified | capture, chat, `PLAN.md` | Write. Never cite as fact |
| 1 | Draft | proposed ADRs, unreviewed wiki pages | Create, labeled |
| 2 | Reviewed | accepted ADRs, architecture | Propose edits |
| 3 | Generated | OpenAPI, migrations, types | Read. Never hand-edit |
| 4 | Constitutional | identity, `AGENTS.md` hard rules, license | Do not change unless asked |

Two clocks: `PLAN.md` is this agent loop (overwrite; do not commit empty). `docs/now.md` is this week (commit; date it).

`docs/schema.md` = why the **product** data model is this way (points at generated artifacts).  
`docs/wiki/SCHEMA.md` = how to **operate the wiki**. Never merge these files.

## Procedure (do this in order)

### 1. Inspect

Explore the repo. Record, in your working notes:

- Project type: software product, library, monorepo, research, mixed, personal, other.
- Package manager and the real install / dev / test / lint / build commands (read manifests and CI; do not guess).
- Existing documentation and agent files (list paths).
- Whether an issue tracker is the task system.
- Whether the project accumulates sources that should be compiled (papers, incidents, research). If no, the wiki ring is **not** earned.
- Which agent tools are already present (`CLAUDE.md`, `.claude/`, `.cursor/`, Copilot instructions, `.gemini/`, `.aider.conf.yml`, existing `AGENTS.md`).
- Public vs private (interface files).

If commands are genuinely unclear, say so in the final report and pick the smallest documented command. Do not invent a stack.

### 2. Classify existing files

For each existing doc, assign one role or mark it as leftover. You will either keep it as the source of truth for that role, or reduce a duplicate to a pointer. Two files claiming the same fact is a bug: keep one, point the other, mention it in the report.

### 3. Kernel (Tier 1 is enough unless a later ring is earned)

**Tier 1 (about 10 minutes):** `README.md` + `AGENTS.md` + the three pointer files if this is a software/agent repo. No `docs/` folder. Stop here unless a ring is earned.

**Tier 2:** + `docs/now.md` and, if they asked, the linter in CI.

**Tier 3:** + `docs/decisions/` the day the first real decision exists.

### 3b. Write the kernel files

**README.md**

- Ensure it exists.
- One paragraph what / who it is for.
- The first successful path to run or read.
- Links to `AGENTS.md` and to any cognition files that exist after this pass.
- Do not move identity, architecture, or history into it.

**AGENTS.md** (create or replace-as-hub if agents will work here)

Target well under 200 lines. Real commands only. No `___` placeholders. No copy of the README.

Required sections:

1. Commands — install, dev, test one file, test full, lint/format, build if it exists.
2. Hard rules — minimal diffs; no new dependencies / generated-code edits / migrations without an ask; never commit secrets, credentials, or `.env` values; write `PLAN.md` before touching more than two files; run the targeted test before declaring done.
3. Authority — the table above, with paths that exist in **this** repo after your pass.
4. Where to read — a routing table. **Only rows whose targets exist** (or that you created in this pass). Delete rows for rings you deferred.
5. After you finish — propose `docs/now.md` patches, decision drafts, and history lines. Do not silently edit constitutional files.

If `AGENTS.md` already exists and is good, keep its local facts. Reshape it into this structure. Do not throw away stack-specific rules that are still true.

**Compatibility pack** (install for software / mixed / any repo agents will open)

Pointers only. No facts. If an existing native file has unique still-true rules, move shared rules into `AGENTS.md` and keep only tool-specific mechanics below the pointer.

`CLAUDE.md` (Claude Code does not read `AGENTS.md` natively):

```markdown
@AGENTS.md
```

Then only existing Claude-specific mechanics (hooks, subagents). Do not invent them. If both `CLAUDE.md` and `.claude/CLAUDE.md` already exist, keep one pointer — prefer the path already in use.

`GEMINI.md` (Gemini CLI still defaults to this name):

```markdown
@AGENTS.md

All operational instructions live in AGENTS.md. Follow that file.
```

`.github/copilot-instructions.md` (some Copilot IDE/review surfaces still treat this as primary):

```markdown
Refer to [AGENTS.md](../AGENTS.md) for all repository agent instructions. That file is the source of truth for commands, conventions, authority, and routing.
```

**Native `AGENTS.md` readers — do nothing extra:** Codex, Cursor, Copilot coding agent / VS Code agent, Jules, Amp, Factory, OpenCode, goose, Zed, Warp, Junie, Windsurf/Cascade/Devin Desktop, Cline/Kilo, Kiro, Grok.

**Add only if that tool is already present:**

- Aider: `.aider.conf.yml` with `read: AGENTS.md`
- Continue: `.continue/rules/project.md` pointing at `AGENTS.md`
- Gemini workspace settings: either commit `GEMINI.md` as a pointer **or** set `context.fileName` to `AGENTS.md`. Not both, or Gemini loads the hub twice.
- Cursor glob extras: `.cursor/rules/*.mdc` — only for path-scoped rules, not a copy of the hub
- Do **not** create legacy `.cursorrules`, `.windsurfrules`, or `.clinerules` for coverage. Those tools read `AGENTS.md` now.

**PLAN.md**

- Do not create and commit an empty `PLAN.md`.
- Mention it in `AGENTS.md`.
- Optionally add `PLAN.md` to `.gitignore` if the repo has one and the team would treat it as local scratch. Do not invent a `.gitignore` from scratch unless the repo has none and you are only ignoring `PLAN.md`.

### 4. Rings (only if earned)

Create at most what the inspect step justified.

**docs/identity.md** — Intent, problem, scope, non-goals, success, constraints, principles, ownership. Write from what the repo and README already imply. Do not invent a vision.

**docs/now.md** — Dated. 1–3 focus items, next actions, blocked, do-not-do. Link the tracker. Do not clone the board. If the tracker is sufficient and there is no extra intent, skip this file.

**docs/architecture.md** — Current shape: boundaries, data flow, invariants. Headings, not a novella. If `ARCHITECTURE.md` or similar already exists, keep it and route to it.

**docs/schema.md** — Only if a data model exists and its *intent* is not obvious from generated artifacts. Point at those artifacts. Do not list every field.

**docs/decisions/** — Only if you can write at least one real decision from repo evidence (stack choice, auth, storage, public API shape, etc.). Then create:

- `docs/decisions/0001-<slug>.md` (or the next free number if ADRs already exist)
- `docs/decisions/_index.md` as a table: id, title, status, date, supersedes

Decision template (one choice per file; title is a choice, not a topic):

```markdown
# 0001. <We will …>

Status: accepted
Date: <today>
Deciders: <if known, else "existing project">
Supersedes: —
Superseded-by: —

## Context
## Options
## Decision
## Assumptions
- [A1] … (revisit if …)
## Consequences
## Revisit if
```

Do not create `0000-template.md`. Do not create the directory with only an index.

If ADRs already exist, do not rewrite them. Add `_index.md` only if missing. Put new decisions in the existing directory.

**docs/skills/<task>.md** — Only if a recurring procedure already lives in the repo (release, migrate, hotfix) or the human named one. One job per file. Do not invent runbooks.

**docs/wiki/** — Only if this project compiles sources. If earned, create `SCHEMA.md` (ingest / query / lint / file-back-answers; raw is immutable; pages are derived; unreviewed pages are not sources), `index.md`, `log.md` with today’s bootstrap line, and `raw/` + `pages/` only with a real first source or a one-line README in `raw/` explaining what belongs there. Prefer not to create the wiki at all over creating an empty one.

**docs/capture/inbox.md** — Only if you are quarantining an existing notes landfill, or the human asked.

**docs/log.md** — Only if you must record something git will not explain. Otherwise skip.

**docs/glossary.md** — Only if a term is already argued or overloaded in the repo.

**Interface files** — Do not add `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`, or `CODE_OF_CONDUCT.md` unless the repo is public / multi-contributor and the file is missing **and** the human wants them. If they exist, leave them.

**docs/work/** and **out/** — Skip unless a real work package or a real external deliverable already needs a home.

**Monorepo nested AGENTS.md** — Do not add package-level files unless a package already has distinct commands or an existing nested agent file. Nearest file wins; do not copy the root matrix into every package.

### 5. Wire the router

After creating files, update `AGENTS.md` (or `README.md`) so every created or mapped hub is one hop away. Remove rows that point at files you did not create.

If `README.md` should point inward, add two or three links. Do not paste architecture into the README.

### 6. Stop

Do not add a weekly-ritual essay, CI lint for docs, ID generators, or further PKM structure.

## Done when

- [ ] Inspect notes exist (in the report, not as a new repo file).
- [ ] Existing files are mapped; no two files claim the same fact without a pointer.
- [ ] `README.md` is a door, not a wiki.
- [ ] `AGENTS.md` (if required) has real commands, authority, and a routing table with only live targets; it is under ~200 lines.
- [ ] Compatibility pack exists for software/agent repos: `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` are pointers, each under ~10 lines, no duplicated facts.
- [ ] No legacy `.cursorrules` / `.windsurfrules` / `.clinerules` created for coverage.
- [ ] No empty ring directories. No `FILES.md`, `hot-cache.md`, `MAP.md`, `TODO.md`, `0000-template.md`.
- [ ] No new CI, dependencies, or product-code refactors.
- [ ] Report written to the human.
- [ ] `python3 scripts/lint_knowledge.py --strict` would pass (or you listed every remaining lint error).

## Report format (write this to the human at the end)

```markdown
# Knowledge architecture — implementation report

## Project type
## Commands discovered
## Mapped (existing path → role)
## Created
## Compatibility pack
## Updated
## Deferred rings (and why)
## Conflicts resolved
## Risks / follow-ups
```

Begin with inspection. Do not create files until the inspect and classify steps are done.
