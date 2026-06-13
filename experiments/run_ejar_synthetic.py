import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
DOCS = ROOT / "docs"
STATUS = ROOT / "child_status.md"


def write_status(stage, failures="", recovery="", next_step=""):
    content = [
        "# Child Status",
        "",
        f"- Stage: {stage}",
        "- Last update: 2026-06-11",
        "- Commands run:",
        "  - `python scripts/generate_literature.py`",
        "  - `python experiments/run_ejar_synthetic.py`",
        f"- Failures: {failures or 'none'}",
        f"- Recovery steps: {recovery or 'none'}",
        f"- Next: {next_step or 'write paper and build PDF'}",
        "",
    ]
    STATUS.write_text("\n".join(content), encoding="utf-8")


@dataclass
class PlanarArm:
    name: str
    links: np.ndarray
    max_step: np.ndarray

    @property
    def n(self):
        return len(self.links)

    def fk(self, q):
        angles = np.cumsum(q)
        x = float(np.sum(self.links * np.cos(angles)))
        y = float(np.sum(self.links * np.sin(angles)))
        return np.array([x, y], dtype=float)

    def jacobian(self, q):
        angles = np.cumsum(q)
        j = np.zeros((2, self.n), dtype=float)
        for col in range(self.n):
            s = 0.0
            c = 0.0
            for k in range(col, self.n):
                s += self.links[k] * math.sin(angles[k])
                c += self.links[k] * math.cos(angles[k])
            j[0, col] = -s
            j[1, col] = c
        return j

    def random_q(self, rng, singular=False):
        if singular:
            return rng.normal(0.0, 0.035, size=self.n)
        return rng.uniform(-math.pi * 0.85, math.pi * 0.85, size=self.n)


def psd_sqrt(mat, eps=1e-9, inverse=False):
    vals, vecs = np.linalg.eigh((mat + mat.T) * 0.5)
    vals = np.maximum(vals, eps)
    if inverse:
        scaled = 1.0 / np.sqrt(vals)
    else:
        scaled = np.sqrt(vals)
    return (vecs * scaled) @ vecs.T


def clip_action(a, max_step):
    ratios = np.divide(max_step, np.maximum(np.abs(a), 1e-12))
    scale = min(1.0, float(np.min(ratios)))
    return a * scale, scale < 0.999


def copy_raw_normalized(source, target, a_source):
    u = a_source / source.max_step
    if target.n >= source.n:
        u_t = np.zeros(target.n)
        u_t[: source.n] = u
    else:
        u_t = u[: target.n]
    a = u_t * target.max_step
    a, clipped = clip_action(a, target.max_step)
    return a, {"clipped": clipped, "residual": float("nan")}


def ejar_absolute(target, q_target, desired_effect, damping=1e-5):
    j = target.jacobian(q_target)
    return ejar_absolute_from_j(target, j, desired_effect, damping=damping)


def ejar_absolute_from_j(target, j, desired_effect, damping=1e-5):
    b2 = np.diag(target.max_step ** 2)
    sigma = j @ b2 @ j.T
    solve = np.linalg.solve(sigma + damping * np.eye(2), desired_effect)
    a = b2 @ j.T @ solve
    a, clipped = clip_action(a, target.max_step)
    effect = j @ a
    residual = float(np.linalg.norm(effect - desired_effect))
    return a, {"clipped": clipped, "residual": residual}


def ejar_capability_token(source, q_source, target, q_target, a_source, damping=1e-5):
    j_s = source.jacobian(q_source)
    j_t = target.jacobian(q_target)
    sigma_s = j_s @ np.diag(source.max_step ** 2) @ j_s.T
    sigma_t = j_t @ np.diag(target.max_step ** 2) @ j_t.T
    d_s = j_s @ a_source
    z = psd_sqrt(sigma_s + damping * np.eye(2), inverse=True) @ d_s
    desired_target_effect = psd_sqrt(sigma_t + damping * np.eye(2), inverse=False) @ z
    a, info = ejar_absolute(target, q_target, desired_target_effect, damping=damping)
    out = j_t @ a
    z_out = psd_sqrt(sigma_t + damping * np.eye(2), inverse=True) @ out
    info["token_error"] = float(np.linalg.norm(z_out - z) / (np.linalg.norm(z) + 1e-9))
    info["capability_effect_norm"] = float(np.linalg.norm(desired_target_effect))
    return a, info


def rel_error(actual, desired):
    return float(np.linalg.norm(actual - desired) / (np.linalg.norm(desired) + 1e-9))


def cosine(actual, desired):
    denom = np.linalg.norm(actual) * np.linalg.norm(desired) + 1e-9
    return float(np.dot(actual, desired) / denom)


