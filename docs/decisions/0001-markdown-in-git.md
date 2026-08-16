---
type: decision
status: accepted
---

# 0001. Store project knowledge as Markdown in git

Status: accepted
Date: 2026-08-17
Deciders: AndysTMC
Supersedes: —
Superseded-by: —

## Context

The knowledge has to be readable by humans, by every major coding agent, and by git history. A database, a wiki host, or a vendor memory store would split the source of truth.

## Options

- A — Markdown files in the git repository
- B — A hosted wiki or Notion as the real store, git as a mirror
- C — Vendor agent memory (Claude auto-memory, Cursor memories) as canonical

## Decision

We will keep canonical knowledge as Markdown (and small scripts) in git.

## Assumptions

- [A1] Major coding agents still read Markdown from the worktree (revisit if that stops).
- [A2] The corpus stays small enough that `index.md` / grep / the linter suffice (revisit if a single wiki exceeds what one read can hold — then add local search, not a new store).

## Consequences

Plain diffs, no vendor lock-in, and the implement prompt can be a URL. We do not get a graph UI or multiplayer presence.

## Revisit if

A required agent can no longer see worktree Markdown, or the corpus needs query infrastructure the linter cannot replace.
