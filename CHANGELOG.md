# Changelog

All notable changes to this specification are recorded here. Spec versions are git tags.

## Unreleased — 0.1.1

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