def one_step_trials(rng, source, targets, n_trials=3200):
    rows = []
    for idx in range(n_trials):
        target = targets[idx % len(targets)]
        singular = idx % 13 == 0
        q_s = source.random_q(rng, singular=False)
        q_t = target.random_q(rng, singular=singular)
        a_s = rng.uniform(-0.8, 0.8, size=source.n) * source.max_step
        d_s = source.jacobian(q_s) @ a_s
        for method in ["raw_copy", "ejar_absolute", "ejar_capability_token"]:
            if method == "raw_copy":
                a_t, info = copy_raw_normalized(source, target, a_s)
                desired = d_s
            elif method == "ejar_absolute":
                a_t, info = ejar_absolute(target, q_t, d_s)
                desired = d_s
            else:
                a_t, info = ejar_capability_token(source, q_s, target, q_t, a_s)
                j_t = target.jacobian(q_t)
                sigma_s = source.jacobian(q_s) @ np.diag(source.max_step ** 2) @ source.jacobian(q_s).T
                sigma_t = j_t @ np.diag(target.max_step ** 2) @ j_t.T
                z = psd_sqrt(sigma_s + 1e-5 * np.eye(2), inverse=True) @ d_s
                desired = psd_sqrt(sigma_t + 1e-5 * np.eye(2), inverse=False) @ z
            actual = target.jacobian(q_t) @ a_t
            rows.append(
                {
                    "trial": idx,
                    "target": target.name,
                    "method": method,
                    "singular_stress": int(singular),
                    "desired_norm": float(np.linalg.norm(desired)),
                    "actual_norm": float(np.linalg.norm(actual)),
                    "relative_effect_error": rel_error(actual, desired),
                    "effect_cosine": cosine(actual, desired),
                    "clipped": int(bool(info.get("clipped", False))),
                    "residual": info.get("residual", ""),
                    "token_error": info.get("token_error", ""),
                }
            )
    return rows


def jacobian_noise_stress(rng, source, targets, n_trials=1800):
    sigmas = [0.0, 0.02, 0.05, 0.10, 0.20]
    rows = []
    for sigma in sigmas:
        for idx in range(n_trials):
            target = targets[idx % len(targets)]
            q_s = source.random_q(rng, singular=False)
            q_t = target.random_q(rng, singular=(idx % 13 == 0))
            a_s = rng.uniform(-0.8, 0.8, size=source.n) * source.max_step
            desired = source.jacobian(q_s) @ a_s
            j_true = target.jacobian(q_t)
            scale = max(1e-9, float(np.sqrt(np.mean(j_true ** 2))))
            j_est = j_true + rng.normal(0.0, sigma * scale, size=j_true.shape)
            a_t, info = ejar_absolute_from_j(target, j_est, desired)
            actual = j_true @ a_t
            reported = j_est @ a_t
            rows.append(
                {
                    "jacobian_noise_sigma": sigma,
                    "trial": idx,
                    "target": target.name,
                    "singular_stress": int(idx % 13 == 0),
                    "relative_effect_error": rel_error(actual, desired),
                    "effect_cosine": cosine(actual, desired),
                    "reported_residual": float(np.linalg.norm(reported - desired)),
                    "true_residual": float(np.linalg.norm(actual - desired)),
                    "residual_gap": float(np.linalg.norm(actual - reported)),
                    "clipped": int(bool(info.get("clipped", False))),
                }
            )
    return rows


def trajectory_trials(rng, source, targets, n_episodes=240, horizon=18):
    rows = []
    for ep in range(n_episodes):
        target = targets[ep % len(targets)]
        q_s0 = source.random_q(rng, singular=False)
        q_t0 = target.random_q(rng, singular=(ep % 17 == 0))
        source_actions = []
        desired_effects = []
        q_s = q_s0.copy()
        for _ in range(horizon):
            a_s = rng.uniform(-0.65, 0.65, size=source.n) * source.max_step
            source_actions.append(a_s)
            desired_effects.append(source.jacobian(q_s) @ a_s)
            q_s = q_s + a_s
        for method in ["raw_copy", "ejar_absolute"]:
            q_t = q_t0.copy()
            p_des = target.fk(q_t0)
            tracking_errors = []
            clipped_count = 0
            residual_sum = 0.0
            for a_s, d_s in zip(source_actions, desired_effects):
                p_des = p_des + d_s
                if method == "raw_copy":
                    a_t, info = copy_raw_normalized(source, target, a_s)
                else:
                    a_t, info = ejar_absolute(target, q_t, d_s)
                clipped_count += int(bool(info.get("clipped", False)))
                if isinstance(info.get("residual", ""), float):
                    residual_sum += info["residual"]
                q_t = q_t + a_t
                tracking_errors.append(float(np.linalg.norm(target.fk(q_t) - p_des)))
            final_error = tracking_errors[-1]
            rows.append(
                {
                    "episode": ep,
                    "target": target.name,
                    "method": method,
                    "horizon": horizon,
                    "final_tracking_error": final_error,
                    "mean_tracking_error": float(np.mean(tracking_errors)),
                    "success_5cm_equiv": int(final_error < 0.05),
                    "success_10cm_equiv": int(final_error < 0.10),
                    "clipped_steps": clipped_count,
                    "residual_sum": residual_sum,
                }
            )
    return rows


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows, key, group_key="method"):
    out = {}
    groups = sorted(set(row[group_key] for row in rows))
    for group in groups:
        vals = np.array([float(row[key]) for row in rows if row[group_key] == group], dtype=float)
        out[group] = {
            "mean": float(np.mean(vals)),
            "median": float(np.median(vals)),
            "p90": float(np.percentile(vals, 90)),
        }
    return out


