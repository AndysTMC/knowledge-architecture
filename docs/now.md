---
type: now
updated: 2026-10-27
horizon: 2026-10-27 → 2026-11-10
---

# Now

## Focus

Publish v0.2.0: decision-gate hardening, fewer false lint findings, init improvements, the refreshed §18 loader table, and accepted decision 0004.

## Next

- AndysTMC merges the release PR, then creates the annotated `v0.2.0` tag on that merge commit.
- Verify the tagged download (`curl` the pinned script, `--version`, a clean `--init` and `--strict`) before advertising it.
- Add `lint (3.14)` to the required checks on main, and protect `v*` tags with a ruleset.
- §18 rows outside the compatibility pack still carry the 2026-08-17 survey; re-check them before 2027-01-25.

## Validation boundary

The adopter field trial started 2026-08-17. A completed-month evaluation has not been verified; release completion and adopter listings do not establish field validation.

## Do not do

- Move published tags or promote decisions without explicit human acceptance.
- Open an empty development cycle after the release.

GitHub protection is managed in repository settings. Verify it through the API before relying on it; checked-in CODEOWNERS alone does not enforce approval.
