# Reproducibility Checklist

- [x] Dependencies are listed in `requirements.txt`.
- [x] Experiment source is `experiments/run_ejar_synthetic.py`.
- [x] Main outputs are `results/one_step_results.csv`, `results/episode_results.csv`, and `results/experiment_summary.json`.
- [x] V2 outputs are `results/jacobian_noise_stress.csv` and `results/jacobian_noise_table.tex`.
- [x] Figures are regenerated under `figures/`.
- [x] Paper source is `paper/main.tex`.
- [x] Canonical batch PDF path is `C:/Users/wangz/Downloads/20.pdf`.
- [x] Local `paper/main.pdf` was deleted after copying the canonical PDF to Downloads.

Recommended verification commands:

```powershell
python experiments\run_ejar_synthetic.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```
