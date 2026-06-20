# Full-Scale Execution Plan for Paper 20

Paper: 20, `20_cross_embodiment_action_renormalization`

Working title: Cross-Embodiment Action Renormalization

Date: 2026-06-14

## 1. Current State Before v3 Work

The v2 paper is a short mechanism note. It argues that cross-embodiment policies should not share raw componentwise actuator commands, because the same normalized coordinate does not imply the same local physical task effect on different robot bodies. The proposed mechanism, Effect-Jacobian Action Renormalization (EJAR), encodes actions through a local action-to-effect map and decodes them through the target embodiment's local Jacobian and actuator limits.

Current evidence:

- One synthetic planar-arm source and three target arms.
- One-step transfer over 9,600 method rows.
- Trajectory transfer over 480 method rows.
- Jacobian-noise stress over 9,000 rows.
- Main v2 numbers:
  - raw copy mean one-step relative effect error 1.252;
  - EJAR absolute-effect mean one-step relative effect error 0.265;
  - EJAR capability-token error 0.016;
  - trajectory success at 0.10 improves from 0.371 to 0.792;
  - at 20 percent Jacobian noise, EJAR absolute-effect mean relative error rises from 0.266 to 0.429.

Current readiness:

- The repo is clean and pushed at v2.
- `C:\Users\wangz\Downloads\20.pdf` has been removed because the old 7-page PDF is not final under the strict 25-page standard.
- The old PDF is archived at `C:\Users\wangz\robotics_60_paper_batch\_nonfinal_download_exports_archive\20260614_before_strict_goal\20.pdf`.
- Local `paper/main.pdf` is absent.
- The v2 decision before this full-scale pass was workshop/revise, not submission-ready.

## 2. Target v3 Claim

The v3 paper should not claim that EJAR solves all cross-embodiment transfer. The final claim should be:

> Componentwise action normalization is an unsafe default cross-embodiment action interface because it does not preserve local task effects under morphology, configuration, actuator-limit, control-rate, and conditioning changes. EJAR is a local action-token interface that uses each robot's action-to-effect map to preserve feasible first-order task effects or report infeasibility through a residual. In a broad deterministic synthetic suite, EJAR reduces effect mismatch, improves trajectory transfer, gives a calibrated infeasibility signal under model validity, and exposes where the method fails under Jacobian error, task-map mismatch, singularity, saturation, latency, and contact-mode changes.

The contribution is an action-interface and diagnostic contribution, not a new operational-space controller.

## 3. Main Reviewer Attacks to Answer

1. This is just operational-space control.
   - Response: concede the controller math, then show the paper's object is the action token at the policy/data interface. Add a table separating controller novelty, action-interface novelty, and unsupported novelty.

2. Synthetic planar arms are too weak.
   - Response: expand from one toy setup to a broad, deterministic, multi-family synthetic benchmark with many arm morphologies, DOF mismatches, control rates, actuator modes, nullspace, residual calibration, learned-token imitation, and contact-proxy failure cases. Still say real hardware is not proven.

3. Raw normalized copy is a straw baseline.
   - Response: add stronger baselines:
   - raw normalized copy;
   - per-body range-scaled copy;
   - end-effector delta IK without capability normalization;
   - static home-configuration Jacobian decoder;
   - morphology-conditioned linear decoder;
   - oracle true-Jacobian decoder;
   - learned linear token decoder trained from calibration samples;
   - source-only action policy and pooled raw-action imitation policy.

4. Learned policies can infer embodiment mismatch from data.
   - Response: add a behavioral-cloning stress where the same goal-conditioned policy is trained over different action labels: raw actions, robot-ID-conditioned raw actions, morphology-conditioned raw actions, absolute effects, and capability tokens. Evaluate target transfer at low, medium, and high calibration-data budgets.

5. Jacobians are unavailable or wrong.
   - Response: keep the existing noise stress but broaden it to calibration-sample estimation, finite-difference estimation, bias, dropout, and latency. Report residual calibration error and infeasible-effect detection.

6. Capability tokens change the task instead of preserving source displacement.
   - Response: separate two modes everywhere: absolute-effect transfer and capability-token command authority. Report both with separate metrics and clear interpretations.

7. Clipping and singularities destroy the guarantee.
   - Response: make clipping/singularity an explicit experiment family. Report residual AUPRC/AUROC for infeasible-effect detection and show where EJAR correctly says "cannot realize this effect."

8. Task-map correspondence is assumed.
   - Response: add a task-map mismatch stress and state that EJAR cannot rescue wrong task semantics. This should narrow the final claim, not be hidden.

