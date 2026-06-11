# Novelty Decision

## Chosen Thesis

Cross-embodiment policies should not share raw normalized actuator commands. They should share capability-normalized task-effect tokens and decode them through each robot's local action-to-effect map. This makes the hidden assumption testable: if two robots receive the same token, they should attempt the same fraction of locally feasible task effect, and the decoder should report when the target cannot realize the requested effect.

## Central Mechanism

Effect-Jacobian Action Renormalization (EJAR): at configuration q for embodiment e, compute the local task Jacobian J_e(q) and an actuator-limit metric B_e. Encode an action a as a dimensionless effect token z = Sigma_e(q)^(-1/2) J_e(q) a, where Sigma_e = J_e B_e B_e^T J_e^T is the local effect-capability ellipsoid. Decode z on a target body through a damped minimum-energy pullback a' = B_t^2 J_t^T (J_t B_t^2 J_t^T + lambda I)^(-1) Sigma_t^(1/2) z, with clipping and a residual that marks infeasible requests.

## Why This Survived the Hostile Set

- Against operational-space control: EJAR is about the policy/data action token, not merely tracking an already specified task-space command.
- Against retargeting: EJAR preserves local differential task effects rather than poses or whole trajectories.
- Against robot foundation models: EJAR can be inserted before learning and creates a measurable transfer invariant rather than asking the model to infer one.
- Against morphology-conditioned transfer: EJAR uses the local operator at q, so the body description is not static.

## Honest Scope

The contribution is a mechanism paper with synthetic embodied-control evidence. It is strongest as an ICLR workshop or revise-level submission unless extended with real robot logs or a multi-robot benchmark.

## Closest Hostile Papers From Sweep

| sweep_rank | title | year | category | hostile_reason |
| --- | --- | --- | --- | --- |
| 1 | HumanHumanoid Robots Cross-Embodiment Behavior-Skill Transfer Using Decomposed Adversarial Learning From Demonstratio... | 2025 | retargeting and teleoperation | Closest transfer threat: already maps commands or demonstrations across bodies. |
| 2 | Pushing the Limits of Cross-Embodiment Learning for Manipulation and Navigation | 2024 | robot foundation policies | Closest empirical threat: may claim multi-robot data learns embodiment compensation. |
| 3 | LEGATO: Cross-Embodiment Imitation Using a Grasping Tool | 2025 | retargeting and teleoperation | Closest transfer threat: already maps commands or demonstrations across bodies. |
| 4 | XSkill: Cross Embodiment Skill Discovery | 2023 | action representation and sequence policies | Closest conceptual threat: explicitly studies body differences. |
| 5 | Towards Synergistic, Generalized, and Efficient Dual-System for Robotic Manipulation | 2024 | robot foundation policies | Closest empirical threat: may claim multi-robot data learns embodiment compensation. |
| 6 | Scaling Cross-Embodied Learning: One Policy for Manipulation, Navigation, Locomotion and Aviation | 2024 | cross-embodiment and morphology transfer | Closest conceptual threat: explicitly studies body differences. |
| 7 | OpenVLA: An Open-Source Vision-Language-Action Model | 2024 | robot foundation policies | Closest empirical threat: may claim multi-robot data learns embodiment compensation. |
| 8 | RoboMIND: Benchmark on Multi-embodiment Intelligence Normative Data for Robot Manipulation | 2024 | robot foundation policies | Closest empirical threat: may claim multi-robot data learns embodiment compensation. |
| 9 | From One Hand to Multiple Hands: Imitation Learning for Dexterous Manipulation From Single-Camera Teleoperation | 2022 | retargeting and teleoperation | Closest transfer threat: already maps commands or demonstrations across bodies. |
| 10 | Leveraging Pretrained Latent Representations for Few-Shot Imitation Learning on an Anthropomorphic Robotic Hand | 2024 | retargeting and teleoperation | Closest transfer threat: already maps commands or demonstrations across bodies. |
| 11 | DexWild: Dexterous Human Interactions for In-the-Wild Robot Policies | 2025 | retargeting and teleoperation | Closest conceptual threat: explicitly studies body differences. |
| 12 | RoVi-Aug: Robot and Viewpoint Augmentation for Cross-Embodiment Robot Learning | 2024 | cross-embodiment and morphology transfer | Closest conceptual threat: explicitly studies body differences. |
| 13 | Any-point Trajectory Modeling for Policy Learning | 2024 | retargeting and teleoperation | Closest conceptual threat: explicitly studies body differences. |
| 14 | One-Shot Transfer of Long-Horizon Extrinsic Manipulation Through Contact Retargeting | 2024 | robot foundation policies | Closest empirical threat: may claim multi-robot data learns embodiment compensation. |
| 15 | Learning Cross-Domain Correspondence for Control with Dynamics\n Cycle-Consistency | 2020 | cross-embodiment and morphology transfer | Closest conceptual threat: explicitly studies body differences. |
