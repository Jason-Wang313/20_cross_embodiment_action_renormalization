# Claims

## Supported Claims

1. Componentwise normalized joint actions do not in general preserve local task effects across robot bodies with different Jacobians, actuator limits, control periods, and local configurations.
2. EJAR absolute-effect decoding reduces morphology-transfer effect error in the v3 synthetic suite: Family A normalized-copy mean relative error is 1.215, while EJAR absolute-effect mean relative error is 0.231.
3. EJAR capability tokens preserve locally normalized effect authority, not absolute displacement; Family A token-relative error is 0.014.
4. One-step action-interface mismatch compounds over transferred sequences: Family B normalized-copy success at 0.10 is 0.156, while EJAR absolute-effect success is 0.908.
5. In a simple linear learned-action-label stress, effect labels decoded with EJAR have lower held-out relative effect error than pooled raw-action labels at 8,000 samples: 0.295 versus 0.920.
6. EJAR residuals are useful infeasibility diagnostics under valid local maps: Family E AUPRC is 0.995.
7. The v3 boundary families show that wrong Jacobians, wrong semantic task maps, wrong control periods, latency, and wrong contact modes degrade or break the claim.

## Formal Claim Status

- Proven in paper: a local first-order preservation proposition under full-row-rank action-effect map, known actuator metric, no clipping, no damping, and valid task correspondence.
- Demonstrated: deterministic synthetic planar-arm/action-effect suite with 12 morphologies, nine experiment families, 114,040 rows, and 19,440 trajectory/learned-policy decision rows.
- Unsupported beyond scope: real hardware, visual policy learning, contact-rich manipulation, correspondence discovery, safety certification, and Jacobian estimation.

## Claims Explicitly Not Made

- EJAR is not a new operational-space controller.
- EJAR is not a universal robot-transfer method.
- EJAR does not solve perception, correspondence, contact-mode selection, or local Jacobian estimation.
- EJAR residuals are not safety certificates and can be falsely reassuring under wrong maps.
- EJAR capability tokens do not preserve absolute displacement.
- The paper does not claim to outperform robot foundation policies.
