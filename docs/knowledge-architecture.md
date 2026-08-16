# A Knowledge Architecture for Humans and Agents

**Version:** 0.1.1  
**Updated:** 2026-08-17  
**Tool table review-by:** 2026-11-17 (§18 ages; treat it as stale after that date until revised)

Start with [docs/kernel.md](kernel.md) if you have not read this before. This file is the full ring.

**Contents**

- [0. The mistake](#0-the-mistake-every-prior-answer-made)
- [1. What to keep](#1-what-to-keep-from-the-prior-answers)
- [2. Weak assumptions](#2-weak-assumptions-to-drop)
- [3. Contradictions](#3-contradictions-resolved)
- [4. What was missing](#4-what-was-missing-from-every-prior-answer)
- [5. The model](#5-the-model)
- [6. Default layout](#6-default-layout-roles-not-a-dump)
- [7. Information flow](#7-information-flow)
- [8. Anti-rot](#8-anti-rot-ritual--mechanics)
- [9. Source-of-truth matrix](#9-source-of-truth-matrix)
- [10. Agent protocol](#10-agent-protocol-put-this-in-agentsmd)
- [11. Decision record](#11-decision-record-the-one-template-that-matters)
- [12. Scale](#12-scale-without-a-rewrite)
- [13. Domain adapters](#13-domain-adapters-same-kinds-different-muscles)
- [14. What not to create](#14-what-you-should-not-create)
- [15. Day-one templates](#15-day-one-templates)
- [16. Why this shape lasts](#16-why-this-shape-lasts)
- [17. Implementation contract](#17-implementation-contract)
- [18. Tool compatibility](#18-tool-compatibility)
- [19. Edges](#19-edges)
- [20. Sources](#20-sources)

**One sentence.** Keep protocol, identity, evidence, belief, decision, attention, and history in different homes — then grow a file only when a real instance of that kind appears.

This is not a starter pack of twenty Markdown files. It is a typed information system with a small kernel, optional rings, an authority model, and explicit write permissions. The same roles work for a weekend script, a SaaS product, a research program, a lab, a company, or a personal body of work. Paths below are a **default mapping**. The roles are the API. Never rename the roles; you may relocate the files if a domain already has a stronger convention.

---

## 0. The mistake every prior answer made

The conversation you collected smashed three different systems into one folder tree, then argued about which tree was “complete.”

| System | Job | Who writes | Failure if mixed with the others |
|---|---|---|---|
| **Protocol** | How a stranger or an agent should operate *here* | Humans. Agents consume. | Becomes a second README, or a tool-specific bible that drifts |
| **Cognition** | What this is, what we believe, what we decided, what we are doing | Humans, or agents under review | Becomes a wiki that cannot tell a decision from a hunch |
| **Compilation** | A compounding, interlinked picture of *sources* | Agents write. Humans curate sources and review | Becomes a software docs tree, or a self-citing hallucination |

Karpathy’s LLM Wiki (April 2026) is **compilation** ([S1](#20-sources)). `AGENTS.md` (Linux Foundation / Agentic AI Foundation, Dec 2025) is **protocol** ([S2](#20-sources)). ADRs and a current-attention file are **cognition**. A file named `index.md` does not make a coding agent smarter. A Zettelkasten does not tell Codex how to run tests. A 200-line `AGENTS.md` does not remember why you rejected Kafka.

A future-proof architecture keeps the three systems distinct, then lets a project activate only the rings it has earned.

---

## 1. What to keep from the prior answers

**From the agent-file dump and hub-and-spoke**

- `README.md` is for humans. `AGENTS.md` is for agents. That split is now an industry standard, not a preference.
- One hub, many pointers. Do not maintain `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, and Copilot instructions as independent rulebooks.
- Progressive disclosure. The file that loads every session must stay short. Deep material is linked, not inlined.
- On-demand skills / recipes beat a single `SKILL.md` novella.
- Session working memory (a plan the current loop can resume) is real. Compaction and subagents lose the plot without it.

**From Spine**

- Cognitive kinds — identity, belief, decision, attention, history — must not share a file. Protocol and evidence are the other two kinds; same rule.
- Small core, optional organs. Empty directories are a smell.
- Create on first real instance, not on a schedule.
- A source-of-truth matrix is more valuable than a clever folder taxonomy.
- Capture is quarantine, not knowledge. Agents must be told that explicitly.
- Maps and links beat deep topic trees.
- Rituals matter, but ritual alone is not enough (see §8).

**From Nexus**

- Proposal → accepted decision → update the current-state view. Pre-decision is a distinct phase.
- Accepted decisions are not silently rewritten. A new record supersedes the old.
- Root-level social interfaces (`CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`) are not knowledge organs. They are doors the world expects.
- Index tables with status columns are more usable than prose lists.

**From the last, agent-minimal answer**

- `README.md` + `AGENTS.md` are the only non-negotiable files for a brand-new *software* repo.
- Hand-maintained `LOG.md` that duplicates git is a liability.
- `TODO.md` / `BACKLOG.md` that duplicate an issue tracker are a liability.
- Empty `docs/decisions/` with no decisions is worse than no folder.
- Do not merge a personal Zettelkasten into the repo agents build against.

**From Karpathy’s actual gist (not the cargo-cult file list)**

- Raw sources are immutable. The compiled wiki is a *derived* layer.
- How to ingest, query, and lint the wiki lives in `docs/wiki/SCHEMA.md`. Root `AGENTS.md` points at it. That is not a second root protocol.
- `index.md` is a catalog. `log.md` is a tape of wiki operations. They are not software project history.
- Good answers get filed back. Chat is not a store.
- Lint for contradictions, orphans, stale claims, missing pages.

**From the 2026 tool reality**

- `AGENTS.md` is the portable standard (60k+ repos; nested files; nearest wins) ([S3](#20-sources)).
- Claude Code still reads `CLAUDE.md`, not `AGENTS.md`. Official pattern: first line `@AGENTS.md`, or a symlink. On Windows, use the import ([S5](#20-sources)).
- Claude Code auto-memory is **machine-local** and is not the team knowledge base. Do not confuse `MEMORY.md` under the local Claude project directory with the repo ([S6](#20-sources)).
- Skills load on demand. Path-scoped rules load when matching files are touched. Both exist so the root protocol can stay small.
- Repository overviews and README clones in `AGENTS.md` do not help task success and raise cost. Keep the hub to commands, don’ts, and landmines an agent cannot discover by reading the tree. Route; do not copy ([S4](#20-sources)).

---

## 2. Weak assumptions to drop

The anti-file list is §14 only. This table is the *beliefs* that produce those files.

| Assumption | Why it is wrong |
|---|---|
| “A comprehensive project needs all of these `.md` files.” | Comprehensive *coverage of kinds* is not a maximal file list. Unused files rot and become false authority. |
| `LOG.md` is always essential. | For code, git + PRs + ADRs + a curated changelog already are history. A parallel tape either duplicates them or drifts. A tape *is* essential for wiki ingest and for belief changes that are not commits. |
| One `ARCHITECTURE.md` blob is always a sin. | One file until it cannot be read in a sitting. Split by view or subsystem only then. Premature decomposition is how teams lose the plot. |
| `SCHEMA.md` should list every field. | Generated artifacts (migrations, Prisma, OpenAPI, protobufs, Zod) are the schema. Prose explains *why*, and points. Hand-transcribed fields drift. |
| Tool pointer files should restate the rules. | Pointers that grow become a second source of truth. Keep them as imports. |
| A weekly ritual will keep the system alive. | Teams that do not already have a review rhythm will not grow one for Markdown. Pair ritual with mechanical checks (§8). |
| IDs like `K014` are required on day one. | They pay off when notes outgrow memory. Until then they are ceremony. Adopt IDs at the compounding stage, not the spark. |
| Agents should treat every Markdown file as true. | Capture, scratch, chat, and unreviewed wiki pages are not authority. Without an authority model the architecture is a suggestion. |
| The Karpathy wiki belongs in every software repo. | It belongs when you are accumulating *sources* you want compiled. A CRUD app does not need `raw/` and entity pages. |
| “Never guess, always `ls -R` first is waste, so never explore.” | Agents still need to read code. The rule is: do not *speculate about contracts*. Do explore the files the routing table named. |

---

## 3. Contradictions, resolved

**Universal vs software-shaped.**  
The *kinds* are universal. The *default paths* lean software because that is where agent tooling has gravity. A thesis uses the same kinds under `docs/` or at root. Do not invent `know/` vs `docs/architecture/` as competing religions. Pick one home (`docs/`) and specialize inside it.

**Minimal vs comprehensive.**  
The kernel is two to five files. Comprehensiveness is the *catalog of roles you are allowed to grow*, plus rules that stop you from growing them early. A system that requires twenty files on day one is not comprehensive. It is brittle.

**`AGENTS.md` as hub vs `MAP.md` as hub.**  
For software, `AGENTS.md` is the machine front door (ecosystem gravity). For a non-software project with no agents, `README.md` plus a short identity file is enough. Do not maintain both a `MAP.md` and an `AGENTS.md` routing table. One router. If you have `AGENTS.md`, the routing table lives there. If you do not, it lives in `README.md`.

**`PROJECT.md` vs a fat README.**  
Identity that changes slowly should not live in the onboarding door. If identity is one paragraph, it may stay in `README.md`. The moment people argue about scope or non-goals, split it to `docs/identity.md` (or `PROJECT.md` at root if you prefer that name). Same role.

**Wiki `log.md` vs project `LOG.md` vs git vs `CHANGELOG.md`.**

| Tape | Records | Audience |
|---|---|---|
| git / PRs | What changed in artifacts | Engineers |
| `CHANGELOG.md` | What shipped that users should know | Users |
| `docs/decisions/` | Why a binding choice was made | Future us |
| `docs/wiki/log.md` | Ingests, lints, filed answers | Wiki operators |
| `docs/log.md` | Belief flips, external events, failed bets that are not commits | Humans reconstructing the project |

Create `docs/log.md` only when one of those events happens and would otherwise vanish into chat.

**Atomic notes vs one architecture file.**  
Beliefs that will be cited and revised should be atomic *when you have more than a handful*. Until then, a well-headed `docs/architecture.md` plus ADRs is enough. Split when a file answers two questions or exceeds a sitting.

**Agents write the wiki vs humans own truth.**  
Agents may draft. Durable promotion requires a review gate (§5.3). The model proposes. The system constrains. A human accepts anything that will be treated as team belief or a binding decision.

---

## 4. What was missing from every prior answer

1. **An authority model.** Files without a trust level will be cited as if they were equal.
2. **Write permissions.** Who may create, edit, or only propose a change to each kind.
3. **Session state vs project attention.** Compaction memory is not the sprint.
4. **Generated vs authored knowledge.** Code, schemas, and metrics already speak. Prose must not fork them.
5. **Provenance.** Compiled pages must not become sources. A quote is a pointer, not a new fact.
6. **Assumptions under decisions.** A decision is a living object: if an assumption dies, the decision is up for review. This is the missing link between a wiki and an ADR.
7. **Public vs private surfaces.** `README.md` may be the only file safe for outsiders.
8. **Mechanical anti-rot.** Dates, ID uniqueness, “prose must not invent fields,” stale-NOW detection.
9. **Monorepo and multi-repo scaling.** Nested protocol files; a parent that only maps.
10. **Machine-local agent memory is not the repo.** Claude auto-memory, Cursor memories, and chat transcripts are not institutional knowledge unless promoted.
11. **Conflict protocol.** Two sources of truth is a bug with a resolution path.
12. **Skills as procedures, not beliefs.** A release checklist is not a claim about the domain.

---

## 5. The model

### 5.1 Seven kinds of information

| Kind | Question | Mutability | Default home |
|---|---|---|---|
| **Protocol** | How do we operate here? | Slow. Human-owned. | `AGENTS.md` (+ thin tool pointers) |
| **Identity** | What is this, why, for whom, not-for-what? | Slow. Edited rarely. | `README.md` (thin) + `docs/identity.md` when it outgrows a paragraph |
| **Evidence** | What did a source actually say? | Immutable | `docs/wiki/raw/` once the wiki ring exists. Do not also create `docs/sources/`. |
| **Belief** | What do *we* claim, with what confidence? | Edit in place; date the flip | `docs/architecture.md` first. Wiki pages if you are compiling sources. `docs/notes/` only if you have project claims and no wiki — never both for the same claims. |
| **Decision** | What did we choose, and why? | Append-only. Supersede, do not invert. | `docs/decisions/` |
| **Attention** | What are we doing *now*? | Volatile. Dated. | `docs/now.md` (project) + `PLAN.md` (session) |
| **History** | What happened that git will not tell you? | Append-only | `docs/log.md` and/or `docs/wiki/log.md` |

Almost every documentation failure is two kinds stuffed into one file.

### 5.2 Three writer classes

| Class | Writes | Examples |
|---|---|---|
| **Human-authored** | Protocol hard rules, identity, accepted decisions, social/legal interfaces | `AGENTS.md`, `docs/identity.md`, accepted ADRs, `LICENSE` |
| **Co-authored** | Current shape, attention, reviewed beliefs | `docs/architecture.md`, `docs/now.md`, glossary |
| **Agent-compiled** | Wiki pages, indexes, session plans, proposed ADRs, capture | `docs/wiki/pages/`, `PLAN.md`, `docs/capture/` |

### 5.3 Authority levels

Treat this table as law. Put a short version in `AGENTS.md`, plus the write-permission table in §6.1. How a draft becomes reviewed is §19.1 only.

| Level | Meaning | Examples | Agents may… |
|---|---|---|---|
| **0 Unverified** | Not citable as true | `docs/capture/`, chat, `PLAN.md`, scratch | Write freely. Never cite as fact. |
| **1 Draft** | Proposed | `docs/decisions/` with status `proposed`; unreviewed wiki pages | Create. Label as draft. |
| **2 Reviewed** | Team-true, dated | Accepted ADRs, reviewed wiki pages, `docs/architecture.md` | Propose edits. Do not silently rewrite. |
| **3 Generated** | True because a command produced it | OpenAPI, migrations, types, coverage | Read. Never hand-edit. Point, don’t transcribe. |
| **4 Constitutional** | Changes the project if it changes | Identity, `AGENTS.md` hard rules, license, threat boundaries | Never change without an explicit human ask. |

### 5.4 Two clocks

- **Session clock** — this agent loop, this compaction window. Lives in `PLAN.md` (overwritten, not accumulated). Gitignore it if it is noise; commit it only when a human must hand a loop to another human or agent.
- **Project clock** — this week’s intent. Lives in `docs/now.md`. Committed. Has an `updated` date. If the date is older than the review cadence, the file is *wrong by definition*.

Do not keep `TODO.md`, `BACKLOG.md`, `SCRATCHPAD.md`, `ACTIVE_TASK.md`, and `NOW.md` at once.

### 5.5 Kernel and rings

```
                    ┌─────────────────────────────────────┐
                    │  KERNEL (day one)                   │
                    │  README.md                          │
                    │  AGENTS.md          [if any agent]  │
                    │  Compatibility pack [software/agents]│
                    │    CLAUDE.md → @AGENTS.md           │
                    │    GEMINI.md → @AGENTS.md           │
                    │    .github/copilot-instructions.md  │
                    └──────────────┬──────────────────────┘
                                   │ first real instance
          ┌─────────────┬──────────┼──────────┬──────────────┐
          ▼             ▼          ▼          ▼              ▼
     Cognition      Decisions   Procedures  Interfaces    Compilation
     identity       ADRs        skills/     CONTRIBUTING  wiki/raw
     architecture   proposals   playbooks   CHANGELOG     wiki/pages
     now            assumptions SECURITY    CODE_OF_CONDUCT index + log
     schema-intent                          LICENSE
          │
          ▼
     capture/   (always a habit; folder only when inbox exists)
     archive/   (when a whole line of work dies or ships forever)
```

**Birth rule.** Do not create a ring until the first real inhabitant exists. Do not create `docs/decisions/` the day you open the repo. Create it the day you make a choice you would hate to re-litigate.

---

## 6. Default layout (roles, not a dump)

The tree below is a **role catalog**. It is not a create-list. Create a path only when the birth rule in §5.5 is satisfied.

`docs/schema.md` and `docs/wiki/SCHEMA.md` are different files. The first is *why the product data model looks this way*. The second is *how to operate the wiki*. Never merge them.

```
.
├── README.md                         # Human door. Thin.
├── AGENTS.md                         # Protocol hub. Short. Routing table lives here.
├── CLAUDE.md                         # [compat] @AGENTS.md
├── GEMINI.md                         # [compat] @AGENTS.md
├── PLAN.md                           # Session attention. Overwritten. Gitignore unless handing off a loop.
├── LICENSE                           # If the project has one
├── out/                              # [expression] first time something is for other people
│
├── .github/
│   └── copilot-instructions.md       # [compat] pointer → AGENTS.md
├── CONTRIBUTING.md                   # [interface] second contributor or public repo
├── CHANGELOG.md                      # [interface] first user-facing release
├── SECURITY.md                       # [interface] public / multi-user
├── CODE_OF_CONDUCT.md                # [interface] community
│
└── docs/
    ├── identity.md                   # [cognition] when README cannot hold the constitution
    ├── now.md                        # [attention] committed weekly intent
    ├── log.md                        # [history] only if git is not enough
    ├── architecture.md               # [belief] current shape; split when too long
    ├── schema.md                     # [belief] product data-model *intent*; points at generated truth
    ├── glossary.md                   # [belief] when a term is argued twice
    ├── decisions/                    # create on first real decision — no empty template file
    │   ├── _index.md                 # table: id, title, status, date, supersedes
    │   └── 0001-<slug>.md
    ├── skills/                       # [procedure] on-demand recipes
    │   └── <task>.md
    ├── work/                         # [motion] first work package that will outlive a week
    ├── capture/                      # [unverified] first time you need an inbox
    │   └── inbox.md
    ├── wiki/                         # [compilation] only if you accumulate sources
    │   ├── SCHEMA.md                 # wiki operator protocol (ingest / query / lint)
    │   ├── index.md
    │   ├── log.md
    │   ├── raw/                      # immutable sources
    │   └── pages/
    └── archive/                      # frozen. do not edit.
```

**Compatibility pack** (software / agent-using repos). Create the thin pointers in §18 so Claude Code, Gemini CLI, and Copilot surfaces that still prefer their native filename all load the same hub. Do not copy `AGENTS.md` into those files.

**Tool-specific extras** (only when the feature is real, not for coverage):

- Cursor glob-scoped rules: `.cursor/rules/*.mdc` — Cursor already reads `AGENTS.md`; use this only for path-scoped extras
- Aider: `.aider.conf.yml` with `read: AGENTS.md` if Aider is in use
- Continue: `.continue/rules/project.md` pointing at `AGENTS.md` if Continue is in use and does not pick up the hub
- Cline / Windsurf / Devin path-scoped rules: their `rules/` directories — only for glob-scoped extras; they read `AGENTS.md`

Do not create legacy `.cursorrules`, `.windsurfrules`, or `.clinerules` if `AGENTS.md` plus the compatibility pack already covers that tool.

### 6.1 File jobs (kernel and first rings)

**`README.md`** — Get a stranger to competence or to the right next file. One paragraph of what/who; the first successful path to run or read; links inward; license/contact if they matter. Not history, not architecture, not every install option.

**`AGENTS.md`** — The protocol. Target well under 200 lines (Claude’s own guidance is the same). Contains: install/dev/test/lint commands; hard don’ts; a routing table; authority rules; write permissions. Does **not** contain architecture essays, schema fields, or a copy of the README.

**`CLAUDE.md`** — First line `@AGENTS.md`. Then only Claude-specific mechanics (hooks, subagents, plan-mode policy). Never a second copy of the facts. Required in the compatibility pack because Claude Code does not read `AGENTS.md` natively.

**`GEMINI.md`** — First line `@AGENTS.md`, plus one sentence that `AGENTS.md` is the source of truth. Gemini CLI’s default filename is still `GEMINI.md`; the pointer makes a teammate’s default install work without editing `settings.json`.

**`.github/copilot-instructions.md`** — One paragraph pointing at `../AGENTS.md`. Needed for Copilot surfaces that still treat this file as primary (some IDE hosts, some review paths). VS Code Copilot and Copilot coding agent also read `AGENTS.md` directly.

**`PLAN.md`** — Current loop only. Objective, steps, blockers. Overwrite next session. Not a diary.

**`docs/now.md`** — Project attention: 1–3 outcomes, next actions, blocked, do-not-do, horizon dates. Link the issue tracker. Do not clone it.

**`docs/identity.md`** — Intent, problem, scope and non-goals, success, constraints, principles, ownership. Change slowly. Material edits earn a log line and often a decision.

**`docs/architecture.md`** — How it fits together *now*. Boundaries, data flow, invariants. Views (context / containers / components / runtime / threats) start as headings. They become separate files only when the parent cannot be read in a sitting.

**`docs/schema.md`** — Intent of the *product* data model. Links to the generated source of truth. Records constraints the generator cannot express. Not the wiki operator file.

**`docs/decisions/NNNN-slug.md`** — One choice per file. Title is a choice, not a topic (“Use Postgres for the system of record,” not “Database”). Status: `proposed` | `accepted` | `superseded by NNNN` | `deprecated`. Once accepted, do not invert it in place.

Every accepted decision lists **assumptions** that would force a revisit. That is the join between compilation and cognition: new evidence is tested against assumptions, not against vibes.

**`docs/skills/<task>.md`** — One recurring job. A migration runbook, a release checklist, a “how we cut a hotfix.” Loaded on demand. If you have explained the same procedure to an agent twice, it has earned a skill.

**`docs/wiki/`** — Karpathy’s three layers, named honestly:

- `raw/` — immutable sources. Humans (or ingest tools) add. Agents never edit.
- `pages/` — compiled, interlinked Markdown. Agents write. Humans review before a page is Level 2.
- `SCHEMA.md` — ingest / query / lint / file-back-answers. This is the wiki’s protocol. `AGENTS.md` points here; it does not duplicate it.
- `index.md` — catalog with one-line summaries. Read first at query time.
- `log.md` — append-only wiki operations, newest first, greppable prefixes.

**`docs/capture/inbox.md`** — Undated bullets. Not citable. Weekly empty-or-promote.

**`docs/archive/`** — Fossils. A one-line README: frozen on DATE. Do not rewrite the past to match the present.

---

## 7. Information flow

```
 world / chat / papers / incidents
              │
              ▼
        capture/  ─────────────── unverified
              │
              │ promote
              ▼
     ┌────────┴─────────┐
     │                  │
  evidence            motion
  (wiki/raw)          (now, PLAN, work)
     │                  │
     │ compile          │
     ▼                  ▼
  beliefs            decisions
  (architecture,        │
   wiki pages,          │ accepted
   notes)               ▼
     │            current-state view
     │            (architecture.md)
     └──────────┬───────┘
                │
                ▼
         expression (README, out/docs, paper, changelog)
                │
                ▼
         history tapes (git, changelog, docs/log, wiki/log)
                │
                ▼
              archive/
```

**What moves along this diagram.** Authority is §5.3. The 1→2 bar is §19.1 (and only there). Flow-specific rules that are not in those sections:

- A source note restates the source. A belief note states *our* claim and links the source.
- When a belief reverses, edit the belief, date the flip, add a history line, and check every decision whose assumptions cite it.
- User-facing docs (`out/`, Diátaxis, papers, briefs) are compiled from reviewed beliefs. If they disagree with a reviewed belief, the belief is updated first or the publication is wrong.

**Proposal pipeline (from Nexus, kept)**

```
capture or research → docs/decisions/NNNN (status: proposed)
                   → accepted
                   → update docs/architecture.md (and wiki pages if any)
                   → one history line
```

A proposal is not a work package. A work package is committed execution. If you need work packages as documents, create `docs/work/` on the first one that will outlive a week. Two-hour tasks are checkboxes in `docs/now.md`.

---

## 8. Anti-rot (ritual + mechanics)

**Human cadence (keep this small or it will not happen)**

- Empty capture. Update `docs/now.md` so it matches reality.
- If a choice was made in chat, write or supersede a decision.
- If a belief flipped, date it and log it.
- Fix the routing table if a new hub cannot be reached in one hop from `AGENTS.md` or `README.md`.

**Mechanical checks**

Run `python3 scripts/lint_knowledge.py --strict` (or the copy `--init` wrote). Tests: `python3 -m unittest tests.test_lint_knowledge`. `--version` prints the embedded version; a vendored copy is stale when that string does not match the pin you intended. Re-vendor with `curl -fsSL -o scripts/lint_knowledge.py` from the tag URL in `--version` JSON (`pin`), then run `--version` again. There is no auto-update.

The script fails on anti-files, empty rings, duplicate decision IDs, accepted ADRs without Assumptions, one-way supersede links, `_index.md` rows that disagree with a file on status / date / supersedes, missing `type:` on conventional paths, wiki pages without a source pointer, fat pointers, dual `CLAUDE.md`, broken relative links and missing `#anchors`, and — under `--strict` — a stale `docs/now.md`. `--init` writes Tier 1 only.

**Promotion hook (CI, not the tree linter).** `python3 scripts/lint_knowledge.py --promotion-base <sha>` fails if the diff lands a decision at `Status: accepted` (a flip, or a new file), **or** if it deletes / moves out of the ring a decision whose last seen status is `accepted` or `superseded` (or whose status is not in the hunk — treated as protected). The match is case-insensitive and allows space before the colon. On GitHub: `human-accepted` + `--allow-promotion` for a promotion; `human-removed` + `--allow-deletion` for a removal. Do not stretch one label over both. The labels are human claims, not proof of thought. The job runs only on `pull_request`; a direct push to `main` is not this hook, and is not branch protection. Kind-mixing inside a typed file, and a belief flip with no `docs/log.md` line, stay human review. Do not claim the script reads those.

When you add more CI of your own: fail if `docs/schema.md` names a field the generated schema does not have.

**Conflict protocol**

If two files both claim a fact:

1. The source-of-truth matrix (§9) decides the winner.
2. Delete or reduce the loser to a pointer.
3. Log one line. This is a bug, same severity as a failing test.

**Ownership**

At spark stage, ownership can be a single line in `docs/identity.md` or `README.md`. From the compounding stage on, accepted decisions and hub files name an owner. Unowned files at that stage are treated as history, not truth. Do not sprinkle empty `owners: []` frontmatter on day one.

---

## 9. Source-of-truth matrix

Put a short form of this in `AGENTS.md`. Expand it in `docs/identity.md` or at the top of `docs/architecture.md` if the matrix grows.

| Fact | Lives in | May be summarized in | Never copied to |
|---|---|---|---|
| How to operate (commands, don’ts) | `AGENTS.md` | tool pointers (one line) | README essays |
| What this is / scope / non-goals | `README.md` or `docs/identity.md` | README first paragraph | NOW, ADRs |
| What we are doing this week | `docs/now.md` | standup | identity |
| What *this loop* is doing | `PLAN.md` | nothing | now.md, git history |
| What shipped to users | `CHANGELOG.md` (prefer generated) | release notes | LOG as a clone |
| A binding choice | `docs/decisions/NNNN` | one line in history | wiki essays |
| Assumptions under a choice | the decision file | wiki only as links | chat |
| Current shape of the system | `docs/architecture.md` | README | a second “overview” |
| Why the data model is this way | `docs/schema.md` | — | field-by-field clones |
| The actual fields / endpoints | generated artifact | — | `schema.md` |
| What a source said | `docs/wiki/raw/` (+ source note) | — | belief pages as if it were ours |
| What we believe | reviewed belief / wiki page | papers, briefs | decisions (except as context links) |
| How to do a recurring job | `docs/skills/` | — | AGENTS.md (beyond a link) |
| Task state | issue tracker | counts in now.md | LOG, BACKLOG.md |
| Who owns what | `docs/identity.md` + CODEOWNERS | — | everywhere else |

---

## 10. Agent protocol (put this in `AGENTS.md`)

Every session:

1. Read `AGENTS.md`. Follow its commands and don’ts.
2. Read `docs/now.md` if it exists (project attention).
3. Read `docs/identity.md` only when the task can change scope or meaning.
4. Treat accepted decisions as constraints. Treat `docs/architecture.md` as current shape.
5. Treat `docs/capture/`, `PLAN.md`, unreviewed wiki pages, and chat as Level 0–1 (§5.3). Do not flip a draft to accepted (§19.1).
6. Prefer generated artifacts over prose when they disagree.
7. For any task that will touch more than two files, write `PLAN.md` before editing.
8. Run the targeted test (or equivalent check) before declaring done.
9. Do not add dependencies, edit generated code, or rewrite accepted decisions unless the human asked.
10. Do not commit secrets, credentials, `.env` values, or personal data into any knowledge file.
11. After non-trivial work, *propose* patches. Do not silently edit Level 2–4 files.

**Monorepos.** Nested `AGENTS.md` files are valid. The nearest file to the edited path wins. The root file holds repo-wide commands and the matrix. Package files hold local commands and don’ts. Do not copy the matrix into every package.

**Subagents.** They inherit protocol. They do not inherit a stale chat plan unless `PLAN.md` is on disk. That is why the session file exists.

---

## 11. Decision record (the one template that matters)

```markdown
# 0007. Use Postgres for the system of record

Status: accepted
Date: 2026-08-16
Deciders: …
Supersedes: —
Superseded-by: —

## Context
The forces in play. Link beliefs and sources. No novel research here.

## Options
- A …
- B …
- C …

## Decision
We will …

## Assumptions
- [A1] Write volume stays under … (revisit if exceeded)
- [A2] Relational integrity remains a product requirement
Each assumption is falsifiable. New evidence is tested against these.

## Consequences
What this buys, what it costs, what we are now forbidden from pretending.

## Revisit if
Observable triggers, not “someday.”
```

Once accepted: clarify wording if you must. Do not invert the choice. A new file supersedes it, both IDs linked.

---

## 12. Scale without a rewrite

| Stage | What exists | What you refuse |
|---|---|---|
| **Spark** (hours–days) | `README.md`. Add `AGENTS.md` (and the §18 pack, if software) the first time an agent touches the repo. | Folders “for later,” empty ADRs, a wiki |
| **Alive** (weeks) | First decision, `docs/now.md`, maybe `docs/architecture.md` | A second README, Notion as the real wiki, `TODO.md` |
| **Compounding** (months) | Decision index, skills you have taught twice, glossary | Topic folders, DESIGN.md megafile, hand-maintained FILES.md |
| **Multi-stream** | Several work notes or a tracker; architecture split by view | Status copied into Slack as truth |
| **Knowledge-heavy** | Wiki ring: raw / pages / index / log / SCHEMA. When `index.md` no longer fits in one read, add local search — do not start with embeddings. | Letting compiled pages become sources |
| **Institutional** | Generated indexes, CI anti-rot, yearly log split, archive, owners | A docs team that writes a parallel universe |
| **Family of projects** | Each repo has this kernel. A parent repo is only a map + identity | One mega-vault for all products |

**Growth mechanism.** Add nodes inside known rings. A new *kind* is a constitutional event: write a decision, update the matrix.

**IDs.** Start sequential decision numbers when you create the first ADR. Adopt `K`/`S`/`W` IDs when notes outnumber what a human can hold (~30–80). Never reuse an ID. The slug may change; the ID may not.

**Splitting a project.** Clone the kernel. Move the relevant decisions and beliefs. Leave stubs: “Moved to repo Y as 0014.” Archive, do not silently delete.

---

## 13. Domain adapters (same kinds, different muscles)

**Software / AI product.** Kernel is `README.md` + `AGENTS.md` + the §18 compatibility pack. Rings: architecture, schema-intent, decisions, skills, now. Wiki only if you are also compiling research or incident knowledge. Diátaxis lives in user docs, not in the kernel. Generated API reference is generated.

**Research / academic.** Kernel is `README.md` + `docs/identity.md` + `docs/now.md`. Wiki ring is first-class. `raw/` is literature and datasets. Work notes are experiments. Results that will be cited become reviewed beliefs. The paper is `out/`, compiled from beliefs + evidence. Lab days may use dated capture files. Big data stays out of git; store paths and hashes.

**Hardware / field / safety.** Same cognition. Safety-critical choices are decisions with explicit `revisit if`. Operator procedures live in expression (`out/` or a controlled procedure system). The *why* stays in beliefs + decisions.

**Business / product.** Identity is strategy. Beliefs are customer insights and economic models (low-confidence beliefs are still beliefs, not decisions). Decisions are bets. `docs/now.md` is the current initiative set. A board brief is expression.

**Personal / creative.** Five files is vanity. `README` or a single identity note + capture is enough. Add a wiki if you are actually compiling sources. Do not simulate a company.

**Standards / policy.** Normative text is expression. Rationale and rejected alternatives are decisions + beliefs. Do not interleave rationale into normative text without a home in beliefs or decisions.

---

## 14. What you should not create

| Anti-file | Why |
|---|---|
| `hot-cache.md` | Not a cache. Cargo cult. |
| Hand-maintained `FILES.md` that restates the tree | Stale map. Fold 10 rows into `AGENTS.md` or generate. |
| `TODO.md` + `BACKLOG.md` + `NOW.md` + issues | Four working memories |
| `NOTES.md` | Untyped landfill |
| `AI_CONTEXT.md` that restates everything | Agents read the kernel |
| Per-tool bibles that diverge | One protocol, many pointers |
| Full arc42 / ISO template on day one | Ceremony pretending to be clarity |
| Personal Zettelkasten copied into a product repo | Wrong boundary; link out |
| Empty `docs/decisions/` or empty `docs/wiki/` | Stub someone must notice is stale |
| A `CHANGELOG.md` hand-duplicated from git *and* `LOG.md` | Generate user-facing notes |
| Compiling wiki pages back into `raw/` | Self-citation. The wiki dies. |

`LICENSE`, `CITATION.cff`, `SECURITY.md`, `CODE_OF_CONDUCT.md` stay at root when the world expects them. They are interfaces, not organs.

---

## 15. Day-one templates

### `AGENTS.md` (software kernel)

```markdown
# Agent protocol

## Commands
- Install: `___`
- Dev: `___`
- Test (one file): `___`
- Test (full): `___`
- Lint / format: `___`

## Hard rules
- Do not add a dependency, edit generated code, or change a migration without an explicit ask.
- Do not commit secrets, credentials, or `.env` values into the repo or these docs.
- Minimal diffs. Touch only what the task requires.
- For work that will edit more than two files, write `PLAN.md` first.
- Run the targeted test before calling the task done.

Delete any "Where to read" row whose target does not exist yet.

## Authority
- Level 0 (not facts): `docs/capture/`, `PLAN.md`, chat
- Level 2 (constraints): accepted files in `docs/decisions/`
- Level 3 (prefer over prose): generated schemas and types
- Level 4 (do not edit unless asked): this file, `docs/identity.md`, `LICENSE`

## Write permissions
- Capture / `PLAN.md`: write.
- Proposed decisions: create; leave `proposed`.
- Accepted decisions, architecture, `docs/now.md`: propose a patch.
- `Status: proposed` → `accepted`: a named human only (PR label `human-accepted`).
- Do not delete an accepted or superseded decision (PR label `human-removed`).

## Where to read
| Need | File |
|---|---|
| What this is | README.md (and docs/identity.md if it exists) |
| What we are doing now | docs/now.md |
| How the system fits together | docs/architecture.md |
| Why a choice was made | docs/decisions/ |
| Data model intent | docs/schema.md |
| Recurring procedures | docs/skills/ |
| Compiled research | docs/wiki/index.md |

## After you finish
Propose, do not silently apply: a docs/now.md patch, a decision draft if you chose something, a one-line history note if git will not explain it.
```

### `CLAUDE.md`

```markdown
@AGENTS.md
```

### `docs/now.md`

```markdown
---
type: now
updated: YYYY-MM-DD
horizon: YYYY-MM-DD → YYYY-MM-DD
---

# Now

## Focus
1.

## Next
- [ ]

## Blocked

## Do not do
```

---

## 16. Why this shape lasts

Prior answers failed in three predictable ways:

- **Too software-shaped** — a pile of agent files that insult a thesis.
- **Too PKM-shaped** — a second brain that a product team will not keep alive, and that a coding agent will not load.
- **Too complete** — twenty templates so small projects drown and large ones still invent a shadow system.

This architecture lasts because it is **typed information + authority + a tiny kernel + rings with a birth rule**.

It is compatible with git, with Claude Code, with Codex, with a lab drive, with a single author, and with fifty. It lets `AGENTS.md` do what it is good at (protocol), ADRs do what they are good at (commitment), Diátaxis do what it is good at (teaching outsiders), and Karpathy’s wiki do what it is good at (compiling sources). It refuses to let any of them pretend to be the others.

The structure is not the directory tree. **The structure is the refusal to mix the seven kinds, the refusal to treat unverified text as true, and the refusal to create a file before it has an inhabitant.** Anti-files: §14.

---

## 17. Implementation contract

This section is the algorithm for applying the architecture to an existing repository. It does not add roles.

**Greenfield Tier 1 (skip the theory).** If the repo has no agent files yet and you only want the kernel:

```bash
curl -fsSL -o lint_knowledge.py \
  https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/v0.1.1/scripts/lint_knowledge.py
python3 lint_knowledge.py --init --install "…" --test "…"
python3 scripts/lint_knowledge.py --version
python3 scripts/lint_knowledge.py --strict
```

`--init` writes `AGENTS.md` (real commands, no README clone), the §18 pointers, and a copy of the script. It does **not** create `docs/`, decisions, or a wiki. The `v0.1.1` pin in `--version` JSON is live. Existing or messy repos still use Phase 1 inspect / Phase 2 apply below — `--init` will not map what you already have.

1. **Inspect first.** Inventory existing docs, agent files, package manifests, CI, issue tracker, and whether the project is software, research, mixed, or something else. Do not invent a parallel tree beside files that already play a role.
2. **Map, then create.** If `PROJECT.md`, `ARCHITECTURE.md`, `adr/`, `docs/adr/`, `DESIGN.md`, or similar already exist, keep them and treat them as the role they already play. Point `AGENTS.md` at those paths. Do not copy their contents into new files with the default names.
3. **Kernel only, unless a ring is already earned.**
   - Always ensure a human door (`README.md`). Thin it only if it has become a wiki; never gut a working quickstart.
   - Add `AGENTS.md` if any agent will work in the repo, or if one already does.
   - For software / mixed / any repo agents will open: install the **compatibility pack** in §18 (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`). Pointers only — never copies.
   - Add Aider / Continue / Cursor glob-rule files only if that tool is already present or the human asked for it.
   - Do not commit an empty `PLAN.md`. Mention it in `AGENTS.md`. Add it to `.gitignore` only if the team wants session files local.
4. **Earn each ring from evidence in the repo, not from this catalog.**
   - `docs/identity.md` — README cannot hold scope / non-goals / ownership without becoming a manifesto.
   - `docs/now.md` — there is current work that is not fully expressed by the issue tracker, or there is no tracker.
   - `docs/architecture.md` — someone has to explain how the system fits together, and no existing file already does.
   - `docs/schema.md` — there is a data model whose *intent* is not obvious from the generated artifact.
   - `docs/decisions/` — there is at least one choice you would hate to re-litigate. Write that decision. Add `_index.md` in the same step. Do not add `0000-template.md`.
   - `docs/skills/<task>.md` — the same procedure has been explained twice, or the repo already has a runbook worth relocating.
   - `docs/wiki/` — the project accumulates sources (papers, incidents, research) that should be compiled. Do not add a wiki to a plain product app.
   - `docs/capture/` — only if there is already a notes landfill to quarantine, or the user asked for an inbox.
   - `docs/log.md` — only if you are recording a belief flip or external event that git will not explain.
   - Interface files — only if the repo is public or already has contributors, or the file already exists.
5. **Fill from the repo, never from placeholders.** Commands in `AGENTS.md` must be the real install / test / lint invocations. Routing table rows must point at files that exist, or at files you created in this pass. Delete routing rows for rings you did not create.
6. **Do not add CI, hooks, or new dependencies** unless the user asked, or the repo already has CI and you are adding a small check they requested.
7. **Report.** List mapped existing files, created files, compatibility-pack files, deliberately deferred rings, and any conflict you resolved by pointer.

---

## 18. Tool compatibility

The architecture is portable because **facts live in one file** (`AGENTS.md`) and every other agent entrypoint is either a native reader of that file or a one-line pointer. Do not maintain parallel rulebooks.

### How loading actually works (2026)

| Tool | Reads `AGENTS.md` natively? | Extra file for coverage | Notes |
|---|---|---|---|
| OpenAI Codex CLI | Yes (primary) | — | Nested `AGENTS.md`; nearest wins |
| Cursor | Yes | `.cursor/rules/*.mdc` only for glob-scoped extras | Do not create legacy `.cursorrules` |
| GitHub Copilot (VS Code agent / coding agent) | Yes | — | Nearest `AGENTS.md` wins |
| GitHub Copilot (some IDEs, some review surfaces) | Unreliable | `.github/copilot-instructions.md` pointer | Compatibility pack |
| Gemini CLI / Gemini Code Assist | Configurable; default is still `GEMINI.md` | `GEMINI.md` pointer | Do not list both `AGENTS.md` and `GEMINI.md` in `context.fileName` if the latter imports the hub |
| Google Jules | Yes | — | |
| Google Antigravity | Yes (`AGENTS.md` and `GEMINI.md`) | Covered by pack | |
| Claude Code | **No** | `CLAUDE.md` with `@AGENTS.md` | Official pattern. Symlink works on Unix; import works on Windows |
| Windsurf / Cascade / Devin Desktop | Yes | `.windsurf/rules/` or `.devin/rules/` only for scoped extras | Do not create legacy `.windsurfrules` |
| Cline / Kilo Code | Yes (also `.clinerules/`) | — | |
| Amp, Factory, OpenCode, goose | Yes | — | |
| Zed, Warp, JetBrains Junie | Yes | — | |
| VS Code (agent customization) | Yes | Copilot pointer still useful | |
| Aider | Via config | `.aider.conf.yml` → `read: AGENTS.md` | Add if Aider is used |
| Continue | Rules in `.continue/rules/` | Thin rule pointing at `AGENTS.md` if Continue is used | |
| Kiro | Yes | `.kiro/steering/` only for Kiro-specific extras | |
| Grok / Grok Build | Yes | — | |

Skills stay on-demand. Default home is `docs/skills/`. Do not copy every skill into `.claude/skills/`, `.agents/skills/`, and Copilot skill folders. If a tool only discovers its own directory, add one pointer or one skill there that names `docs/skills/` — do not fork the recipes.

If both `CLAUDE.md` and `.claude/CLAUDE.md` exist, keep a single pointer (prefer the one already in use). Claude loads both and concatenates them.

Do not put large binaries in `docs/wiki/raw/`. Store a path and hash; keep the blob outside git.

### Compatibility pack (create these in software / agent-using repos)

These files contain **no facts**. If a fact appears in one of them, move it to `AGENTS.md`.

**`CLAUDE.md`**

```markdown
@AGENTS.md
```

**`GEMINI.md`**

```markdown
@AGENTS.md

All operational instructions live in AGENTS.md. Follow that file.
```

**`.github/copilot-instructions.md`**

```markdown
Refer to [AGENTS.md](../AGENTS.md) for all repository agent instructions. That file is the source of truth for commands, conventions, authority, and routing.
```

Optional, only if that tool is present:

**`.aider.conf.yml`**

```yaml
read: AGENTS.md
```

**`.gemini/settings.json`** — pick one, never both, or Gemini loads the hub twice:

- Default: commit `GEMINI.md` as a pointer and do **not** list both files in `context.fileName`.
- Or omit `GEMINI.md` and set `"context": { "fileName": "AGENTS.md" }`.

**`.continue/rules/project.md`**

```markdown
---
name: project
---
Follow AGENTS.md at the repository root as the source of truth.
```

### Rules that keep this from drifting

1. `AGENTS.md` is the only file that may grow.
2. Pointers stay under ~10 lines. If a pointer has grown, you have a second source of truth — cut it back.
3. If an existing native file already has unique, still-true rules, move the shared ones into `AGENTS.md` and leave only tool-specific mechanics in the native file (Claude hooks, Cursor globs, Copilot `applyTo` instruction files).
4. Nested `AGENTS.md` in a monorepo is the portable scoping mechanism. Prefer it over creating nested `CLAUDE.md` / `GEMINI.md` / Copilot files unless that tool will not see the nested hub.
5. Do not symlink `AGENTS.md` to five names as the only strategy. Claude’s `@` import is the documented Windows-safe path. Other tools get a one-line pointer so Git on Windows does not depend on symlink privileges.
6. When a new agent appears, check whether it reads `AGENTS.md`. If yes, do nothing. If no, add one pointer. Do not invent a new hub.

§18 is dated. If **Tool table review-by** on the title block has passed, treat the table as a hint, re-check loaders, and ship a spec minor version. Do not leave a year-old loader table unmarked.

---

## 19. Edges

### 19.1 Promoting Level 1 → Level 2

A draft becomes reviewed only when **all** of these hold:

1. A **named human** (the owner, or a decider listed on the file) sets status to `accepted` / `reviewed` and dates it.
2. The file is a single kind. If it answers two questions, split it first.
3. Claims that depend on evidence link those sources. Claims that depend on a choice link the decision.
4. For a decision: Context, Options, Decision, Assumptions (falsifiable), Consequences are present.
5. For a wiki page: it does not treat another Level 1 page as a source.

Agents may open the PR or edit the draft. They may **not** flip the status field to accepted, and they may **not** delete an accepted or superseded decision (supersede it). Self-promotion is a Level 0 action pretending to be Level 2. On GitHub, a PR that lands `Status: accepted` needs `human-accepted`; a PR that removes a protected decision needs `human-removed`. `lint_knowledge.py --promotion-base` enforces both. The labels are human claims, not a substitute for the five bullets above.

### 19.2 Ownership handoff

- Record the new owner on the file (or in `docs/identity.md` for the whole project) and the date.
- The previous owner does not stay as a ghost authority. If they must remain a decider, say so explicitly.
- Unowned Level 2+ files at compounding stage are treated as history until someone claims them. Do not silently keep editing them as if they were live.

### 19.3 Conflicting evidence

When two sources cannot both be true of the same claim:

1. Keep both Evidence files. Evidence is immutable; do not “fix” a source to match the belief.
2. State the conflict on the Belief file: what each source says, what we currently hold, and the confidence.
3. If a Decision’s assumption is now in doubt, mark that decision `revisit` (or write a superseding draft). Do not invert the old decision in place.
4. One line in `docs/log.md` (this is an event git will not explain).

The Belief is allowed to pick a side. The Evidence layer is not allowed to forget the loser.

### 19.4 Non-Markdown artifacts

Diagrams, notebooks, spreadsheets, slides, and binaries are not first-class kinds. Rules:

- **Generated** (build output, exported API, rendered diagrams from source) → Level 3. Point; do not hand-edit.
- **Authored binary** (a Figma export, a recorded talk, a dataset) → store outside git if large; in-repo keep a Markdown stub of the right kind that links the path or URL and the hash.
- **Notebooks** that mix claim, experiment, and scratch → the notebook is capture or a work record until a Belief or Decision is cut out of it.
- Do not invent `docs/diagrams/` as a kind. The kind is the question the artifact answers.

### 19.5 This specification’s own clocks

| Field | Where | Cadence |
|---|---|---|
| Spec version | title block of this file, [CHANGELOG.md](../CHANGELOG.md) | Breaking change = major; new ring or edge = minor; wording = patch |
| `updated` | title block | Every accepted edit |
| Tool table review-by | title block | 90 days or the next loader surprise, whichever first |

Shipped versions of this spec live on git tags (`v0.1.0`, …). **Published tags are never moved.** Once outsiders pin `.../v0.1.0/docs/...`, that tree is frozen; later work is `v0.1.1+`. Do not rewrite `main` in a way that requires moving those tags. The implement prompt must keep working against a pinned tag.

---

## 20. Sources

Empirical claims in §1 and §18. Retrieved 2026-08-17. The architecture’s own evidence rule applies here: a claim without a pointer is a vibe.

| ID | Claim in this spec | Source |
|---|---|---|
| **S1** | Karpathy’s LLM Wiki, April 2026 | [gist `llm-wiki.md`](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (created 2026-04-04). Earlier public note: [X, 2026-04-02](https://x.com/karpathy/status/2039805659525644595). |
| **S2** | `AGENTS.md` donated to the Linux Foundation / Agentic AI Foundation, December 2025 | [Linux Foundation press release, 2025-12-09](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation); [OpenAI, same day](https://openai.com/index/agentic-ai-foundation/); steward home [aaif.io](https://aaif.io/). |
| **S3** | `AGENTS.md` used in 60k+ repositories; nested files, nearest wins | [agents.md](https://agents.md/) (“used by over 60k open-source projects”; [GitHub code search](https://github.com/search?q=path%3AAGENTS.md+NOT+is%3Afork+NOT+is%3Aarchived&type=code)). Nearest-wins is in the same page’s FAQ. |
| **S4** | README clones / repository overviews in `AGENTS.md` do not help, and context files raise cost | Gloaguen, Mündler, Müller, Raychev, Vechev, *Evaluating AGENTS.md*, [arXiv:2602.11988](https://arxiv.org/abs/2602.11988) (v2, 2026-06-23): context files do not generally improve task success and increase inference cost by over 20%; “repository overviews, although popular … are not helpful.” The spec does **not** claim a measured drop from any one duplicated paragraph — it claims the failure mode the paper measured. |
| **S5** | Claude Code reads `CLAUDE.md`, not `AGENTS.md`; official bridge is `@AGENTS.md` (or a symlink; import on Windows) | [Claude Code memory docs](https://code.claude.com/docs/en/memory) (section “AGENTS.md”). |
| **S6** | Claude auto-memory is machine-local, not the team knowledge base | Same [memory docs](https://code.claude.com/docs/en/memory): auto-memory writes `MEMORY.md` in the local Claude project directory. |
| **S7** | Keep the always-on protocol file short (~200 lines) | [Claude Code features overview](https://code.claude.com/docs/en/features-overview): “Keep CLAUDE.md under 200 lines.” This spec applies the same budget to `AGENTS.md`, the file that actually loads in portable setups. |

§18’s tool table is a dated survey (see **Tool table review-by**), not a second evidence appendix. When a loader fact in that table changes, update the table and this section in the same edit.
