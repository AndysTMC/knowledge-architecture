# Changelog

All notable changes to this specification are recorded here. Spec versions are git tags.

## 0.2.0 — 2026-10-27

Minor version per §18 (loader re-check) and because the gate reports failures it previously missed. JSON output and CLI flags are unchanged. Decision 0004 accepted by AndysTMC.

- Decision gate: `--promotion-base` no longer passes silently when Git config sets `color.diff`/`color.ui` to `always`, and no longer crashes under `diff.noprefix` or `diff.mnemonicPrefix`. It diffs only decision directories, with paths relative to `--root`, so a package root now gates its own ring. A supplied diff with terminal color codes is rejected.
- **New failures adopters may see:** a package-level `--promotion-base` run now reports promotions, edits, and deletions it previously missed; a colored `--promotion-diff` input is an error; a lint `--root` that is not a directory is an error instead of an empty pass.
- Fewer false findings: a UTF-8 BOM no longer hides frontmatter; a `CLAUDE.md` (or other pointer) symlinked to `AGENTS.md` passes; setext, indented, and linked headings produce their GitHub anchors; links inside HTML comments are ignored; directories Git ignores are pruned (ignored anti-files are still reported).
- `--init`: `AGENTS.md` lists the knowledge lint command and drops its self-referential routing row; init skips `CLAUDE.md` when `.claude/CLAUDE.md` exists instead of creating a lint error; it warns when no test command is known; command hints cover `packageManager`, Bun, uv, and Poetry.
- Spec §18, §1, §6.1, S5, and the implement prompt: Claude Code reads `AGENTS.md` natively since v2.1.277 when no `CLAUDE.md` or `CLAUDE.local.md` exists. The pack keeps the `@AGENTS.md` import (proposed decision 0004). Copilot rows refreshed. Tool table review-by moves to 2027-01-25.
- Spec fixes: §19.3 no longer tells readers to set an invalid `revisit` status; the §15 `AGENTS.md` template gains the knowledge lint command and the `human-edited` rule, and its stray instruction moved outside the template; §14 names every anti-file the linter rejects; §8 adds a minimal adopter CI workflow; the implement prompt no longer uses a `v0.1.0` pin example and lists the write-permissions section.
- CI tests Python 3.14 alongside 3.10 and 3.12.

## 0.1.2 — 2026-09-08

- Fix downloaded-script root selection; preserve README under init `--force`; refuse unsafe init paths.
- Prune dependencies before walking; explicitly marked fixture trees are excluded while ordinary test documentation is checked.
- Validate conventional alternate ADR paths, conflicting/invalid statuses, dates, supersession cycles, and reordered index headers.
- Check link titles, images, references, escaped-root links, and code-free anchors; reject empty source pointers and missing local source targets.
- Return structured findings for malformed dates, text, and Gemini settings; improve command inference and reject conflicting CLI modes.
- Gate protected edits/demotions separately with `human-edited`; fix multi-file diff boundaries and header-like content; use full-context merge-base comparisons and disable external diff helpers.
- CI declares read-only permissions, tests Python 3.10/3.12, and runs both base and proposed gates; repository protection setup remains a maintainer action.
- Align proposed decision templates, frontmatter vocabulary, development-version/published-pin semantics, and adoption instructions. Keep strict clocks and the existing JSON shape; add `--touch-now` as an explicit alias.
- Review disposition and remaining human release/configuration steps are recorded in model activity. No published tag is moved.

- Decision / identity / architecture / schema / now templates now include the `type:` frontmatter the linter requires (§11, §6.1, implement-prompt). Apply-by-the-book no longer produces a pile of `missing type:` errors. From issue #1.
- `ADOPTERS.md`: TukitoZenx/patrn.ink-api and patrn.ink-ui, owner-approved listing. Display, not a completed messy month.
- Dated the 0.1.1 heading and dropped “unreleased” now that the tag exists. The `v0.1.1` tree itself still says “Unreleased”; that tag is not moved.

## 0.1.1 — 2026-08-17

- Sources appendix (§20). The “duplicated README hurts” line matches Gloaguen et al., not a vibe.
- Linter: `type:` by path, bidirectional supersedes, `_index.md` status/date/supersedes, wiki source pointers, `#anchors`, CommonMark fences, `--init`, `--version` / `PIN_URL`.
- Promotion hook: `--promotion-base` fails a diff that lands `Status: accepted` (`human-accepted` / `--allow-promotion`) or that deletes / moves out an accepted or superseded decision (`human-removed` / `--allow-deletion`). One label does not cover the other. Case, `Status :`, rename+flip, and hunk-less moves out of the ring are gated. A decision with no parseable `Status:` is an error. The hook is pull-request only.
- README fast path no longer curls a tag that does not exist. Re-vendor procedure is documented. No PyPI/uvx entry point in this patch.
- Spec: §2 points at §14 for anti-files; 1→2 bar lives in §19.1 only. `AGENTS.md` has write permissions.
- Still human review: kind-mixing inside a typed file, belief flips without a log line.
- Still no third-party adopter and no product-repo month. Those are not spec gaps.

## 0.1.0 — 2026-08-17

- First tagged release of the knowledge architecture.
- Kernel page (`docs/kernel.md`); full spec remains the on-demand ring.
- Authority edges: Level 1→2 promotion, ownership handoff, conflicting evidence, non-Markdown artifacts, spec clocks (§19).
- Compatibility pack for Claude Code, Gemini CLI, and Copilot holdouts.
- URL-based apply flow (`docs/implement-prompt.md`).
- Mechanical linter (`scripts/lint_knowledge.py`) with tests, `--strict` / `--fix` / `--format json`, `check` alias, and CI.
- Apply flow is Phase 1 inspect / Phase 2 apply; README names Tier 1–3 and pinned vendor curls.
- This repository applies the architecture to itself (reference layout, not a product app).
- Model handoff notes live in `model-activity/` (this repo only; not part of the spec).
- This tag is frozen. Later work ships as `v0.1.1+` (see CONTRIBUTING).
