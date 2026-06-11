# Plan

## Goal
Produce an honest, runnable, anonymous ICLR-style robotics paper for paper 20, starting from the seed "Cross Embodiment Action Renormalization" but allowing the literature to change the thesis. The final repo must include literature artifacts, runnable evidence, paper source, compiled PDF at `C:/Users/wangz/Downloads/20.pdf`, GitHub push status, and `docs/final_audit.md`.

## Execution Stages

1. **Environment and resume check**
   - Inspect the existing folder without deleting useful artifacts.
   - Record tool availability safely in `child_status.md`.
   - Create `docs/`, `scripts/`, `experiments/`, `paper/`, and `figures/` if needed.

2. **Literature sweep**
   - Build or reuse cached literature data.
   - Collect at least 1000 candidate robotics / embodied intelligence papers relevant to cross-embodiment learning, robot action spaces, retargeting, morphology transfer, manipulation, sim-to-real, and robot foundation policies.
   - Save `docs/related_work_matrix.csv` with mechanism, assumptions, fixed variables, ignored failure modes, novelty impact, and open questions.
   - Produce the required 1000-paper landscape, 300-paper serious skim, 200-250-paper deep read, and 100-paper hostile prior-work set as structured artifacts.

3. **Novelty decision**
   - Define the field box and list at least 20 false-prone hidden assumptions.
   - Generate competing paper directions that break those assumptions.
   - Select the strongest direction only after hostile prior-work comparison.
   - Save `docs/literature_map.md`, `docs/hostile_prior_work.md`, `docs/novelty_boundary_map.md`, `docs/novelty_decision.md`, `docs/claims.md`, and `docs/reviewer_attacks.md`.

4. **Mechanism and evidence**
   - Specify a central mechanism that is not merely a bigger model, more data, benchmark, uncertainty, active learning, verifier, module combination, LLM planner, or generic RL.
   - Implement a small runnable synthetic embodied-control experiment that can demonstrate whether the broken assumption matters.
   - Save code, outputs, plots, and a concise experiment report.

5. **Paper writing**
   - Fetch or install the latest available official ICLR style files at runtime when possible; otherwise document fallback.
   - Write an anonymous ICLR-style LaTeX paper with honest claims, hostile prior-work boundaries, method, evidence, limitations, and reproducibility details.
   - Sanitize BibTeX/LaTeX for pdfLaTeX.

6. **Build and verify**
   - Compile with direct `pdflatex`, `bibtex`, `pdflatex`, `pdflatex` using explicit generous timeouts.
   - Copy the final PDF only to `C:/Users/wangz/Downloads/20.pdf`.
   - Document any build failure and recovery.

7. **Repository publication**
   - Ensure the repo is runnable with a README.
   - Commit intentional changes.
   - Create and push public GitHub repo `20_cross_embodiment_action_renormalization` if authenticated tooling allows.
   - Record the GitHub URL or exact failure.

8. **Final audit**
   - Write `docs/final_audit.md` answering all required audit questions, including Desktop copy status as `pending orchestrator copy` unless appended later.

## Safety Rules

- Avoid bare probes that can abort the run; use safe checks and explicit timeouts.
- Do not delete existing caches unless proven invalid.
- Keep `child_status.md` updated by rewriting from current facts.
- Prefer resumable scripts for literature, experiments, and paper building.
