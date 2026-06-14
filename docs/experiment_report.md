# Experiment Report

## Question

Does componentwise action normalization preserve task effects across robot bodies, and does Effect-Jacobian Action Renormalization (EJAR) reduce the mismatch under a broad deterministic synthetic audit?

## V3 Setup

The v3 suite uses 12 planar-arm morphologies with 2-6 degrees of freedom, different link lengths, actuator limits, redundancy, local conditioning, control periods, task-map assumptions, and contact-proxy maps. It runs nine families:

- Family A: embodiment diversity main sweep.
- Family B: long-horizon trajectory transfer.
- Family C: learned action-interface stress.
- Family D: Jacobian/model-error stress.
- Family E: residual calibration and infeasibility detection.
- Family F: semantic task-map mismatch.
- Family G: control-rate and latency mismatch.
- Family H: contact-effect proxy.
- Family I: negative controls and sanity checks.

## Key V3 Results

- Total rows: 114,040.
- Trajectory/learned-policy decision rows: 19,440.
- Plot failures: 0.
- Family A normalized-copy mean relative error: 1.215.
- Family A EJAR-absolute mean relative error: 0.231.
- Family A EJAR-capability token-relative error: 0.014.
- Family B normalized-copy success at 0.10: 0.156.
- Family B EJAR-absolute success at 0.10: 0.908.
- Family C effect-label EJAR mean relative error at 8,000 samples: 0.295, versus pooled raw-action error 0.920.
- Family D exact-Jacobian mean relative error: 0.239.
- Family D 20 percent noisy-Jacobian mean relative error: 0.427.
- Family E best infeasibility AUPRC: 0.995 using EJAR residual.

## Interpretation

The evidence supports a narrow synthetic mechanism claim: raw componentwise action normalization is not a reliable cross-embodiment effect invariant, while EJAR improves effect preservation when a valid local task map and action-effect model are available. The same suite also shows the boundary: wrong Jacobians, wrong semantic task maps, wrong timing, latency, and wrong contact modes degrade or break the claim.

## Artifacts

- `experiments/full_scale_ejar.py`
- `results/full_scale/metadata.json`
- `results/full_scale/progress.json`
- `results/full_scale/family_*_seed.csv`
- `results/full_scale/family_*_summary.csv`
- `results/full_scale/table_*.tex`
- `results/full_scale/figure_*.pdf`
- `results/full_scale/figure_*.png`
- `docs/evidence_summary.md`
