# Changelog

All notable changes to this specification are recorded here. Spec versions are git tags.

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
