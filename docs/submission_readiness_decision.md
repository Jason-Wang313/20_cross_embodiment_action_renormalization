# Submission Readiness Decision

Decision: workshop-only / strong-revise.

## Why Not Submit-Ready

- Evidence is synthetic planar-arm evidence only.
- No real heterogeneous robot logs are included.
- Contact-rich manipulation and task-correspondence learning are out of scope.
- EJAR assumes a local action-effect model; v2 shows wrong Jacobians degrade effect preservation and residual trustworthiness.

## Why Not Kill

- The action-normalization failure is clear and runnable.
- The formal local preservation proposition is honest about rank, clipping, damping, and feasibility assumptions.
- V2 adds sensitivity evidence for the known-Jacobian assumption rather than hiding it.

## Required Next Work For Main-Track Strength

- Validate on logged heterogeneous robot data or real multi-robot demonstrations.
- Add contact-conditioned task maps and manipulation tasks.
- Evaluate learned or calibrated Jacobian estimates.
- Stress semantic task-map correspondence errors.
