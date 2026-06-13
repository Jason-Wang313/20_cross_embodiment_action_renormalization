# Experiment Report

## Question

Does componentwise action normalization preserve task effects across robot bodies, and does Effect-Jacobian Action Renormalization (EJAR) reduce the mismatch in a controlled embodied setting?

## Setup

A 2D teacher arm generates joint actions and first-order end-effector effects. Three target arms with different link lengths, degrees of freedom, and actuator limits receive either raw normalized copied actions or EJAR-decoded actions. The experiment includes random configurations and a repeated near-singular stress subset.

## Key Results

- ejar_absolute: mean relative one-step effect error 0.265, median 0.087, p90 0.778.
- ejar_capability_token: mean relative one-step effect error 0.016, median 0.005, p90 0.023.
- raw_copy: mean relative one-step effect error 1.252, median 1.212, p90 1.980.

- ejar_absolute: trajectory success rate at 0.10 workspace units 0.792.
- raw_copy: trajectory success rate at 0.10 workspace units 0.371.

## V2 Jacobian-Misspecification Stress

- sigma 0.00: mean relative error 0.266, p90 0.777, true residual 0.0177, residual gap 0.0000.
- sigma 0.02: mean relative error 0.283, p90 0.783, true residual 0.0180, residual gap 0.0010.
- sigma 0.05: mean relative error 0.287, p90 0.769, true residual 0.0179, residual gap 0.0025.
- sigma 0.10: mean relative error 0.343, p90 0.853, true residual 0.0204, residual gap 0.0051.
- sigma 0.20: mean relative error 0.429, p90 0.916, true residual 0.0226, residual gap 0.0102.

## Interpretation

The synthetic evidence supports the narrow mechanism claim: copying normalized actuator values is not effect preserving across embodiments, while a local Jacobian pullback substantially improves first-order effect matching when the requested effect is feasible. Near singularities and actuator clipping remain failure modes; EJAR reports those through residuals rather than pretending the action transferred cleanly.

## Artifacts

- `results/one_step_results.csv`
- `results/episode_results.csv`
- `results/experiment_summary.json`
- `results/jacobian_noise_stress.csv`
- `figures/one_step_effect_error.png`
- `figures/trajectory_transfer.png`
