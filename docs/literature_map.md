# Literature Map

## Field Box

Cross-embodiment robot learning: methods that try to make policies, demonstrations, actions, or controllers transfer across robot bodies whose kinematics, dynamics, actuation limits, grippers, sensing, or control rates differ. The relevant embodied-intelligence boundary includes robot action models, task-space control, manipulation learning, retargeting, sim-to-real, morphology transfer, and robot foundation policies.

## Sweep Protocol

- Landscape sweep: top 1000 ranked rows in `docs/related_work_matrix.csv`.
- Serious skim: rows 1-300, with mechanism and assumption annotations.
- Deep read surrogate: rows 1-240, selected by relevance to action semantics, embodiment transfer, and control.
- Hostile prior-work set: rows 1-100, used to attack novelty.

The extraction is abstract/title/metadata based. It is useful for mapping the field and hostile boundaries, but it is not a substitute for line-by-line human reading of every cited paper.

## Category Counts

- general robot learning: 223
- sim-to-real transfer: 156
- cross-embodiment and morphology transfer: 114
- imitation and demonstrations: 110
- retargeting and teleoperation: 96
- robot manipulation learning: 82
- robot foundation policies: 80
- contact-rich manipulation: 44
- task-space control and kinematics: 39
- action representation and sequence policies: 28
- locomotion transfer: 28

## Frequent Venues/Sources

- arXiv (Cornell University): 135
- IEEE Robotics and Automation Letters: 44
- Frontiers in Robotics and AI: 42
- International Journal of Social Robotics: 27
- IEEE Access: 24
- IEEE Transactions on Robotics: 20
- Frontiers in Neurorobotics: 17
- The International Journal of Robotics Research: 16
- Robotics and Autonomous Systems: 13
- Nature Communications: 12
- Sensors: 12
- Robotics: 12
- ACM Transactions on Human-Robot Interaction: 12
- Applied Sciences: 11
- Journal of NeuroEngineering and Rehabilitation: 9
- Science Robotics: 8
- Proceedings of the AAAI Conference on Artificial Intelligence: 8
- Annual Review of Control Robotics and Autonomous Systems: 8
- Soft Robotics: 8
- IEEE/ASME Transactions on Mechatronics: 7

## Top Serious-Skim Papers

