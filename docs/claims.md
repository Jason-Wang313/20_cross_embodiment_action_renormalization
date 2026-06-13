# Claims

## Supported Claims

1. Componentwise normalized joint actions do not in general preserve end-effector/task effects across robot bodies with different Jacobians.
2. If the requested effect lies in the target robot's local feasible effect subspace and clipping is inactive, a damped pseudoinverse decoder can preserve the requested first-order task effect up to the damping residual.
3. Capability-normalized effect tokens expose anisotropy and infeasibility that raw action normalization hides.
4. In the included planar-arm synthetic experiment, EJAR reduces one-step effect error and improves closed-loop reaching transfer relative to raw normalized joint copying.
5. The v2 Jacobian-misspecification stress shows that EJAR depends on a trustworthy local action-effect model: at 20% relative Jacobian noise, absolute-effect mean relative error rises from 0.266 to 0.429 and the predicted-vs-realized residual gap rises to 0.0102.

## Formal Claim Status

- Proven in paper: a local first-order proposition under full-row-rank Jacobian, known actuator metric, no clipping, and first-order dynamics.
- Demonstrated: synthetic planar arms with different link lengths, degrees of freedom, and local configurations.
- Unsupported beyond scope: contact-rich object manipulation, real hardware, perception-conditioned policies, high-speed dynamics, and learned Jacobian estimation.
- The residual diagnostic is not guaranteed under wrong Jacobians; it is only as good as the estimated action-effect map used to compute it.

## Claims Explicitly Not Made

- EJAR is not a universal controller.
- EJAR does not remove the need for feedback.
- EJAR does not solve correspondence, contact-mode selection, or perception.
- EJAR does not solve local Jacobian estimation or guarantee residual calibration under model error.
- EJAR does not claim novelty over operational-space control as a controller; the novelty claim is about action renormalization at the cross-embodiment policy/data interface.