9. Contact-rich manipulation invalidates first-order free-space Jacobians.
   - Response: add a deliberately limited contact-proxy experiment with a 2D object push map and contact-mode mismatch. Use it to identify failure boundaries, not to claim real manipulation.

10. The literature sweep is shallow.
   - Response: keep it transparent as automated hostile coverage; add a concise manual-boundary discussion for the closest families: operational-space control, retargeting/teleoperation, morphology-conditioned learning, robot foundation policies, and action sequence models.

## 4. Full-Scale Experiment Suite

The v3 suite will be implemented as a new RAM-light sequential runner:

`experiments/full_scale_ejar.py`

Outputs:

- `results/full_scale/metadata.json`
- `results/full_scale/progress.json`
- `results/full_scale/family_*_seed.csv`
- `results/full_scale/family_*_summary.csv`
- `results/full_scale/table_*.tex`
- `results/full_scale/figure_*.pdf`
- `results/full_scale/figure_*.png`

The runner should stream each family to disk and compute summaries incrementally. It must avoid retaining large raw arrays in memory. It may retain compact per-method metric vectors for plots where the expected row count is modest. Large family rows should be written to CSV immediately and summarized from running aggregates.

### Family A: Embodiment Diversity Main Sweep

Question: does EJAR preserve task effects across many source-target morphology pairs better than raw action normalization and stronger non-EJAR baselines?

Design:

- Generate deterministic source-target pairs from 2-link, 3-link, 4-link, 5-link, and 6-link planar arms.
- Vary link scales, actuator limits, redundancy, workspace overlap, and target conditioning.
- Include near-singular and regular configurations.
- Methods:
  - raw normalized copy;
  - range-scaled copy;
  - static home-Jacobian decoder;
  - target damped IK absolute-effect decoder;
  - EJAR absolute-effect decoder;
  - EJAR capability-token decoder;
  - oracle true-effect decoder for upper-bound interpretation.
- Metrics:
  - relative effect error;
  - cosine alignment;
  - absolute effect norm error;
  - capability-token error;
  - clip rate;
  - residual;
  - condition number;
  - target/source rank and DOF mismatch.

Acceptance target:

- The summary should show raw and range-scaled copying are not reliable across morphology pairs.
- EJAR absolute should reduce effect error versus raw/range/static baselines.
- Capability-token should be best only on token-relative metrics, not misrepresented as absolute displacement preservation.

### Family B: Long-Horizon Trajectory Transfer

Question: do one-step action-interface errors compound during transferred action sequences?

Design:

- Source generates goal-directed task-effect sequences toward randomized workspace goals.
- Transfer sequences to targets for horizons 8, 16, 32, and 64.
- Evaluate open-loop and feedback-corrected variants.
- Methods:
  - raw copy;
  - range-scaled copy;
  - static home-Jacobian decoder;
  - EJAR absolute;
  - EJAR with residual fallback that shrinks infeasible effects;
  - oracle target IK.
- Metrics:
  - final tracking error;
  - mean path error;
  - success at thresholds 0.05, 0.10, 0.20;
  - accumulated residual;
  - number of clipped steps;
  - failure mode label.

Acceptance target:

- EJAR should improve median and success-rate transfer over raw/range baselines, especially as horizon increases.
- Failures under infeasible and singular configurations should remain visible.

### Family C: Learned Action-Interface Stress

Question: can a simple learned policy infer embodiment mismatch, and does an effect-token action representation make learning easier?

Design:

- Generate supervised goal-conditioned training data from multiple source arms.
- Train small closed-form ridge models or compact MLP-free linear decoders using NumPy only:
  - source-only raw action model;
  - pooled raw action model;
  - robot-ID-conditioned raw action model;
  - morphology-feature-conditioned raw action model;
  - absolute-effect label model;
  - capability-token label model.
- Decode labels on held-out target arms.
- Vary training data budgets: 100, 500, 2,000, and 8,000 samples.
- Vary held-out morphology severity.

Metrics:

- final reaching success;
- one-step goal-progress error;
- train/test label error;
- transfer degradation from seen to unseen morphologies;
- number of target-specific calibration samples needed.

Acceptance target:

- Do not claim neural policies cannot learn the mapping. Instead report whether explicit effect labels remain competitive or more stable at low and medium data budgets.

### Family D: Jacobian Estimation and Model Error

Question: how much does EJAR rely on a correct local action-effect model?

Design:

- Decode using target Jacobians with:
  - Gaussian noise;
  - structured scale bias;
  - column dropout;
  - finite-difference estimates from K calibration samples;
  - stale Jacobians from previous configurations;
  - latency-shifted configurations.
