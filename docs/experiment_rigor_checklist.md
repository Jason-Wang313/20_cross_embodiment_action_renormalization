# Experiment Rigor Checklist

- [x] Runnable v2 experiment: `python experiments/run_ejar_synthetic.py`.
- [x] Paper-specific v3 execution plan written before full-scale edits: `docs/full_scale_execution_plan.md`.
- [x] RAM-light full-scale runner: `python experiments/full_scale_ejar.py`.
- [x] Full-scale runner completed with `metadata.json` stage `complete`.
- [x] Total v3 rows: 114,040.
- [x] Trajectory/learned-policy decision rows: 19,440.
- [x] Plot failures: 0.
- [x] Main morphology sweep includes raw joint copy, normalized copy, link-scaled copy, static-home decoder, target IK, EJAR absolute, and EJAR capability-token decoding.
- [x] Long-horizon transfer covers horizons 8, 16, 32, and 64.
- [x] Learned action-interface stress covers pooled raw labels, robot-ID raw labels, morphology-conditioned raw labels, effect labels, and capability-token labels.
- [x] Model-error stress covers exact, noisy, biased, column-dropped, finite-difference, and stale Jacobians.
- [x] Residual calibration reports AUROC/AUPRC and false reassurance.
- [x] Boundary tests cover semantic task-map mismatch, control-rate/latency mismatch, and a contact-effect proxy.
- [x] Negative controls include matched morphology, random map, zero effect, same geometry/different limits, and same limits/different geometry.
- [x] Final manuscript imports generated tables and figures.
- [x] Final PDF is 26 pages.
- [ ] Real multi-robot logs.
- [ ] Contact-rich real manipulation.
- [ ] Learned visual policy benchmark.
- [ ] Hardware Jacobian calibration study.

Decision: submission-ready as a synthetic mechanism paper with explicit real-robot limitations.
