# Design history (Grok 4.6)

Project note for continuing this repository. **Not** part of the knowledge architecture.

The spec is [docs/knowledge-architecture.md](../docs/knowledge-architecture.md).

Produced with Grok 4.6 (xAI) in August 2026.

---

## Starting point

The problem was well-known and poorly solved: teams were copying long lists of Markdown files “for AI agents,” then maintaining conflicting copies for each tool. Several published answers already existed. They disagreed.

The inputs that had to be reconciled:

1. A **maximal file list** for 2026 agentic repos — `README`, `AGENTS`, `CLAUDE`, `GEMINI`, `FILES`, `DESIGN`, `SKILL`, `ARCHITECTURE`, `SCHEMA`, a Karpathy-style wiki (`index.md`, `log.md`, `hot-cache.md`), OSS compliance files, and `PLAN` / `TODO` / `BACKLOG`.
2. **Hub-and-spoke** — `AGENTS.md` as the single source of truth; tool-specific files as pointers.
3. **Spine** — a domain-agnostic knowledge OS: five information kinds (identity, truth, decision, motion, history); a tiny core; organs (`decide/`, `know/`, `do/`, `out/`, `capture/`, `archive/`) created only when inhabited.
4. **Nexus** — a software-docs tree: current-state architecture, immutable ADRs, operations, research, AI context, `_INDEX` tables.
5. A **minimal agent-first** position — only `README.md` and `AGENTS.md` are non-negotiable; most of the PKM apparatus is ceremony a coding agent will not load.

The work was to keep what survives contact with real tools and real projects, and discard cargo cult.

---

## Research before the spec

Claims in those answers were checked against primary sources, not restated from blogs.

