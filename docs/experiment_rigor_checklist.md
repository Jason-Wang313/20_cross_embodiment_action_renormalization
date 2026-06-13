# Experiment Rigor Checklist

- [x] Runnable experiment: `python experiments/run_ejar_synthetic.py`.
- [x] One-step transfer trials: 9,600 method rows.
- [x] Trajectory transfer episodes: 480 method rows.
- [x] V2 Jacobian-noise stress rows: 9,000.
- [x] Baselines include raw normalized action copying, EJAR absolute-effect decoding, and EJAR capability-token decoding.
- [x] Stress includes near-singular configurations and noisy estimated target Jacobians.
- [x] Outputs include CSVs, JSON summary, generated LaTeX stress table, and figures.
- [ ] Real multi-robot logs.
- [ ] Contact-rich manipulation.
- [ ] Learned or measured Jacobian estimates.
- [ ] Task-correspondence mismatch stress.

Decision: rigorous enough for workshop-only / strong-revise positioning; not enough for full submission claims.
