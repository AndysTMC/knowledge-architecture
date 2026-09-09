# Changelog

All notable changes to this specification are recorded here. Spec versions are git tags.

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
