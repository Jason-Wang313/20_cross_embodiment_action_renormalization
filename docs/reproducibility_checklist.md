# Reproducibility Checklist

- [x] Dependencies are listed in `requirements.txt`.
- [x] Original v2 experiment source is `experiments/run_ejar_synthetic.py`.
- [x] Full-scale v3 experiment source is `experiments/full_scale_ejar.py`.
- [x] Full-scale outputs are under `results/full_scale/`.
- [x] Full-scale metadata is `results/full_scale/metadata.json`.
- [x] Full-scale progress is `results/full_scale/progress.json`.
- [x] Generated tables are `results/full_scale/table_*.tex`.
- [x] Generated figures are `results/full_scale/figure_*.pdf` and `.png`.
- [x] Evidence summary is `docs/evidence_summary.md`.
- [x] Paper source is `paper/main.tex`.
- [x] Canonical batch PDF path is `C:\Users\wangz\Downloads\20.pdf`.
- [x] Final PDF page count: 26.
- [x] Final PDF bytes: 409,298.
- [x] Final PDF SHA256: `106CC7757D60C2D17A1434DFE281981F745922B90855E29CE6E260FC0CF66E94`.
- [x] VLA-style boxed links: 60 annotations; pages `[(1, 16), (2, 25), (3, 13), (16, 1), (17, 5)]`; colors green = 54, red = 6, cyan = 0; all borders `(0, 0, 1)`.
- [x] Local `paper/main.pdf` removed after copying the canonical final PDF to Downloads.

Recommended verification commands:

```powershell
python -m py_compile experiments\run_ejar_synthetic.py experiments\full_scale_ejar.py
python experiments\full_scale_ejar.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdftotext C:\Users\wangz\Downloads\20.pdf - | rg "Submission-hardening version: v3|114,040|19,440|1\.215|0\.231|0\.908|Final Audit"
Get-FileHash C:\Users\wangz\Downloads\20.pdf -Algorithm SHA256
```