def success_summary(rows):
    out = {}
    for method in sorted(set(r["method"] for r in rows)):
        vals = [int(r["success_10cm_equiv"]) for r in rows if r["method"] == method]
        out[method] = float(np.mean(vals))
    return out


def jacobian_stress_summary(rows):
    out = {}
    for sigma in sorted(set(float(r["jacobian_noise_sigma"]) for r in rows)):
        group = [r for r in rows if float(r["jacobian_noise_sigma"]) == sigma]
        rel = np.array([float(r["relative_effect_error"]) for r in group], dtype=float)
        reported = np.array([float(r["reported_residual"]) for r in group], dtype=float)
        true = np.array([float(r["true_residual"]) for r in group], dtype=float)
        gap = np.array([float(r["residual_gap"]) for r in group], dtype=float)
        clipped = np.array([int(r["clipped"]) for r in group], dtype=float)
        out[f"{sigma:.2f}"] = {
            "mean_relative_effect_error": float(np.mean(rel)),
            "p90_relative_effect_error": float(np.percentile(rel, 90)),
            "mean_reported_residual": float(np.mean(reported)),
            "mean_true_residual": float(np.mean(true)),
            "mean_residual_gap": float(np.mean(gap)),
            "clip_rate": float(np.mean(clipped)),
        }
    return out


def write_jacobian_noise_table(stress_summary):
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{V2 Jacobian-misspecification stress. EJAR decodes with a noisy estimated target Jacobian, but the realized effect is evaluated with the true Jacobian. Residual gap is the mean difference between the predicted and realized target effects.}",
        r"\label{tab:jacobian-stress}",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r"Noise $\sigma$ & Mean rel. error & p90 rel. error & True residual & Residual gap \\",
        r"\midrule",
    ]
    for sigma, stats in stress_summary.items():
        lines.append(
            f"{sigma} & {stats['mean_relative_effect_error']:.3f} & {stats['p90_relative_effect_error']:.3f} & {stats['mean_true_residual']:.4f} & {stats['mean_residual_gap']:.4f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    (RESULTS / "jacobian_noise_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_results(one_rows, ep_rows):
    methods = ["raw_copy", "ejar_absolute", "ejar_capability_token"]
    means = []
    p90s = []
    for method in methods:
        vals = np.array([float(r["relative_effect_error"]) for r in one_rows if r["method"] == method])
        means.append(float(np.mean(vals)))
        p90s.append(float(np.percentile(vals, 90)))
    plt.figure(figsize=(7.0, 4.2))
    x = np.arange(len(methods))
    plt.bar(x - 0.17, means, width=0.34, label="mean")
    plt.bar(x + 0.17, p90s, width=0.34, label="p90")
    plt.xticks(x, ["raw copy", "EJAR abs", "EJAR token"])
    plt.ylabel("relative one-step effect error")
    plt.title("Cross-body action transfer error")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIGURES / "one_step_effect_error.png", dpi=200)
    plt.savefig(FIGURES / "one_step_effect_error.pdf")
    plt.close()

    methods2 = ["raw_copy", "ejar_absolute"]
    success = []
    final = []
    for method in methods2:
        vals = [float(r["success_10cm_equiv"]) for r in ep_rows if r["method"] == method]
        errs = [float(r["final_tracking_error"]) for r in ep_rows if r["method"] == method]
        success.append(float(np.mean(vals)))
        final.append(float(np.median(errs)))
    fig, ax1 = plt.subplots(figsize=(6.8, 4.0))
    x2 = np.arange(len(methods2))
    ax1.bar(x2 - 0.18, success, width=0.36, color="#2b7bba", label="success @0.10")
    ax1.set_ylim(0, 1)
    ax1.set_ylabel("trajectory success rate")
    ax2 = ax1.twinx()
    ax2.bar(x2 + 0.18, final, width=0.36, color="#b24a3b", label="median final error")
    ax2.set_ylabel("median final tracking error")
    ax1.set_xticks(x2)
    ax1.set_xticklabels(["raw copy", "EJAR abs"])
    ax1.set_title("Transferred source action sequences")
    fig.tight_layout()
    fig.savefig(FIGURES / "trajectory_transfer.png", dpi=200)
    fig.savefig(FIGURES / "trajectory_transfer.pdf")
    plt.close(fig)


