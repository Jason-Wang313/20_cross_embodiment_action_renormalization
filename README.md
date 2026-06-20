# Cross-Embodiment Action Renormalization

This repository contains paper 20 from the robotics/embodied-intelligence batch. The selected thesis is that cross-embodiment robot policies should not share raw normalized actuator commands; they should share local task-effect tokens decoded through each robot's action-to-effect map.

Submission-hardening v3 is complete. The final PDF is `C:\Users\wangz\Downloads\20.pdf` (26 pages, SHA256 `106CC7757D60C2D17A1434DFE281981F745922B90855E29CE6E260FC0CF66E94`).

VLA-style boxed-link verification: 60 annotations on pages `[(1, 16), (2, 25), (3, 13), (16, 1), (17, 5)]`; colors green = 54, red = 6, cyan = 0; all borders `(0, 0, 1)`.

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
