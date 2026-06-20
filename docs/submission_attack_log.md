# Submission Attack Log

Updated: 2026-06-20

## V3 Attack Rounds

1. **"The old paper is only seven pages."** Rewrote into a 26-page manuscript with generated full-scale evidence and detailed appendices.
2. **"The evidence is too small."** Added a nine-family deterministic suite with 114,040 rows and 19,440 trajectory/learned-policy decision rows.
3. **"Raw normalized copy is a weak straw baseline."** Added link-scaled copy, static-home decoder, target IK, learned raw-action labels, robot-ID raw labels, and morphology-conditioned raw labels.
4. **"This is just operational-space control."** Kept the novelty boundary narrow: the controller math is prior art; the contribution is the action token at the cross-embodiment policy/data interface.
5. **"Learned policies can infer morphology."** Added Family C learned action-label stress and reported relative error/cosine rather than only loose success.
6. **"Jacobians are wrong in practice."** Added broader target-model error stress with Gaussian noise, scale bias, column dropout, finite-difference noise, and stale maps.
7. **"Residuals can be falsely reassuring."** Added residual calibration and residual-gap reporting; final claim restricts residual validity to valid local maps.
8. **"Task correspondence is assumed."** Added task-map mismatch family and states that EJAR cannot solve wrong semantic maps.
9. **"Contact breaks the first-order model."** Added a contact-effect proxy that helps only under known contact mode and breaks under wrong mode.
10. **"Negative controls are missing."** Added matched morphology, random map, zero-effect, geometry/limit controls.
11. **"The PDF link styling depends on implicit defaults."** Added explicit `hyperref` border colors, rebuilt the final PDF, and visually checked all affected link pages against the VLA-v4 role model.

## Terminal Assessment

Recoverable synthetic-rigor issues were fixed. Remaining limitations require real robots, visual policies, learned correspondence, or contact-rich manipulation; those are explicitly outside the final narrow claim.
