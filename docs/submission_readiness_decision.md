# Submission Readiness Decision

Decision: submission-ready as a synthetic mechanism paper.

## Why Submit-Ready Under The Narrow Claim

- The v3 paper no longer rests on a small planar-arm sanity check; it includes a deterministic full-scale suite with 114,040 rows and 19,440 trajectory/learned-policy decision rows.
- The suite includes strong baselines: target IK, static-home decoding, link-scaled copy, raw learned labels, robot-ID raw labels, and morphology-conditioned raw labels.
- The main claim is narrow: action tokens should preserve local task effects or local capability authority, and residuals should expose infeasible requests under valid maps.
- Boundary failures are explicit: wrong Jacobians, task-map mismatch, wrong control periods, latency, and wrong contact modes are measured rather than hidden.
- The final manuscript is 26 pages and imports generated tables/figures directly.
- The final PDF now matches the VLA-v4 role model's boxed-link convention: green citation/URL boxes, red internal-reference boxes, no cyan boxes, and one-point borders.

## Remaining Limits

- No real robot logs.
- No visual policy training.
- No real contact-rich manipulation.
- No learned correspondence or task-map discovery.
- No safety certification.

## Honest Submission Position

Submit as a mechanism and diagnostic paper for cross-embodiment action interfaces, not as a robot foundation policy, hardware-transfer, or contact-manipulation paper.
