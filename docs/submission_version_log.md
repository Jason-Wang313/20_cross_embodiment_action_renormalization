# Submission Version Log

## v3-link-hardening - 2026-06-20

- Added explicit VLA-style `hyperref` boxed-link styling to `paper/main.tex`.
- Rebuilt and re-exported the canonical PDF to `C:\Users\wangz\Downloads\20.pdf`.
- Verified final PDF: 26 pages, 409,298 bytes, SHA256 `106CC7757D60C2D17A1434DFE281981F745922B90855E29CE6E260FC0CF66E94`.
- Verified 60 link annotations: green = 54, red = 6, cyan = 0, with one-point borders on pages `[(1, 16), (2, 25), (3, 13), (16, 1), (17, 5)]`.

## v3 - 2026-06-14

- Added `docs/full_scale_execution_plan.md`.
- Added RAM-light full-scale runner `experiments/full_scale_ejar.py`.
- Generated `results/full_scale/` with 114,040 deterministic rows, 19,440 trajectory/learned-policy decision rows, metadata, progress, CSVs, generated LaTeX tables, and figures.
- Rewrote the manuscript into a 26-page v3 submission artifact.
- Final PDF exported to `C:\Users\wangz\Downloads\20.pdf`.
- Final PDF SHA256 before the 2026-06-20 link-style hardening: `E23D1C3D300FF6010FBE0F3574AC84ACA0E4FD5F2488048D6C57D79C2B9369E0`.
- Final decision: submission-ready as a synthetic mechanism paper with explicit real-robot limitations.

## v2 - 2026-06-13

- Added Jacobian-misspecification stress to `experiments/run_ejar_synthetic.py`.
- Generated `results/jacobian_noise_stress.csv` and `results/jacobian_noise_table.tex`.
- Updated the manuscript with visible v2 metadata, the stress table, and a quantified known-Jacobian limitation.
- Updated claims, reviewer attacks, audit notes, and reproducibility documentation.

## v1 - 2026-06-11

- Original generated EJAR paper with synthetic planar-arm experiments, ICLR-style manuscript, and public GitHub repository.
