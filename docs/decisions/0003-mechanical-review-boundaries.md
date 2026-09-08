---
type: decision
---

# 0003. Make mechanical review boundaries explicit

Status: proposed
Date: 2026-09-08
Deciders: pending human acceptance
Supersedes: —
Superseded-by: —

## Context

Review found that bootstrap defaults could write outside the target, alternate ADR paths received different checks, and accepted decision content could change without a gate. The current repair implements conservative checks without changing the seven information kinds or the v0.1.x result shape.

## Options

- Keep only status-transition checks and rely on prose for protected edits.
- Gate protected edits separately, document the remaining human boundaries, and keep compatibility aliases.
- Replace the CLI and type vocabulary in a larger redesign.

## Decision

Proposed: retain the small vendored CLI; gate protected edits with `human-edited` separately from acceptance and deletion. Treat partial diffs with unknown old status conservatively. Keep strict clock checks and existing type names. Support the four documented conventional decision directories; run package checks with an explicit root.

These behaviors are implemented in the unreleased working tree under the user's repair authorization. This record remains proposed until a named human accepts it. It does not authorize deletion or inversion of an existing accepted choice.

## Assumptions

- [A1] Full-context Git diffs provide enough status evidence for routine review (revisit if partial-diff false positives dominate).
- [A2] Maintainers can keep the small attention file current (revisit if clock failures regularly block unrelated contributions).
- [A3] Most adopters can use a conventional ADR directory or an explicit package root (revisit when a real adopter needs a configurable mapping).

## Consequences

Protected clarifications and supersession metadata also need an edit label. No label proves human identity or judgment: branch protection and reviewer permissions remain required. A type migration, new subcommands, and structured findings are deferred to a separately reviewed compatibility change.

## Revisit if

Adopter evidence invalidates any assumption, or the supported path and parser subset prevents a legitimate workflow.