- Evaluate realized effect under the true Jacobian.

Metrics:

- mean and p90 relative effect error;
- residual gap;
- residual calibration slope/intercept;
- true infeasible residual;
- estimated residual;
- calibration-sample budget sensitivity.

Acceptance target:

- The paper must show degradation clearly and use it to narrow claims.
- Residuals should be reliable only when the local model is reliable.

### Family E: Feasibility, Singularity, and Residual Calibration

Question: does EJAR's residual identify infeasible requests rather than silently failing?

Design:

- Sample requested effects at increasing fractions of each target's local capability ellipsoid.
- Include rank-deficient, near-singular, saturated, and out-of-workspace local requests.
- Label infeasible rows by oracle best achievable residual.
- Methods:
  - EJAR residual;
  - static-Jacobian residual;
  - action-norm heuristic;
  - condition-number heuristic.

Metrics:

- AUROC/AUPRC for infeasible-effect detection;
- Brier score / expected calibration error for residual-normalized infeasibility;
- residual vs true error correlation;
  - false reassurance rate: low reported residual with high realized error.

Acceptance target:

- Residual should be useful under known-model assumptions.
- Explicitly report false reassurance under model error.

### Family F: Task-Map and Correspondence Mismatch

Question: what happens when source and target task maps are not semantically aligned?

Design:

- Create task-map transformations:
  - correct shared end-effector map;
  - rotated task frame;
  - scaled axis;
  - swapped axes;
  - wrong contact point on a redundant arm;
  - missing gripper/contact coordinate.
- Use EJAR with the wrong assumed target map and evaluate in the true task frame.

Metrics:

- effect error under assumed map;
- effect error under true map;
- residual gap;
- failure mode classification.

Acceptance target:

- EJAR cannot fix wrong semantic correspondences. This should strengthen the paper by making the limitation experimentally visible.

### Family G: Control-Rate, Latency, and Action-Mode Mismatch

Question: does action-interface mismatch include timing and actuator-mode differences?

Design:

- Simulate velocity, position-delta, and torque-proxy action semantics through first-order local maps.
- Vary control period, latency, action hold, actuator saturation, and smoothing.
- Test whether EJAR with the correct per-step action map handles rate changes better than componentwise normalization.

Metrics:

- one-step and multi-step effect error;
- success under rate mismatch;
- latency sensitivity;
- residual gap.

Acceptance target:

- The paper should show that EJAR is an action-effect interface, so the map must include the action mode and control period.

### Family H: Contact-Proxy Boundary

Question: how far can a local effect map help when contact changes the task map?

Design:

- Implement a simple 2D pushing/contact proxy:
  - arm endpoint applies a local push to an object;
  - object motion depends on contact normal, friction-like anisotropy, and contact mode;
  - wrong contact mode causes effect-map mismatch.
- Compare raw copy, end-effector EJAR, and contact-effect EJAR when the contact mode is known or wrong.

Metrics:

- object displacement error;
- contact-mode mismatch rate;
- residual gap;
- success at moving object toward goal.

Acceptance target:

- Known contact-effect map can help in the toy proxy.
- Wrong contact mode breaks the claim. This remains a boundary experiment, not real manipulation evidence.

### Family I: Negative Controls and Sanity Checks

Question: are results coming from the intended mechanism?

Design:

- Matched source-target morphology where raw copy should perform well.
- Randomized Jacobian labels where EJAR should fail.
- Zero-effect actions where all methods should report small effects.
- Same morphology but different actuator limits.
- Same actuator limits but different link geometry.

Metrics:

- expected success/failure by control.
- mechanism isolation table.

Acceptance target:

- The matched-morphology control prevents overstating raw-copy failure.
- Randomized-map control prevents overstating EJAR under invalid maps.

### Family J: Runtime, Memory, and Reproducibility

Question: can a reviewer rerun the suite?

Design:

- Log wall time by family.
- Log peak row counts and output sizes.
- Store metadata: Python version, NumPy version, matplotlib version, seed list, command, and generated files.

Acceptance target:

- `metadata.json` must report total seed rows, total simulated episodes/trials, zero plot failures, and final stage complete.

## 5. Page-Count Strategy

The final manuscript must be at least 25 pages. Page count must come from real content:

- main paper with abstract, introduction, related work, method, formal proposition, experiment overview, main result tables/figures, limitations, and conclusion;
- appendix A: notation and action-token definitions;
- appendix B: proof details and exact assumptions;
- appendix C: experiment suite protocol by family;
- appendix D: full table set;
- appendix E: residual calibration and infeasibility analysis;
- appendix F: learned action-interface stress;
- appendix G: task-map mismatch and contact-proxy boundaries;
- appendix H: negative controls;
- appendix I: reproducibility, runtime, memory, and artifact audit;
- appendix J: reviewer self-attacks and claim boundary.

