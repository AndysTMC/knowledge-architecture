---
type: now
updated: 2026-09-09
horizon: 2026-09-09 → 2026-09-23
---

# Now

## Focus

The v0.1.2 repair and release work is complete. Main uses the released linter version and pin; no new development cycle is open.

## Completed

- Published v0.1.2 through PR #2 and verified the downloaded artifacts against the immutable tag.
- Passed all 82 tests, strict lint, and Python 3.10/3.12 CI.
- Enabled required CI checks and code-owner review on main; administrators retain bypass permission.
- Recorded AndysTMC's explicit acceptance of ADR 0003 and corrected the portfolio in PR #4.
- Closed issue #1 after verifying the released templates and reproducing the missing-type failure in control fixtures.

## Next

No queued implementation tasks. Routine maintenance remains: review the dated §18 tool survey before 2026-11-17 and assess adopter feedback when available.

## Validation boundary

The adopter field trial started 2026-08-17. A completed-month evaluation has not been verified; release completion and adopter listings do not establish field validation.

## Do not do

- Move published tags or promote future decisions without explicit human acceptance.
- Open an empty development cycle or create unused documentation directories.

GitHub protection is managed in repository settings. Verify it through the API before relying on it; checked-in CODEOWNERS alone does not enforce approval.
