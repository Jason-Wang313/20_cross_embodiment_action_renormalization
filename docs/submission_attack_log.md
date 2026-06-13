# Submission Attack Log

Updated: 2026-06-13 02:05:44 +01:00

## V2 Attack Rounds

1. **"This assumes exact Jacobians."** Added a Jacobian-misspecification stress where EJAR decodes with a noisy estimated target Jacobian but realized effects are evaluated with the true Jacobian.
2. **"The residual may be falsely reassuring."** The stress reports both estimated-model residual and true residual gap. At 20% relative Jacobian noise, the residual gap rises to 0.0102.
3. **"Operational-space control already knows this."** The paper keeps the novelty boundary narrow: the controller math is prior art; the claim is about the action representation and infeasibility diagnostic at the cross-embodiment data/policy interface.
4. **"Synthetic planar arms are too weak."** The decision remains workshop-only / strong-revise; real multi-robot logs or contact manipulation are required for main-track strength.
5. **"Task-map mismatch is unresolved."** Still true and explicitly out of scope; the v2 stress covers local Jacobian noise, not semantic task correspondence.

## Terminal Assessment

Recoverable sensitivity evidence was added. Remaining limitations require new datasets, real robots, or learned perception/Jacobian estimation.