| sweep_rank | title | year | venue | category | actual_mechanism_introduced |
| --- | --- | --- | --- | --- | --- |
| 1 | HumanHumanoid Robots Cross-Embodiment Behavior-Skill Transfer Using Decomposed Adversarial Learning From Demonstratio... | 2025 | IEEE Robotics & Automation Magazine | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 2 | Pushing the Limits of Cross-Embodiment Learning for Manipulation and Navigation | 2024 |  | robot foundation policies | Large sequence model conditioned on vision, language, history, and sometimes robot identity. |
| 3 | LEGATO: Cross-Embodiment Imitation Using a Grasping Tool | 2025 | IEEE Robotics and Automation Letters | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 4 | XSkill: Cross Embodiment Skill Discovery | 2023 | arXiv (Cornell University) | action representation and sequence policies | Denoising or score-based sequence model over robot actions. |
| 5 | Towards Synergistic, Generalized, and Efficient Dual-System for Robotic Manipulation | 2024 | arXiv (Cornell University) | robot foundation policies | Denoising or score-based sequence model over robot actions. |
| 6 | Scaling Cross-Embodied Learning: One Policy for Manipulation, Navigation, Locomotion and Aviation | 2024 | arXiv (Cornell University) | cross-embodiment and morphology transfer | Large sequence model conditioned on vision, language, history, and sometimes robot identity. |
| 7 | OpenVLA: An Open-Source Vision-Language-Action Model | 2024 | arXiv (Cornell University) | robot foundation policies | Denoising or score-based sequence model over robot actions. |
| 8 | RoboMIND: Benchmark on Multi-embodiment Intelligence Normative Data for Robot Manipulation | 2024 | arXiv (Cornell University) | robot foundation policies | Large sequence model conditioned on vision, language, history, and sometimes robot identity. |
| 9 | From One Hand to Multiple Hands: Imitation Learning for Dexterous Manipulation From Single-Camera Teleoperation | 2022 | IEEE Robotics and Automation Letters | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 10 | Leveraging Pretrained Latent Representations for Few-Shot Imitation Learning on an Anthropomorphic Robotic Hand | 2024 |  | retargeting and teleoperation | Large sequence model conditioned on vision, language, history, and sometimes robot identity. |
| 11 | DexWild: Dexterous Human Interactions for In-the-Wild Robot Policies | 2025 |  | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 12 | RoVi-Aug: Robot and Viewpoint Augmentation for Cross-Embodiment Robot Learning | 2024 | arXiv (Cornell University) | cross-embodiment and morphology transfer | Morphology-conditioned dynamics, policy, or representation for transferring behavior across bodies. |
| 13 | Any-point Trajectory Modeling for Policy Learning | 2024 |  | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 14 | One-Shot Transfer of Long-Horizon Extrinsic Manipulation Through Contact Retargeting | 2024 |  | robot foundation policies | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 15 | Learning Cross-Domain Correspondence for Control with Dynamics\n Cycle-Consistency | 2020 | arXiv (Cornell University) | cross-embodiment and morphology transfer | Simulator variation or adaptation meant to make a learned policy robust on real hardware. |
| 16 | From One Hand to Multiple Hands: Imitation Learning for Dexterous Manipulation from Single-Camera Teleoperation | 2022 | arXiv (Cornell University) | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 17 | Plan-Guided Reinforcement Learning for Whole-Body Manipulation | 2023 | arXiv (Cornell University) | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 18 | DexH2R: Task-Oriented Dexterous Manipulation From Human to Robots | 2025 | IEEE/ASME Transactions on Mechatronics | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 19 | TACT: Humanoid Whole-Body Contact Manipulation Through Deep Imitation Learning With Tactile Modality | 2025 | IEEE Robotics and Automation Letters | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 20 | X-Nav: Learning End-to-End Cross-Embodiment Navigation for Mobile Robots | 2025 | IEEE Robotics and Automation Letters | action representation and sequence policies | Large sequence model conditioned on vision, language, history, and sometimes robot identity. |
| 21 | XIRL: Cross-embodiment Inverse Reinforcement Learning | 2021 | arXiv (Cornell University) | cross-embodiment and morphology transfer | Morphology-conditioned dynamics, policy, or representation for transferring behavior across bodies. |
| 22 | RAPID Hand: A Robust, Affordable, Perception-Integrated, Dexterous Manipulation Platform for Generalist Robot Autonomy | 2025 | ArXiv.org | robot foundation policies | Denoising or score-based sequence model over robot actions. |
| 23 | Multicontact Motion Retargeting Using Whole-Body Optimization of Full Kinematics and Sequential Force Equilibrium | 2022 | IEEE/ASME Transactions on Mechatronics | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 24 | Mirage: Cross-Embodiment Zero-Shot Policy Transfer with Cross-Painting | 2024 | arXiv (Cornell University) | robot foundation policies | Morphology-conditioned dynamics, policy, or representation for transferring behavior across bodies. |
| 25 | RAM: Retrieval-Based Affordance Transfer for Generalizable Zero-Shot Robotic Manipulation | 2024 | arXiv (Cornell University) | cross-embodiment and morphology transfer | Morphology-conditioned dynamics, policy, or representation for transferring behavior across bodies. |
| 26 | Polybot: Training One Policy Across Robots While Embracing Variability | 2023 | arXiv (Cornell University) | cross-embodiment and morphology transfer | Morphology-conditioned dynamics, policy, or representation for transferring behavior across bodies. |
| 27 | DexForce: Extracting Force-Informed Actions From Kinesthetic Demonstrations for Dexterous Manipulation | 2025 | IEEE Robotics and Automation Letters | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 28 | RH20T: A Comprehensive Robotic Dataset for Learning Diverse Skills in One-Shot | 2024 |  | robot foundation policies | Large sequence model conditioned on vision, language, history, and sometimes robot identity. |
| 29 | GELLO: A General, Low-Cost, and Intuitive Teleoperation Framework for Robot Manipulators | 2024 |  | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 30 | Sim-to-real via latent prediction: Transferring visual non-prehensile manipulation policies | 2023 | Frontiers in Robotics and AI | sim-to-real transfer | Simulator variation or adaptation meant to make a learned policy robust on real hardware. |
| 31 | Augmented Reality for RObots (ARRO): Pointing Visuomotor Policies Towards Visual Robustness | 2026 | IEEE Robotics and Automation Letters | robot foundation policies | Denoising or score-based sequence model over robot actions. |
| 32 | ForceMimic: Force-Centric Imitation Learning with Force-Motion Capture System for Contact-Rich Manipulation | 2025 |  | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 33 | Open X-Embodiment: Robotic Learning Datasets and RT-X Models : Open X-Embodiment Collaboration<sup>0</sup> | 2024 |  | robot foundation policies | Large sequence model conditioned on vision, language, history, and sometimes robot identity. |
| 34 | Open X-Embodiment: Robotic Learning Datasets and RT-X Models | 2023 | arXiv (Cornell University) | robot foundation policies | Large sequence model conditioned on vision, language, history, and sometimes robot identity. |
| 35 | Toward Teaching by Demonstration for Robot-Assisted Minimally Invasive Surgery | 2021 | IEEE Transactions on Automation Science and Engineering | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 36 | REvolveR: Continuous Evolutionary Models for Robot-to-robot Policy Transfer | 2022 | arXiv (Cornell University) | cross-embodiment and morphology transfer | Morphology-conditioned dynamics, policy, or representation for transferring behavior across bodies. |
| 37 | A Survey on Sim-to-Real Transfer Methods for Robotic Manipulation | 2024 |  | sim-to-real transfer | Simulator variation or adaptation meant to make a learned policy robust on real hardware. |
| 38 | Brain-Actuated Control of Dual-Arm Robot Manipulation With Relative Motion | 2017 | IEEE Transactions on Cognitive and Developmental Systems | task-space control and kinematics | Task-space or Jacobian-based controller translating desired motion into robot commands. |
| 39 | My Robot, My Motion: Expressive Real-Time Teleoperation | 2025 |  | retargeting and teleoperation | Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences. |
| 40 | Manipulator-Independent Representations for Visual Imitation | 2021 |  | cross-embodiment and morphology transfer | Morphology-conditioned dynamics, policy, or representation for transferring behavior across bodies. |

## Readout

The field has strong coverage of task-space control, morphology-conditioned learning, retargeting, sim-to-real robustness, diffusion/action sequence policies, and robot foundation policies. The common weak point is that action comparability is usually delegated to the chosen interface, a learned embodiment token, a simulator randomization envelope, or a controller beneath the policy. That leaves a narrow but meaningful opening for an explicit action renormalization rule whose object is the physical task effect of the action token itself.