Do not use filler. If the paper is short after adding real evidence, add real appendices: per-family acceptance criteria, failure-case narratives, exact robot morphology tables, metric definitions, and generated artifact schema.

## 6. Writing and Claim Policy

The final paper should use these claim rules:

- Say "synthetic deterministic suite" rather than "robot benchmark" unless no real robots are used.
- Do not say EJAR is novel as a controller.
- Do not say EJAR solves correspondence, contact manipulation, learned perception, hardware calibration, or policy scaling.
- Do not compare to foundation policies as if a small simulator beats them.
- Do say that EJAR isolates an action-interface invariant and can be used as a diagnostic/layer.
- If Windowed/learned/morphology baselines beat EJAR in a metric, report that directly and narrow the claim.
- Keep absolute-effect transfer and capability-token transfer separated.

## 7. Implementation Plan

1. Add `experiments/full_scale_ejar.py`.
2. Reuse robust pieces from `experiments/run_ejar_synthetic.py`: `PlanarArm`, Jacobian, clipping, pseudoinverse, CSV writing, plotting.
3. Extend `PlanarArm` to support variable DOF, task frames, control periods, and finite-difference Jacobian estimation.
4. Implement family functions one at a time. Each family writes its own seed CSV, summary CSV, and LaTeX table.
5. Add a progress JSON after each family so a timeout does not lose completed work.
6. Keep plotting late and isolated so a plotting failure does not destroy numeric results.
7. Generate manuscript-ready tables and figures under `results/full_scale/`.
8. Run `python -m py_compile` on both experiment scripts.
9. Run the full suite once to completion.
10. Inspect summaries for overclaims and update the final claim.
11. Replace `paper/main.tex` with the full v3 manuscript importing generated tables/figures.
12. Compile locally, inspect page count, iterate until at least 25 pages.
13. Only when final: copy to `C:\Users\wangz\Downloads\20.pdf`.
14. Verify PDF markers, page count, text, hash, and absence of `paper/main.pdf`.
15. Update README, child status, claims, attack log, version log, readiness decision, reproducibility checklist, final audit, and hostile reviewer response.
16. Commit and push.

## 8. RAM-Light Execution Strategy

- Families run sequentially.
- CSV rows are streamed to disk with `csv.DictWriter`.
- Running aggregates use counts, sums, squared sums, min, max, and compact percentile reservoirs where possible.
- Only modest vectors needed for figures are retained.
- No multiprocessing unless a family is proven slow and memory-stable.
- No large in-memory pandas dataframes.
- Metadata and progress are written after every family.
- If a run times out, resume by skipping families whose CSV and summary already exist only after validating their metadata.

## 9. Final Acceptance Checklist Before Moving to Paper 21

- `docs/full_scale_execution_plan.md` exists and reflects this v3 work.
- Full-scale runner completes with `metadata.json` stage `complete`.
- Full-scale results include at least Families A-I plus runtime metadata.
- Tables and figures are generated and imported by the paper.
- Manuscript visibly says `Submission-hardening version: v3`.
- Paper is at least 25 pages by PDF page count.
- Final PDF exists at `C:\Users\wangz\Downloads\20.pdf`.

## 2026-06-20 VLA-Style Link Hardening Addendum

After the v3 scientific content was finalized, the canonical PDF was rebuilt
with explicit VLA-style `hyperref` boxed-link settings. This addendum does not
change experiments, claims, figures, tables, bibliography content, or page
count. It only hardens final PDF presentation:

- citation links use green one-point boxes;
- URL links use green one-point boxes;
- internal section/table/figure links use red one-point boxes;
- no cyan URL boxes appear;
- affected link pages 1, 2, 3, 16, and 17 were rendered and visually checked
  against the visible VLA-v4 role model.
- `C:\Users\wangz\Downloads\20.pdf` is verified as the actual Paper20 final.
- Old short `20.pdf` remains outside Downloads.
- Local `paper/main.pdf` is removed after final export.
- Docs/logs/checklists/readiness decision are updated.
- Claims are narrowed to match evidence.
- `python -m py_compile experiments\run_ejar_synthetic.py experiments\full_scale_ejar.py` passes.
- LaTeX build completes with `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.
- `git diff --check` passes.
- Changes are committed with a clear v3 full-scale message.
- Commit is pushed and `HEAD == @{u}`.
- Worktree is clean.
