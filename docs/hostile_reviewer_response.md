# Hostile Reviewer Response

## Likely Rejection Point

"EJAR assumes the exact Jacobian, but cross-embodiment learning often does not have a calibrated local action-effect map."

## Response

The v2 paper agrees and quantifies the boundary. EJAR is an action representation and diagnostic assuming a local task map and action-effect model; it does not solve Jacobian estimation. In the v2 stress, EJAR decodes actions with a noisy estimated target Jacobian and is evaluated under the true Jacobian. Mean relative error rises from 0.266 at exact Jacobians to 0.429 at 20% relative noise, and the residual gap rises to 0.0102.

## What The Paper Still Cannot Claim

- Robustness to arbitrary Jacobian or task-map error.
- Contact-rich manipulation transfer.
- Learned perception or correspondence discovery.
- Real-robot validation.

## Honest Position

Workshop-only / strong-revise: crisp mechanism and useful sensitivity evidence, but not main-track without real multi-robot or contact-rich validation.
