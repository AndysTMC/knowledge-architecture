---
type: now
updated: 2026-10-27
horizon: 2026-10-27 → 2026-11-10
---

# Now

## Focus

Review and merge the 0.1.3 development work: decision-gate hardening, fewer false lint findings, init improvements, and the refreshed §18 loader table. v0.1.2 remains the latest published release and pin.

## Next

- AndysTMC reviews the hardening PR and decides on proposed decision 0004 (keep the `CLAUDE.md` import pointer).
- After merge, add the new `lint (3.14)` check to the required checks on main.
- Decide whether to publish the work as v0.1.3 (or v0.2.0, since §18 asks for a minor version after a loader re-check). Publishing needs explicit authorization; then follow the CONTRIBUTING release checklist.
- §18 rows outside the compatibility pack still carry the 2026-08-17 survey; re-check them before 2027-01-25.

## Validation boundary

The adopter field trial started 2026-08-17. A completed-month evaluation has not been verified; release completion and adopter listings do not establish field validation.

## Do not do

- Move published tags, change `PIN_URL` before a release is published, or promote decisions without explicit human acceptance.
- Create unused documentation directories.

GitHub protection is managed in repository settings. Verify it through the API before relying on it; checked-in CODEOWNERS alone does not enforce approval.
