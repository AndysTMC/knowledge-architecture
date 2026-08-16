---
type: decision
status: accepted
---

# 0002. License the specification and linter under MIT

Status: accepted
Date: 2026-08-17
Deciders: AndysTMC
Supersedes: —
Superseded-by: —

## Context

The project is meant to be copied into other repositories. A missing license blocks adoption. Dual-licensing the prose (CC-BY) and the script (MIT) is clearer for some orgs and heavier for everyone else.

## Options

- A — MIT for the whole repository
- B — CC-BY-4.0 for the spec, MIT for `scripts/`
- C — No license (default copyright)

## Decision

We will use the MIT License for the specification, prompts, and linter.

## Assumptions

- [A1] Adopters need to copy and modify the spec inside their own repos (revisit if a standards body later needs a different grant).

## Consequences

Simple reuse. Attribution via the copyright line. No copyleft.

## Revisit if

A foundation or standards process requires a different license.
