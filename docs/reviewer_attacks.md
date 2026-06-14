# Reviewer Attacks

| Attack | Severity | Response / required evidence |
| --- | --- | --- |
| This is just operational-space control. | High | Concede controller ancestry; novelty is the action-token interface and infeasibility diagnostic at the policy/data boundary. |
| Synthetic evidence is not enough for robot transfer. | High | Agree for hardware claims; v3 is submission-ready only as a synthetic mechanism paper. |
| Raw normalized copy is a weak baseline. | High | v3 includes target IK, static-home, link-scaled, and learned raw-action baselines. |
| Target IK is close to EJAR. | Medium | Correct; target IK is a controller baseline. EJAR's claim is about what shared action tokens should represent. |
| Jacobians are often unavailable or wrong. | High | Family D quantifies noise, bias, dropout, finite-difference, and stale-map failures. |
| Residuals can be falsely reassuring. | High | Family D and F show residual gaps under wrong maps; residual validity is limited to valid local maps. |
| Capability tokens change the task. | Medium | The paper separates absolute-effect and capability-token modes and does not claim token mode preserves metric displacement. |
| Learned policies can infer embodiment mismatch. | Medium | Family C tests simple learned labels; the paper does not deny that larger policies can learn compensation. |
| Contact-rich manipulation violates assumptions. | High | Family H is only a contact proxy and explicitly not a real manipulation claim. |
| Task-map correspondence is assumed. | High | Family F shows wrong correspondences break EJAR; correspondence learning is unsupported. |
| The literature sweep is automated. | Medium | The sweep is framed as hostile coverage, not exhaustive manual scholarship. |
