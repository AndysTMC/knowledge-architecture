---
type: identity
status: active
updated: 2026-08-17
---

# Knowledge Architecture

## Intent

A typed knowledge system that humans and coding agents can share, without mixing protocol, beliefs, decisions, and compiled sources into one junk drawer.

## Problem

Teams improvising `AGENTS.md`, `CLAUDE.md`, wikis, and TODO files create conflicting instructions and files no agent should treat as true.

## Scope

- In: kinds of information, authority, birth rule, tool compatibility, a linter, and a prompt to apply the spec to another repo.
- Out: replacing the issue tracker or CI; enforcing policy inside Markdown (hooks enforce); a hosted product; claiming third-party adoption that does not exist.

## Success

A stranger can apply the kernel in an afternoon. A messy month later, the repo still has one hub, dated attention, and decisions that were superseded rather than silently rewritten.

## Constraints

Plain git + Markdown. No required runtime beyond Python 3 for the linter. Pointers, not per-tool bibles.

## Principles

1. Small kernel; grow on first inhabitant.
2. Generated artifacts beat transcribed prose.
3. Agents propose; humans accept Level 2+.
4. One router (`AGENTS.md`).

## Ownership

Repository: AndysTMC. Spec changes that add a kind need a new decision.
