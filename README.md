# Cross-Embodiment Action Renormalization

This repository contains paper 20 from the robotics/embodied-intelligence batch. The selected thesis is that cross-embodiment robot policies should not share raw normalized actuator commands; they should share local task-effect tokens decoded through each robot's action-to-effect map.

## Main Mechanism

Effect-Jacobian Action Renormalization (EJAR) uses a robot's local task Jacobian and one-step actuator limits to encode or decode actions by their local task effects. The paper makes a narrow mechanism claim: componentwise action normalization is not generally effect preserving across different robot bodies.

## Reproduce

Install Python dependencies if needed:

```powershell
python -m pip install -r requirements.txt
```

Run the synthetic evidence:

```powershell
python experiments/run_ejar_synthetic.py
```

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

The compiled PDF is copied by the batch run to `C:/Users/wangz/Downloads/20.pdf`.

## Important Artifacts

- `docs/related_work_matrix.csv`: 1000-paper annotated landscape sweep.
- `docs/literature_map.md`: field map and sweep protocol.
- `docs/hostile_prior_work.md`: 100-paper hostile prior set.
- `docs/novelty_boundary_map.md`: assumptions and novelty boundary.
- `docs/novelty_decision.md`: selected thesis and rejected alternatives.
- `docs/claims.md`: supported and unsupported claims.
- `docs/reviewer_attacks.md`: adversarial review risks.
- `docs/final_audit.md`: final readiness audit.
- `paper/main.tex`: anonymous ICLR-style manuscript.
- `experiments/run_ejar_synthetic.py`: runnable synthetic experiment.