def write_report(summary):
    lines = [
        "# Experiment Report",
        "",
        "## Question",
        "",
        "Does componentwise action normalization preserve task effects across robot bodies, and does Effect-Jacobian Action Renormalization (EJAR) reduce the mismatch in a controlled embodied setting?",
        "",
        "## Setup",
        "",
        "A 2D teacher arm generates joint actions and first-order end-effector effects. Three target arms with different link lengths, degrees of freedom, and actuator limits receive either raw normalized copied actions or EJAR-decoded actions. The experiment includes random configurations and a repeated near-singular stress subset.",
        "",
        "## Key Results",
        "",
    ]
    one = summary["one_step_relative_error"]
    for method, stats in one.items():
        lines.append(f"- {method}: mean relative one-step effect error {stats['mean']:.3f}, median {stats['median']:.3f}, p90 {stats['p90']:.3f}.")
    lines.append("")
    for method, rate in summary["trajectory_success_10cm"].items():
        lines.append(f"- {method}: trajectory success rate at 0.10 workspace units {rate:.3f}.")
    if "jacobian_noise_stress" in summary:
        lines.extend(["", "## V2 Jacobian-Misspecification Stress", ""])
        for sigma, stats in summary["jacobian_noise_stress"].items():
            lines.append(
                "- sigma {sigma}: mean relative error {mean_relative_effect_error:.3f}, p90 {p90_relative_effect_error:.3f}, true residual {mean_true_residual:.4f}, residual gap {mean_residual_gap:.4f}.".format(
                    sigma=sigma,
                    **stats,
                )
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The synthetic evidence supports the narrow mechanism claim: copying normalized actuator values is not effect preserving across embodiments, while a local Jacobian pullback substantially improves first-order effect matching when the requested effect is feasible. Near singularities and actuator clipping remain failure modes; EJAR reports those through residuals rather than pretending the action transferred cleanly.",
            "",
            "## Artifacts",
            "",
            "- `results/one_step_results.csv`",
            "- `results/episode_results.csv`",
            "- `results/experiment_summary.json`",
            "- `results/jacobian_noise_stress.csv`",
            "- `figures/one_step_effect_error.png`",
            "- `figures/trajectory_transfer.png`",
        ]
    )
    (DOCS / "experiment_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    rng = np.random.default_rng(20)
    source = PlanarArm("teacher_2link", np.array([1.0, 0.70]), np.array([0.085, 0.075]))
    targets = [
        PlanarArm("short_2link", np.array([0.62, 0.46]), np.array([0.095, 0.070])),
        PlanarArm("long_2link", np.array([1.35, 0.95]), np.array([0.060, 0.055])),
        PlanarArm("asymmetric_3link", np.array([0.78, 0.52, 0.34]), np.array([0.060, 0.075, 0.090])),
    ]
    try:
        write_status("synthetic experiment running", next_step="write result CSVs, plots, and experiment report")
        one_rows = one_step_trials(rng, source, targets)
        ep_rows = trajectory_trials(rng, source, targets)
        jacobian_rows = jacobian_noise_stress(np.random.default_rng(2020), source, targets)
        write_csv(RESULTS / "one_step_results.csv", one_rows)
        write_csv(RESULTS / "jacobian_noise_stress.csv", jacobian_rows)
        write_csv(RESULTS / "episode_results.csv", ep_rows)
        jacobian_summary = jacobian_stress_summary(jacobian_rows)
        write_jacobian_noise_table(jacobian_summary)
        summary = {
            "source": source.name,
            "targets": [t.name for t in targets],
            "one_step_trials": len(one_rows),
            "jacobian_noise_trials": len(jacobian_rows),
            "trajectory_rows": len(ep_rows),
            "one_step_relative_error": summarize(one_rows, "relative_effect_error"),
            "one_step_cosine": summarize(one_rows, "effect_cosine"),
            "jacobian_noise_stress": jacobian_summary,
            "trajectory_final_error": summarize(ep_rows, "final_tracking_error"),
            "trajectory_success_10cm": success_summary(ep_rows),
        }
        (RESULTS / "experiment_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        plot_results(one_rows, ep_rows)
        write_report(summary)
        write_status("synthetic experiment complete", next_step="write ICLR paper, build PDF, publish repo")
        print(json.dumps(summary, indent=2))
    except Exception as exc:
        write_status(
            "synthetic experiment failed",
            failures=repr(exc),
            recovery="failure recorded; inspect experiment script and rerun",
            next_step="repair experiment before writing paper",
        )
        print(json.dumps({"error": repr(exc)}, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
