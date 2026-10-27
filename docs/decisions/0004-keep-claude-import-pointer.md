---
type: decision
---

# 0004. Keep the CLAUDE.md import pointer now that Claude Code reads AGENTS.md

Status: proposed
Date: 2026-10-27
Deciders: AndysTMC (pending)
Supersedes: —
Superseded-by: —

## Context

The compatibility pack ships `CLAUDE.md` containing `@AGENTS.md` because Claude Code did not read `AGENTS.md`. Since v2.1.277 it does, but only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` is in the working directory or above it. Older versions, sessions where the built-in reader is disabled, and some sessions on versions before v2.1.281 read `CLAUDE.md` only. Claude Code documents that an `@AGENTS.md` import is never loaded twice, whatever the instruction-file setting. See [the specification’s S5](../knowledge-architecture.md#20-sources).

## Options

- A — Keep `CLAUDE.md` with `@AGENTS.md` in the pack and `--init`
- B — Drop `CLAUDE.md` from the pack and rely on native reading
- C — Make the pointer optional, chosen per repository

## Decision

We will keep option A. `CLAUDE.md` stays a one-line import, written by `--init` and required by the pack. A symlink to `AGENTS.md` remains an accepted alternative for teams that do not use Windows.

## Assumptions

- [A1] Some adopters run Claude Code versions or sessions that read only `CLAUDE.md` (revisit when the supported floor is past v2.1.281 for a year).
- [A2] A personal `CLAUDE.local.md` is common, and it switches native `AGENTS.md` reading off (revisit if Claude Code stops counting it).
- [A3] An imported `AGENTS.md` is never loaded twice (revisit if the vendor documentation changes).

## Consequences

Every adopter gets the hub in Claude Code regardless of version or local files, at the cost of one extra file. The pointer must stay an import: a `CLAUDE.md` that only tells Claude in words to read `AGENTS.md` does not load it.

## Revisit if

Claude Code reads `AGENTS.md` regardless of `CLAUDE.md` files, or a supported version reads the hub twice through the import.
