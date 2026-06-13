# Reviewer Attacks

| Attack | Severity | Response / required evidence |
| --- | --- | --- |
| This is just operational-space control. | High | Concede controller ancestry; boundary is the policy/data action token plus capability normalization and infeasibility residual. Need to cite Khatib-style control and frame novelty narrowly. |
| Synthetic planar arms are too weak. | High | Agree; paper-readiness should be workshop/revise unless real robot logs are added. Synthetic evidence is only a mechanism sanity check. |
| Jacobians are often unavailable or wrong. | High | V2 adds a Jacobian-misspecification stress. At 20% relative Jacobian noise, mean relative effect error rises from 0.266 to 0.429 and the residual gap rises to 0.0102. The paper must state that EJAR does not solve Jacobian estimation. |
| Contact tasks violate first-order free-space assumptions. | High | Mark unsupported; propose contact-conditioned task maps as future work. |
| Learned policies can infer this from data. | Medium | Maybe with enough data; EJAR is still useful as an inductive action interface and exposes infeasibility. Need ablations on data scale in future. |
| Capability normalization changes the task rather than preserving absolute effects. | Medium | Clarify two modes: absolute-effect pullback and local capability-normalized token execution. Report which is used in each experiment. |
| Clipping destroys the guarantee. | Medium | Yes; clipping is exactly where the residual reports infeasibility. |
| The method assumes matched task maps. | High | True; correspondence/task-map mismatch is outside scope. |
| The literature sweep is automated and shallow. | Medium | Be transparent; use it for boundary finding, not as a substitute for manual citation scholarship. |
