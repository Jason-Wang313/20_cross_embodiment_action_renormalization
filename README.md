# Cross-Embodiment Action Renormalization

This repository contains paper 20 from the robotics/embodied-intelligence batch. The selected thesis is that cross-embodiment robot policies should not share raw normalized actuator commands; they should share local task-effect tokens decoded through each robot's action-to-effect map.

Submission-hardening v3 is complete. The final PDF is `C:\Users\wangz\Downloads\20.pdf` (26 pages, SHA256 `E23D1C3D300FF6010FBE0F3574AC84ACA0E4FD5F2488048D6C57D79C2B9369E0`).

## Main Mechanism

Effect-Jacobian Action Renormalization (EJAR) uses a robot's local task Jacobian and one-step actuator limits to encode or decode actions by their local task effects. The paper makes a narrow mechanism claim: componentwise action normalization is not generally effect preserving across different robot bodies. The v3 manuscript remains a synthetic mechanism paper, not a real-robot deployment claim.

## Reproduce

Install Python dependencies if needed:

```powershell
python -m pip install -r requirements.txt
```

Run the synthetic evidence:

```powershell
python experiments/run_ejar_synthetic.py
```

Run the full-scale v3 evidence:

```powershell
python experiments/full_scale_ejar.py
```

The v3 run writes `results/full_scale/` with 114,040 deterministic rows, 19,440 trajectory/learned-policy decision rows, generated tables, figures, metadata, and progress logs.

Regenerate the literature artifacts:

```powershell
python scripts/generate_literature.py
```

Build the paper from the `paper/` directory:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Only the final verified PDF is copied to `C:\Users\wangz\Downloads\20.pdf`.

## Important Artifacts

- `docs/related_work_matrix.csv`: 1000-paper annotated landscape sweep.
- `docs/literature_map.md`: field map and sweep protocol.
- `docs/hostile_prior_work.md`: 100-paper hostile prior set.
- `docs/novelty_boundary_map.md`: assumptions and novelty boundary.
- `docs/novelty_decision.md`: selected thesis and rejected alternatives.
- `docs/claims.md`: supported and unsupported claims.
- `docs/reviewer_attacks.md`: adversarial review risks.
- `docs/final_audit.md`: final readiness audit.
- `docs/full_scale_execution_plan.md`: v3 paper-specific full-scale plan.
- `docs/evidence_summary.md`: v3 headline evidence and final PDF details.
- `results/jacobian_noise_stress.csv`: v2 Jacobian-misspecification stress.
- `results/jacobian_noise_table.tex`: generated LaTeX table for the v2 stress.
- `results/full_scale/`: v3 full-scale CSVs, tables, figures, metadata, and progress.
- `paper/main.tex`: anonymous ICLR-style manuscript.
- `experiments/run_ejar_synthetic.py`: runnable synthetic experiment.
- `experiments/full_scale_ejar.py`: v3 RAM-light full-scale runner.