- **[AGENTS.md](https://agents.md/)** and the Linux Foundation **Agentic AI Foundation** (December 2025): portable “README for agents,” nested files, nearest wins. Native in Codex, Cursor, Copilot coding agent, Gemini (configurable), Jules, Amp, Factory, OpenCode, goose, Zed, Warp, Junie, Windsurf/Devin, Cline, Kiro, and others.
- **Claude Code memory documentation:** Claude reads `CLAUDE.md`, not `AGENTS.md`. Official workaround: first line `@AGENTS.md`, or a symlink on Unix. Windows should use the import. Auto-memory on a local machine is not the team knowledge base.
- **Karpathy’s [llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) gist (April 2026):** three layers — immutable raw sources, an LLM-maintained wiki, and a schema for ingest / query / lint. `index.md` is a catalog; `log.md` is a tape of wiki operations. There is no `hot-cache.md`. The pattern compiles *sources*; it is not a software-repo file list.
- **ADRs** (Nygard / Fowler): one decision per file; supersede, do not silently invert.
- **GitHub Copilot:** the coding agent and VS Code can read `AGENTS.md`; some IDE and review surfaces still treat `.github/copilot-instructions.md` as primary.
- **Gemini CLI:** default context file is still `GEMINI.md`; `settings.json` can point at `AGENTS.md`. Listing both *and* importing the hub loads the hub twice.

That is why “put a Karpathy wiki in every CRUD app” and “`hot-cache.md` makes agents faster” were rejected, and why Claude / Gemini / Copilot files exist only as a pointer pack.

---

## What was kept, dropped, and resolved

**Kept**

- Human door (`README.md`) vs agent protocol (`AGENTS.md`).
- One hub, many pointers — no divergent tool bibles.
- Progressive disclosure: the always-loaded file stays short; depth is linked.
- On-demand skills instead of one `SKILL.md` novella.
- Session working memory so compaction and subagents do not lose the plot.
- Typed information: identity ≠ belief ≠ decision ≠ attention ≠ history.
- Create on first real instance. An empty `docs/decisions/` is worse than no folder.
- A source-of-truth matrix.
- Capture as quarantine, not authority.
- Proposal → accepted ADR → update the current-state view.
- ADRs are append-only; a new file supersedes the old.
- OSS files (`CONTRIBUTING`, `CHANGELOG`, `SECURITY`, `CODE_OF_CONDUCT`) are interfaces, not knowledge organs.
- A brand-new software repo can start with two files; everything else is earned.
- Karpathy: raw immutable, wiki derived, answers filed back, lint for contradictions.

**Dropped**

- `hot-cache.md` — models have no fast path for that name.
- Hand-maintained `FILES.md` — goes stale, then causes hallucinations.
- `TODO.md` + `BACKLOG.md` + `SCRATCHPAD.md` stacked on `NOW` and an issue tracker — five working memories.
- Mandatory `LOG.md` that clones git.
- A Zettelkasten inside every product repo on day one.
- Full Spine / Nexus directory ceremony as the default.
- Transcribing generated schemas into prose.
- A new hub per tool.

**Contradictions resolved**

- Universal vs software-shaped → kinds are universal; default paths lean software; roles can move.
- Minimal vs comprehensive → the kernel is small; comprehensiveness is the catalog of roles you may grow, plus a birth rule.
- `AGENTS.md` vs `MAP.md` → one router. If agents exist, the table lives in `AGENTS.md`.
- Wiki log vs git vs changelog vs project log → four tapes; create `docs/log.md` only when git will not explain the event.
- Agents write the wiki vs humans own truth → agents draft; promotion to team-true or binding decision needs a review gate.

**Gaps the earlier answers did not close**

Authority levels, write permissions, session clock vs project clock, generated vs authored knowledge, provenance (compiled pages must not become sources), assumptions under decisions, public vs private surfaces, mechanical anti-rot, monorepo and multi-repo scale, machine-local agent memory ≠ the repo, conflict protocol, skills as procedures not beliefs.

---

## The specification

[docs/knowledge-architecture.md](../docs/knowledge-architecture.md) is the spec. [README.md](../README.md) is only the door.

Organizing rule:

> Keep protocol, identity, evidence, belief, decision, attention, and history in different homes — then grow a file only when a real instance of that kind appears.

| System | Job | Typical files |
|---|---|---|
| Protocol | How to operate here | `AGENTS.md` + pointers |
| Cognition | What this is, what we believe, what we chose, what we are doing | identity, architecture, decisions, `docs/now.md` |
| Compilation | Compounding picture of sources | `docs/wiki/` — only if the project accumulates sources |

Seven kinds. Five authority levels (0 unverified → 4 constitutional). Two clocks (`PLAN.md` = this loop; `docs/now.md` = this week).

The layout tree is a **role catalog**, not a create-list. Empty rings are a failure. Existing `PROJECT.md`, `ARCHITECTURE.md`, or `adr/` keep their paths; the router points at them.

This repository does not contain twenty empty templates. That would violate the spec.

---

## Implementation contract and prompt

A first implementer pass found traps that would cause a model to materialize the whole tree. Those were closed in the spec:

- Tree marked as a role catalog.
- `docs/schema.md` (product data-model intent) distinguished from `docs/wiki/SCHEMA.md` (wiki operator protocol).
- `0000-template.md` and empty committed `PLAN.md` forbidden.
- Ownership not required as empty frontmatter on day one.
- **§17 Implementation contract** — inspect → map → kernel → earned rings → fill from the repo → report.

[docs/implement-prompt.md](../docs/implement-prompt.md) is a paste-ready prompt for applying the spec inside another repository. It is self-contained if the spec is not attached, and defers to the spec if it is. It requires real commands, live routing rows only, and a report of what was mapped, created, deferred, and conflicted.

---

## Tool compatibility

Popular CLIs and IDEs do not all load the same filename. **§18** records how loading actually works in 2026.

**Native `AGENTS.md` (no extra file):** Codex, Cursor, Copilot coding agent / VS Code agent, Jules, Amp, Factory, OpenCode, goose, Zed, Warp, Junie, Windsurf / Cascade / Devin Desktop, Cline / Kilo, Kiro, Grok.

**Compatibility pack** for software and other agent-using repos — pointers only, no facts:

- `CLAUDE.md` → `@AGENTS.md` (Claude Code still does not read `AGENTS.md`)
- `GEMINI.md` → `@AGENTS.md` (Gemini CLI still defaults to this name)
- `.github/copilot-instructions.md` → link to `AGENTS.md` (some Copilot IDE and review surfaces)

Add Aider, Continue, or glob-scoped Cursor / Windsurf rules only when that tool is present. Do not create legacy `.cursorrules`, `.windsurfrules`, or `.clinerules` for coverage.

---

## Final review

A last pass did not change the model. It closed remaining implementer bugs:

| Gap | Fix |
|---|---|
| Software kernel listed only README + AGENTS + CLAUDE | Aligned with the three-file pack |
| Gemini settings listing both files while `GEMINI.md` imports the hub | Either/or — never both |
| Both `CLAUDE.md` and `.claude/CLAUDE.md` | Keep a single pointer |
| No secrets rule | No secrets, credentials, or `.env` values in knowledge files |
| Routing table showed every ring | Delete any row whose target does not exist |
| Wiki scale stopped at “add pages” | When `index.md` no longer fits in one read, add local search; do not start with embeddings |
| Skills copied into every tool directory | One home (`docs/skills/`); pointer only if a tool cannot see it |
| Large binaries in `wiki/raw/` | Path and hash; blob stays out of git |

Left out on purpose: replacing the issue tracker or CI; enforcing policy in Markdown (hooks enforce); enterprise RAG on day one; a `DESIGN.md` blob; a file per new IDE.

---

## Repository contents

See [docs/this-repo.md](../docs/this-repo.md) for the current layout. v0.1.0 applies the architecture to this repository and adds a kernel page, a linter, and adoption files.

To apply the architecture elsewhere: open a session in the target repository and give the model the implement-file URL (or the short paste block in `README.md`). The prompt fetches the spec from the same GitHub repo and applies it to the current tree.

| If you want… | Read |
|---|---|
| What the system is | [docs/knowledge-architecture.md](../docs/knowledge-architecture.md) |
| How to install it in another repo | [docs/implement-prompt.md](../docs/implement-prompt.md) |
| Why it looks this way | This file |
| A one-screen on-ramp | [README.md](../README.md) |
