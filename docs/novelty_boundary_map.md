# Novelty Boundary Map

## Not New Enough

- Using a Jacobian or inverse kinematics controller by itself.
- Adding a robot-ID or morphology token to a larger policy.
- Training on more heterogeneous robot data.
- Retargeting source trajectories to target end-effector poses.
- Creating a benchmark of cross-robot failures without changing the action mechanism.
- Combining a foundation policy with an off-the-shelf low-level controller.

## Open Boundary

A paper remains plausible if the action variable itself is redefined so that equal tokens mean equal local task-effect authority, with a computable infeasibility residual when a target body cannot realize the source effect. The novelty lives in treating action renormalization as a first-class rule at the policy/data boundary rather than as an implicit controller detail or learned nuisance factor.

## Twenty-Four False-Prone Assumptions

1. A normalized joint delta means the same thing on robots with different link lengths.
2. An end-effector displacement is equally feasible across embodiments at the same workspace point.
3. The gripper or contact frame can be treated as a fixed nuisance variable.
4. Per-dimension action scaling is enough to remove embodiment identity.
5. Training data can teach away morphology mismatch without an explicit action rule.
6. The task effect of an action is independent of local kinematic singularities.
7. Action frequency and controller latency do not change the physical effect of an action.
8. Torque, velocity, and position interfaces can be compared after affine normalization.
9. Workspace overlap is sufficient for action transfer.
10. Morphology can be represented by a static token rather than a local operator.
11. Object motion is the right effect variable for every contact state.
12. Nullspace motion is harmless when transferring manipulation actions.
13. Safety limits are separable from task-effect preservation.
14. Demonstrations collected on one robot are action labels for another robot.
15. Policies should learn embodiment compensation rather than receive a renormalized action space.
16. A larger multi-robot dataset closes the action semantics gap.
17. Simulation randomization covers real embodiment differences without preserving effects.
18. Retargeting poses is equivalent to retargeting action effects.
19. The same policy output norm should correspond to the same task authority.
20. Closed-loop correction makes one-step effect mismatch irrelevant.
21. Contact-rich tasks can ignore the anisotropy of local controllability.
22. Embodiment mismatch is mostly visual or geometric, not a property of the action map.
23. Failure near singularities is an edge case rather than a central transfer boundary.
24. A shared latent action space is meaningful without a measurable decoding rule.

## Directions Considered

| Direction | Broken assumption | Why it lost or won |
| --- | --- | --- |
| Bigger cross-robot transformer | Data scale can absorb action mismatch | Rejected: forbidden weak move and already covered by robot foundation policies. |
| New benchmark of action mismatch | Existing evaluations reveal transfer failure | Rejected: benchmark-only contribution. |
| Uncertainty-aware cross-embodiment decoder | Failure is mostly epistemic | Rejected: uncertainty does not define equal action effects. |
| Learned latent action autoencoder | A latent can become comparable from data | Rejected: hard to separate from prior action-representation work. |
| Effect-Jacobian Action Renormalization | Same normalized action should mean same physical effect | Selected: changes the central mechanism and yields a checkable first-order claim plus runnable evidence. |

## Chosen Boundary

The selected paper is not claiming to solve universal robot transfer. It claims that a common normalization assumption is false, proposes an explicit local renormalization rule, proves/demonstrates a limited first-order preservation property, and reports where the rule fails.
