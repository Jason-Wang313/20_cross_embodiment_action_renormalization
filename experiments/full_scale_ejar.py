import csv
import json
import math
import platform
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "full_scale"
FIGURES = RESULTS
DOCS = ROOT / "docs"
SEED = 20020


def now_seconds():
    return time.perf_counter()


def ensure_dirs():
    RESULTS.mkdir(parents=True, exist_ok=True)


def safe_float(x, default=0.0):
    try:
        value = float(x)
        if math.isfinite(value):
            return value
    except Exception:
        pass
    return default


def mean(xs):
    xs = list(xs)
    return float(np.mean(xs)) if xs else 0.0


def median(xs):
    xs = list(xs)
    return float(np.median(xs)) if xs else 0.0


def pctl(xs, p):
    xs = list(xs)
    return float(np.percentile(xs, p)) if xs else 0.0


def sem95(xs):
    xs = np.asarray(list(xs), dtype=float)
    if len(xs) <= 1:
        return 0.0
    return float(1.96 * np.std(xs, ddof=1) / math.sqrt(len(xs)))


def rel_error(actual, desired):
    return float(np.linalg.norm(actual - desired) / (np.linalg.norm(desired) + 1e-9))


def cosine(actual, desired):
    denom = np.linalg.norm(actual) * np.linalg.norm(desired) + 1e-9
    return float(np.dot(actual, desired) / denom)


def clip_action(a, max_step):
    a = np.asarray(a, dtype=float)
    ratios = np.divide(max_step, np.maximum(np.abs(a), 1e-12))
    scale = min(1.0, float(np.min(ratios)))
    return a * scale, scale < 0.999


def pad_or_truncate(vec, n):
    out = np.zeros(n, dtype=float)
    m = min(len(vec), n)
    out[:m] = vec[:m]
    return out


def safe_solve(a, b):
    try:
        return np.linalg.solve(a, b)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(a) @ b


def psd_sqrt(mat, eps=1e-9, inverse=False):
    vals, vecs = np.linalg.eigh((mat + mat.T) * 0.5)
    vals = np.maximum(vals, eps)
    if inverse:
        vals = 1.0 / np.sqrt(vals)
    else:
        vals = np.sqrt(vals)
    return (vecs * vals) @ vecs.T


def condition_score(j, max_step=None):
    if max_step is not None:
        j = j @ np.diag(max_step)
    s = np.linalg.svd(j, compute_uv=False)
    if len(s) == 0:
        return 1e9
    return float(s[0] / max(s[-1], 1e-9))


@dataclass
class PlanarArm:
    name: str
    links: np.ndarray
    max_step: np.ndarray
    control_dt: float = 1.0

    @property
    def n(self):
        return int(len(self.links))

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
        center = rng.normal(0.0, 0.18, size=self.n)
        spread = rng.uniform(-math.pi * 0.78, math.pi * 0.78, size=self.n)
        return 0.35 * center + 0.65 * spread

    def features(self):
        return np.array(
            [
                self.n / 6.0,
                float(np.sum(self.links)),
                float(np.mean(self.links)),
                float(np.std(self.links)),
                float(np.mean(self.max_step)),
                float(np.std(self.max_step)),
                float(np.max(self.max_step)),
            ],
            dtype=float,
        )


def make_arm_zoo():
    arms = [
        PlanarArm("teacher_2link", np.array([1.00, 0.70]), np.array([0.085, 0.075])),
        PlanarArm("short_2link", np.array([0.62, 0.46]), np.array([0.095, 0.070])),
        PlanarArm("long_2link", np.array([1.35, 0.95]), np.array([0.060, 0.055])),
        PlanarArm("wide_2link", np.array([1.10, 0.35]), np.array([0.055, 0.110])),
        PlanarArm("asym_3link", np.array([0.78, 0.52, 0.34]), np.array([0.060, 0.075, 0.090])),
        PlanarArm("heavy_3link", np.array([1.25, 0.72, 0.30]), np.array([0.045, 0.060, 0.095])),
        PlanarArm("redundant_4link", np.array([0.55, 0.47, 0.40, 0.28]), np.array([0.070, 0.075, 0.065, 0.085])),
        PlanarArm("long_4link", np.array([0.90, 0.66, 0.42, 0.22]), np.array([0.050, 0.055, 0.075, 0.080])),
        PlanarArm("soft_5link", np.array([0.42, 0.38, 0.34, 0.25, 0.18]), np.array([0.080, 0.080, 0.070, 0.070, 0.060])),
        PlanarArm("needle_5link", np.array([0.80, 0.50, 0.28, 0.18, 0.11]), np.array([0.035, 0.050, 0.060, 0.085, 0.100])),
        PlanarArm("snake_6link", np.array([0.36, 0.32, 0.29, 0.24, 0.20, 0.15]), np.array([0.075, 0.070, 0.070, 0.060, 0.060, 0.055])),
        PlanarArm("large_6link", np.array([0.62, 0.50, 0.42, 0.32, 0.24, 0.16]), np.array([0.045, 0.050, 0.055, 0.065, 0.070, 0.080])),
    ]
    return arms


def raw_joint_copy(source, target, a_source):
    a = pad_or_truncate(a_source, target.n)
    a, clipped = clip_action(a, target.max_step)
    return a, {"clipped": clipped, "residual": float("nan")}


def normalized_copy(source, target, a_source):
    u = a_source / source.max_step
    u_t = pad_or_truncate(u, target.n)
    a = u_t * target.max_step
    a, clipped = clip_action(a, target.max_step)
    return a, {"clipped": clipped, "residual": float("nan")}


def link_scaled_copy(source, target, a_source):
    u = a_source / source.max_step
    source_reach = max(float(np.sum(source.links)), 1e-9)
    target_reach = max(float(np.sum(target.links)), 1e-9)
    scale = source_reach / target_reach
    u_t = pad_or_truncate(u, target.n) * scale
    a = u_t * target.max_step
    a, clipped = clip_action(a, target.max_step)
    return a, {"clipped": clipped, "residual": float("nan")}


def decode_with_j(target, j_decode, desired_effect, damping=1e-5, weighted=True):
    if weighted:
        b2 = np.diag(target.max_step ** 2)
        sigma = j_decode @ b2 @ j_decode.T
        solve = safe_solve(sigma + damping * np.eye(j_decode.shape[0]), desired_effect)
        a = b2 @ j_decode.T @ solve
    else:
        sigma = j_decode @ j_decode.T
        solve = safe_solve(sigma + damping * np.eye(j_decode.shape[0]), desired_effect)
        a = j_decode.T @ solve
    a, clipped = clip_action(a, target.max_step)
    reported_effect = j_decode @ a
    return a, {
        "clipped": clipped,
        "reported_effect": reported_effect,
        "residual": float(np.linalg.norm(reported_effect - desired_effect)),
    }


def ejar_absolute(target, q_target, desired_effect, damping=1e-5):
    return decode_with_j(target, target.jacobian(q_target), desired_effect, damping=damping, weighted=True)


def target_ik(target, q_target, desired_effect, damping=1e-5):
    return decode_with_j(target, target.jacobian(q_target), desired_effect, damping=damping, weighted=False)


def static_home_decoder(target, desired_effect, damping=1e-5):
    q_home = np.zeros(target.n, dtype=float)
    return decode_with_j(target, target.jacobian(q_home), desired_effect, damping=damping, weighted=True)


def ejar_capability_token(source, q_source, target, q_target, a_source, damping=1e-5):
    j_s = source.jacobian(q_source)
    j_t = target.jacobian(q_target)
    sigma_s = j_s @ np.diag(source.max_step ** 2) @ j_s.T
    sigma_t = j_t @ np.diag(target.max_step ** 2) @ j_t.T
    d_s = j_s @ a_source
    z = psd_sqrt(sigma_s + damping * np.eye(2), inverse=True) @ d_s
    desired_target = psd_sqrt(sigma_t + damping * np.eye(2), inverse=False) @ z
    a, info = ejar_absolute(target, q_target, desired_target, damping=damping)
    actual = j_t @ a
    z_actual = psd_sqrt(sigma_t + damping * np.eye(2), inverse=True) @ actual
    info["token_error"] = rel_error(z_actual, z)
    info["desired_target_effect"] = desired_target
    return a, info


def summarize_groups(records, group_key, metrics, extra_keys=None):
    extra_keys = extra_keys or []
    groups = sorted(set(r[group_key] for r in records))
    rows = []
    for group in groups:
        sub = [r for r in records if r[group_key] == group]
        row = {group_key: group, "n": len(sub)}
        for metric in metrics:
            vals = [safe_float(r.get(metric)) for r in sub if str(r.get(metric, "")) != ""]
            row[f"{metric}_mean"] = mean(vals)
            row[f"{metric}_median"] = median(vals)
            row[f"{metric}_p90"] = pctl(vals, 90)
            row[f"{metric}_ci95"] = sem95(vals)
        for key in extra_keys:
            vals = [safe_float(r.get(key)) for r in sub if str(r.get(key, "")) != ""]
            row[f"{key}_mean"] = mean(vals)
        rows.append(row)
    return rows


def write_csv(path, rows, fieldnames=None):
    rows = list(rows)
    if not rows:
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def latex_escape(text):
    return str(text).replace("_", r"\_").replace("%", r"\%")


def fmt(x, digits=3):
    if isinstance(x, str):
        return latex_escape(x)
    try:
        return f"{float(x):.{digits}f}"
    except Exception:
        return latex_escape(x)


def write_table(path, caption, label, columns, rows, digits=3):
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        r"\begin{tabular}{" + "l" + "c" * (len(columns) - 1) + "}",
        r"\toprule",
        " & ".join(latex_escape(c[1]) for c in columns) + r" \\",
        r"\midrule",
    ]
    for row in rows:
        cells = []
        for key, _ in columns:
            value = row.get(key, "")
            cells.append(fmt(value, digits=digits))
        lines.append(" & ".join(cells) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def record_progress(stage, family_status, total_rows, total_episodes, plot_failures=0):
    progress = {
        "stage": stage,
        "family_status": family_status,
        "total_rows": total_rows,
        "total_episodes": total_episodes,
        "plot_failures": plot_failures,
        "updated_unix": time.time(),
    }
    (RESULTS / "progress.json").write_text(json.dumps(progress, indent=2), encoding="utf-8")


def family_a_main_sweep(rng, arms):
    t0 = now_seconds()
    rows = []
    sources = arms[:6]
    targets = arms[1:]
    methods = ["raw_joint", "normalized_copy", "link_scaled", "static_home", "target_ik", "ejar_absolute", "ejar_capability"]
    n_trials = 3000
    for trial in range(n_trials):
        source = sources[trial % len(sources)]
        target = targets[(trial * 5 + 3) % len(targets)]
        singular = trial % 11 == 0
        q_s = source.random_q(rng, singular=False)
        q_t = target.random_q(rng, singular=singular)
        a_s = rng.uniform(-0.85, 0.85, size=source.n) * source.max_step
        d_s = source.jacobian(q_s) @ a_s
        cond = condition_score(target.jacobian(q_t), target.max_step)
        for method in methods:
            desired = d_s
            if method == "raw_joint":
                a_t, info = raw_joint_copy(source, target, a_s)
            elif method == "normalized_copy":
                a_t, info = normalized_copy(source, target, a_s)
            elif method == "link_scaled":
                a_t, info = link_scaled_copy(source, target, a_s)
            elif method == "static_home":
                a_t, info = static_home_decoder(target, d_s)
            elif method == "target_ik":
                a_t, info = target_ik(target, q_t, d_s)
            elif method == "ejar_absolute":
                a_t, info = ejar_absolute(target, q_t, d_s)
            elif method == "ejar_capability":
                a_t, info = ejar_capability_token(source, q_s, target, q_t, a_s)
                desired = info["desired_target_effect"]
            actual = target.jacobian(q_t) @ a_t
            rows.append(
                {
                    "trial": trial,
                    "source": source.name,
                    "target": target.name,
                    "method": method,
                    "mode": "token" if method == "ejar_capability" else "absolute",
                    "singular": int(singular),
                    "source_dof": source.n,
                    "target_dof": target.n,
                    "condition": cond,
                    "relative_effect_error": rel_error(actual, desired),
                    "effect_cosine": cosine(actual, desired),
                    "absolute_error": float(np.linalg.norm(actual - desired)),
                    "desired_norm": float(np.linalg.norm(desired)),
                    "clipped": int(bool(info.get("clipped", False))),
                    "residual": safe_float(info.get("residual", 0.0)),
                    "token_error": safe_float(info.get("token_error", "")),
                }
            )
    write_csv(RESULTS / "family_a_main_seed.csv", rows)
    summary = summarize_groups(
        rows,
        "method",
        ["relative_effect_error", "effect_cosine", "absolute_error", "residual"],
        extra_keys=["clipped", "condition"],
    )
    write_csv(RESULTS / "family_a_main_summary.csv", summary)
    table_rows = sorted(summary, key=lambda r: r["relative_effect_error_mean"])
    write_table(
        RESULTS / "table_main_sweep.tex",
        "Family A main morphology sweep. Lower effect error is better. Capability-token rows are evaluated against locally normalized target effects, while the other rows use absolute source effects.",
        "tab:main-sweep",
        [
            ("method", "Method"),
            ("relative_effect_error_mean", "Mean rel. err."),
            ("relative_effect_error_p90", "p90 rel. err."),
            ("effect_cosine_mean", "Cosine"),
            ("clipped_mean", "Clip rate"),
        ],
        table_rows,
    )
    return {"family": "A", "rows": len(rows), "episodes": 0, "seconds": now_seconds() - t0}


def transfer_action_for_method(method, source, target, q_s, q_t, a_s, desired):
    if method == "raw_joint":
        return raw_joint_copy(source, target, a_s)
    if method == "normalized_copy":
        return normalized_copy(source, target, a_s)
    if method == "link_scaled":
        return link_scaled_copy(source, target, a_s)
    if method == "static_home":
        return static_home_decoder(target, desired)
    if method == "target_ik":
        return target_ik(target, q_t, desired)
    if method == "ejar_absolute":
        return ejar_absolute(target, q_t, desired)
    if method == "ejar_residual_fallback":
        a, info = ejar_absolute(target, q_t, desired)
        if safe_float(info.get("residual")) > 0.035:
            a, info = ejar_absolute(target, q_t, 0.65 * desired)
            info["fallback_used"] = True
        else:
            info["fallback_used"] = False
        return a, info
    raise ValueError(method)


def family_b_trajectory(rng, arms):
    t0 = now_seconds()
    rows = []
    methods = ["raw_joint", "normalized_copy", "link_scaled", "static_home", "target_ik", "ejar_absolute", "ejar_residual_fallback"]
    horizons = [8, 16, 32, 64]
    episodes_per_horizon = 180
    for h in horizons:
        for ep in range(episodes_per_horizon):
            source = arms[(ep + h) % 6]
            target = arms[(ep * 7 + h) % (len(arms) - 1) + 1]
            singular = ep % 17 == 0
            q_s0 = source.random_q(rng, singular=False)
            q_t0 = target.random_q(rng, singular=singular)
            goal = source.fk(q_s0) + rng.normal(0.0, 0.22, size=2)
            q_s = q_s0.copy()
            source_actions = []
            desired_effects = []
            for step in range(h):
                delta = goal - source.fk(q_s)
                desired = delta / max(1.0, h - step)
                desired_norm = np.linalg.norm(desired)
                if desired_norm > 0.075:
                    desired = desired / desired_norm * 0.075
                a_s, _ = ejar_absolute(source, q_s, desired)
                d_s = source.jacobian(q_s) @ a_s
                source_actions.append(a_s)
                desired_effects.append(d_s)
                q_s = q_s + a_s
            for method in methods:
                q_t = q_t0.copy()
                p_des = target.fk(q_t0).copy()
                errors = []
                clipped_steps = 0
                residual_sum = 0.0
                fallback_steps = 0
                for a_s, d_s in zip(source_actions, desired_effects):
                    p_des = p_des + d_s
                    a_t, info = transfer_action_for_method(method, source, target, q_s0, q_t, a_s, d_s)
                    clipped_steps += int(bool(info.get("clipped", False)))
                    fallback_steps += int(bool(info.get("fallback_used", False)))
                    residual_sum += safe_float(info.get("residual", 0.0))
                    q_t = q_t + a_t
                    errors.append(float(np.linalg.norm(target.fk(q_t) - p_des)))
                final_error = errors[-1]
                rows.append(
                    {
                        "episode": f"{h}_{ep}",
                        "horizon": h,
                        "source": source.name,
                        "target": target.name,
                        "method": method,
                        "singular": int(singular),
                        "final_tracking_error": final_error,
                        "mean_tracking_error": mean(errors),
                        "success_005": int(final_error < 0.05),
                        "success_010": int(final_error < 0.10),
                        "success_020": int(final_error < 0.20),
                        "clipped_steps": clipped_steps,
                        "residual_sum": residual_sum,
                        "fallback_steps": fallback_steps,
                    }
                )
    write_csv(RESULTS / "family_b_trajectory_seed.csv", rows)
    summary = []
    for method in sorted(set(r["method"] for r in rows)):
        sub = [r for r in rows if r["method"] == method]
        summary.append(
            {
                "method": method,
                "n": len(sub),
                "final_error_mean": mean(safe_float(r["final_tracking_error"]) for r in sub),
                "final_error_median": median(safe_float(r["final_tracking_error"]) for r in sub),
                "final_error_p90": pctl((safe_float(r["final_tracking_error"]) for r in sub), 90),
                "success_010_mean": mean(safe_float(r["success_010"]) for r in sub),
                "success_020_mean": mean(safe_float(r["success_020"]) for r in sub),
                "clipped_steps_mean": mean(safe_float(r["clipped_steps"]) for r in sub),
                "residual_sum_mean": mean(safe_float(r["residual_sum"]) for r in sub),
            }
        )
    write_csv(RESULTS / "family_b_trajectory_summary.csv", summary)
    write_table(
        RESULTS / "table_trajectory.tex",
        "Family B long-horizon transfer. Success is final target path error below 0.10 workspace units.",
        "tab:trajectory-v3",
        [
            ("method", "Method"),
            ("final_error_median", "Median final err."),
            ("final_error_p90", "p90 final err."),
            ("success_010_mean", "Success 0.10"),
            ("clipped_steps_mean", "Clip steps"),
        ],
        sorted(summary, key=lambda r: -r["success_010_mean"]),
    )
    return {"family": "B", "rows": len(rows), "episodes": len(rows), "seconds": now_seconds() - t0}


def max_dof():
    return 6


def q_features(q, n=max_dof()):
    q_pad = pad_or_truncate(q, n)
    return np.concatenate([np.sin(q_pad), np.cos(q_pad)])


def make_policy_feature(arm, q, desired_effect, include_morph=False, include_id=False, id_index=-1, id_count=0):
    base = [desired_effect[0], desired_effect[1], np.linalg.norm(desired_effect), condition_score(arm.jacobian(q), arm.max_step)]
    feat = np.concatenate([np.array(base, dtype=float), q_features(q)])
    if include_morph:
        feat = np.concatenate([feat, arm.features()])
    if include_id:
        one = np.zeros(id_count, dtype=float)
        if 0 <= id_index < id_count:
            one[id_index] = 1.0
        feat = np.concatenate([feat, one])
    return feat


def ridge_fit(x, y, alpha=1e-3):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xb = np.concatenate([x, np.ones((x.shape[0], 1))], axis=1)
    eye = np.eye(xb.shape[1])
    eye[-1, -1] = 0.0
    return safe_solve(xb.T @ xb + alpha * eye, xb.T @ y)


def ridge_predict(w, x):
    xb = np.concatenate([np.asarray(x, dtype=float), np.ones((len(x), 1))], axis=1)
    return xb @ w


def make_learning_sample(rng, arm):
    q = arm.random_q(rng, singular=(rng.random() < 0.08))
    goal = arm.fk(q) + rng.normal(0.0, 0.18, size=2)
    desired = goal - arm.fk(q)
    norm = np.linalg.norm(desired)
    if norm > 0.08:
        desired = desired / norm * 0.08
    a, _ = ejar_absolute(arm, q, desired)
    raw_label = pad_or_truncate(a / arm.max_step, max_dof())
    j = arm.jacobian(q)
    sigma = j @ np.diag(arm.max_step ** 2) @ j.T
    token = psd_sqrt(sigma + 1e-5 * np.eye(2), inverse=True) @ desired
    return q, desired, raw_label, desired, token


def family_c_learning(rng, arms):
    t0 = now_seconds()
    train_arms = arms[:7]
    test_arms = arms[7:]
    budgets = [100, 500, 2000, 8000]
    methods = [
        ("pooled_raw", "raw", False, False),
        ("morph_raw", "raw", True, False),
        ("robot_id_raw", "raw", False, True),
        ("effect_label_ejar", "effect", False, False),
        ("capability_token_ejar", "token", False, False),
    ]
    rows = []
    for budget in budgets:
        train_bank = []
        for i in range(budget):
            arm_index = i % len(train_arms)
            arm = train_arms[arm_index]
            q, desired, raw_label, effect_label, token = make_learning_sample(rng, arm)
            train_bank.append((arm_index, arm, q, desired, raw_label, effect_label, token))
        models = {}
        for method, label_kind, include_morph, include_id in methods:
            x = []
            y = []
            for arm_index, arm, q, desired, raw_label, effect_label, token in train_bank:
                x.append(make_policy_feature(arm, q, desired, include_morph, include_id, arm_index, len(train_arms)))
                if label_kind == "raw":
                    y.append(raw_label)
                elif label_kind == "effect":
                    y.append(effect_label)
                else:
                    y.append(token)
            models[method] = (ridge_fit(x, y), label_kind, include_morph, include_id)
        eval_cases = 720
        for case in range(eval_cases):
            arm = test_arms[case % len(test_arms)]
            q, desired, _, _, _ = make_learning_sample(rng, arm)
            for method, (w, label_kind, include_morph, include_id) in models.items():
                x = [make_policy_feature(arm, q, desired, include_morph, include_id, -1, len(train_arms))]
                pred = ridge_predict(w, x)[0]
                if label_kind == "raw":
                    u = pad_or_truncate(pred, arm.n)
                    a = u * arm.max_step
                    a, clipped = clip_action(a, arm.max_step)
                    info = {"clipped": clipped, "residual": 0.0}
                elif label_kind == "effect":
                    a, info = ejar_absolute(arm, q, pred)
                else:
                    j = arm.jacobian(q)
                    sigma = j @ np.diag(arm.max_step ** 2) @ j.T
                    desired_target = psd_sqrt(sigma + 1e-5 * np.eye(2), inverse=False) @ pred
                    a, info = ejar_absolute(arm, q, desired_target)
                actual = arm.jacobian(q) @ a
                rows.append(
                    {
                        "budget": budget,
                        "case": case,
                        "target": arm.name,
                        "method": method,
                        "relative_goal_effect_error": rel_error(actual, desired),
                        "progress_cosine": cosine(actual, desired),
                        "success_005": int(np.linalg.norm(actual - desired) < 0.05),
                        "success_010": int(np.linalg.norm(actual - desired) < 0.10),
                        "actual_norm": float(np.linalg.norm(actual)),
                        "desired_norm": float(np.linalg.norm(desired)),
                        "clipped": int(bool(info.get("clipped", False))),
                    }
                )
    write_csv(RESULTS / "family_c_learning_seed.csv", rows)
    summary = []
    for budget in budgets:
        for method in sorted(set(r["method"] for r in rows)):
            sub = [r for r in rows if r["budget"] == budget and r["method"] == method]
            summary.append(
                {
                    "budget": budget,
                    "method": method,
                    "n": len(sub),
                    "relative_goal_effect_error_mean": mean(safe_float(r["relative_goal_effect_error"]) for r in sub),
                    "relative_goal_effect_error_p90": pctl((safe_float(r["relative_goal_effect_error"]) for r in sub), 90),
                    "progress_cosine_mean": mean(safe_float(r["progress_cosine"]) for r in sub),
                    "success_005_mean": mean(safe_float(r["success_005"]) for r in sub),
                    "success_010_mean": mean(safe_float(r["success_010"]) for r in sub),
                    "clipped_mean": mean(safe_float(r["clipped"]) for r in sub),
                }
            )
    write_csv(RESULTS / "family_c_learning_summary.csv", summary)
    final_budget = [r for r in summary if r["budget"] == max(budgets)]
    write_table(
        RESULTS / "table_learning.tex",
        "Family C learned action-interface stress at the largest training budget. Effect-label and token-label models are decoded through the target local map.",
        "tab:learning",
        [
            ("method", "Method"),
            ("relative_goal_effect_error_mean", "Mean rel. err."),
            ("relative_goal_effect_error_p90", "p90 rel. err."),
            ("success_010_mean", "Success 0.10"),
            ("progress_cosine_mean", "Progress cosine"),
        ],
        sorted(final_budget, key=lambda r: -r["success_010_mean"]),
    )
    return {"family": "C", "rows": len(rows), "episodes": len(rows), "seconds": now_seconds() - t0}


def noisy_jacobian(rng, j_true, variant, arm=None, q=None):
    scale = max(1e-9, float(np.sqrt(np.mean(j_true ** 2))))
    if variant == "exact":
        return j_true
    if variant == "gaussian_002":
        return j_true + rng.normal(0.0, 0.02 * scale, size=j_true.shape)
    if variant == "gaussian_010":
        return j_true + rng.normal(0.0, 0.10 * scale, size=j_true.shape)
    if variant == "gaussian_020":
        return j_true + rng.normal(0.0, 0.20 * scale, size=j_true.shape)
    if variant == "scale_bias_110":
        bias = np.diag([1.10, 0.88])
        return bias @ j_true
    if variant == "column_dropout":
        j = j_true.copy()
        col = int(rng.integers(0, j.shape[1]))
        j[:, col] *= 0.15
        return j
    if variant == "finite_diff_noisy":
        eps = 1e-4
        cols = []
        for k in range(arm.n):
            dq = np.zeros(arm.n)
            dq[k] = eps
            col = (arm.fk(q + dq) - arm.fk(q - dq)) / (2.0 * eps)
            cols.append(col)
        return np.stack(cols, axis=1) + rng.normal(0.0, 0.04 * scale, size=j_true.shape)
    if variant == "stale_q":
        q_old = q + rng.normal(0.0, 0.18, size=arm.n)
        return arm.jacobian(q_old)
    raise ValueError(variant)


def family_d_model_error(rng, arms):
    t0 = now_seconds()
    variants = ["exact", "gaussian_002", "gaussian_010", "gaussian_020", "scale_bias_110", "column_dropout", "finite_diff_noisy", "stale_q"]
    rows = []
    n_trials = 1400
    for trial in range(n_trials):
        source = arms[trial % 6]
        target = arms[(trial * 5 + 2) % (len(arms) - 1) + 1]
        q_s = source.random_q(rng, singular=False)
        q_t = target.random_q(rng, singular=(trial % 13 == 0))
        a_s = rng.uniform(-0.85, 0.85, size=source.n) * source.max_step
        desired = source.jacobian(q_s) @ a_s
        j_true = target.jacobian(q_t)
        for variant in variants:
            j_est = noisy_jacobian(rng, j_true, variant, arm=target, q=q_t)
            a_t, info = decode_with_j(target, j_est, desired, weighted=True)
            actual = j_true @ a_t
            reported = j_est @ a_t
            rows.append(
                {
                    "trial": trial,
                    "variant": variant,
                    "source": source.name,
                    "target": target.name,
                    "relative_effect_error": rel_error(actual, desired),
                    "effect_cosine": cosine(actual, desired),
                    "reported_residual": float(np.linalg.norm(reported - desired)),
                    "true_residual": float(np.linalg.norm(actual - desired)),
                    "residual_gap": float(np.linalg.norm(actual - reported)),
                    "clipped": int(bool(info.get("clipped", False))),
                }
            )
    write_csv(RESULTS / "family_d_model_error_seed.csv", rows)
    summary = summarize_groups(rows, "variant", ["relative_effect_error", "reported_residual", "true_residual", "residual_gap"], extra_keys=["clipped"])
    write_csv(RESULTS / "family_d_model_error_summary.csv", summary)
    write_table(
        RESULTS / "table_model_error.tex",
        "Family D target-model error. EJAR decodes with the listed estimated Jacobian but is evaluated under the true target Jacobian.",
        "tab:model-error",
        [
            ("variant", "Decoder map"),
            ("relative_effect_error_mean", "Mean rel. err."),
            ("relative_effect_error_p90", "p90 rel. err."),
            ("true_residual_mean", "True residual"),
            ("residual_gap_mean", "Residual gap"),
        ],
        sorted(summary, key=lambda r: r["relative_effect_error_mean"]),
    )
    return {"family": "D", "rows": len(rows), "episodes": 0, "seconds": now_seconds() - t0}


def auroc(labels, scores):
    pairs = sorted(zip(scores, labels), key=lambda x: x[0])
    pos = sum(labels)
    neg = len(labels) - pos
    if pos == 0 or neg == 0:
        return 0.5
    rank_sum = 0.0
    for rank, (_, label) in enumerate(pairs, start=1):
        if label:
            rank_sum += rank
    return float((rank_sum - pos * (pos + 1) / 2.0) / (pos * neg))


def auprc(labels, scores):
    order = np.argsort(-np.asarray(scores, dtype=float))
    labels_arr = np.asarray(labels, dtype=float)[order]
    pos = float(np.sum(labels_arr))
    if pos <= 0:
        return 0.0
    tp = 0.0
    fp = 0.0
    last_recall = 0.0
    area = 0.0
    for lab in labels_arr:
        if lab > 0.5:
            tp += 1.0
        else:
            fp += 1.0
        recall = tp / pos
        precision = tp / max(tp + fp, 1e-9)
        area += precision * max(0.0, recall - last_recall)
        last_recall = recall
    return float(area)


def family_e_residual_calibration(rng, arms):
    t0 = now_seconds()
    rows = []
    n_trials = 7200
    scales = [0.35, 0.70, 1.00, 1.35, 1.75, 2.25]
    for trial in range(n_trials):
        target = arms[(trial * 7 + 4) % len(arms)]
        q_t = target.random_q(rng, singular=(trial % 9 == 0))
        j = target.jacobian(q_t)
        sigma = j @ np.diag(target.max_step ** 2) @ j.T
        direction = rng.normal(0.0, 1.0, size=2)
        direction = direction / (np.linalg.norm(direction) + 1e-9)
        scale = scales[trial % len(scales)]
        desired = psd_sqrt(sigma + 1e-5 * np.eye(2)) @ direction * scale
        a, info = ejar_absolute(target, q_t, desired)
        actual = j @ a
        true_residual = float(np.linalg.norm(actual - desired))
        infeasible = int((true_residual / (np.linalg.norm(desired) + 1e-9)) > 0.15 or bool(info.get("clipped", False)))
        a_static, info_static = static_home_decoder(target, desired)
        actual_static = j @ a_static
        action_norm_score = float(np.linalg.norm(a) / (np.linalg.norm(target.max_step) + 1e-9))
        cond_score = condition_score(j, target.max_step)
        rows.append(
            {
                "trial": trial,
                "target": target.name,
                "scale": scale,
                "infeasible": infeasible,
                "true_relative_residual": true_residual / (np.linalg.norm(desired) + 1e-9),
                "ejar_residual_score": safe_float(info.get("residual", 0.0)),
                "static_residual_score": float(np.linalg.norm(actual_static - desired)),
                "action_norm_score": action_norm_score,
                "condition_score": cond_score,
                "clipped": int(bool(info.get("clipped", False))),
            }
        )
    write_csv(RESULTS / "family_e_residual_seed.csv", rows)
    labels = [int(r["infeasible"]) for r in rows]
    score_keys = ["ejar_residual_score", "static_residual_score", "action_norm_score", "condition_score"]
    summary = []
    for key in score_keys:
        scores = [safe_float(r[key]) for r in rows]
        low_cut = np.percentile(scores, 25)
        infeasible_count = max(1, sum(labels))
        false_reassure = sum(1 for r, s in zip(rows, scores) if s <= low_cut and int(r["infeasible"]) == 1) / infeasible_count
        summary.append(
            {
                "score": key,
                "n": len(rows),
                "auroc": auroc(labels, scores),
                "auprc": auprc(labels, scores),
                "false_reassurance_rate": false_reassure,
                "mean_score": mean(scores),
            }
        )
    write_csv(RESULTS / "family_e_residual_summary.csv", summary)
    write_table(
        RESULTS / "table_residual_calibration.tex",
        "Family E infeasible-effect detection. Higher AUROC/AUPRC is better; false reassurance is the fraction of infeasible requests in the lowest-score quartile.",
        "tab:residual-calibration",
        [
            ("score", "Score"),
            ("auroc", "AUROC"),
            ("auprc", "AUPRC"),
            ("false_reassurance_rate", "False reassurance"),
            ("mean_score", "Mean score"),
        ],
        sorted(summary, key=lambda r: -r["auprc"]),
    )
    return {"family": "E", "rows": len(rows), "episodes": 0, "seconds": now_seconds() - t0}


def task_transform(name):
    if name == "identity":
        return np.eye(2)
    if name == "rotate_30":
        c = math.cos(math.radians(30.0))
        s = math.sin(math.radians(30.0))
        return np.array([[c, -s], [s, c]], dtype=float)
    if name == "scale_x2":
        return np.array([[2.0, 0.0], [0.0, 0.7]], dtype=float)
    if name == "swap_axes":
        return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=float)
    if name == "drop_y":
        return np.array([[1.0, 0.0], [0.0, 0.05]], dtype=float)
    raise ValueError(name)


def family_f_task_mismatch(rng, arms):
    t0 = now_seconds()
    transforms = ["identity", "rotate_30", "scale_x2", "swap_axes", "drop_y"]
    methods = ["raw_joint", "ejar_correct_map", "ejar_assumed_map"]
    rows = []
    n_trials = 4200
    for trial in range(n_trials):
        source = arms[trial % 6]
        target = arms[(trial * 7 + 1) % (len(arms) - 1) + 1]
        q_s = source.random_q(rng)
        q_t = target.random_q(rng, singular=(trial % 15 == 0))
        a_s = rng.uniform(-0.8, 0.8, size=source.n) * source.max_step
        d_true = source.jacobian(q_s) @ a_s
        mismatch = transforms[trial % len(transforms)]
        tmat = task_transform(mismatch)
        d_assumed = tmat @ d_true
        for method in methods:
            if method == "raw_joint":
                a_t, info = raw_joint_copy(source, target, a_s)
                desired_for_decode = d_true
            elif method == "ejar_correct_map":
                a_t, info = ejar_absolute(target, q_t, d_true)
                desired_for_decode = d_true
            else:
                a_t, info = ejar_absolute(target, q_t, d_assumed)
                desired_for_decode = d_assumed
            actual_true = target.jacobian(q_t) @ a_t
            rows.append(
                {
                    "trial": trial,
                    "mismatch": mismatch,
                    "method": method,
                    "target": target.name,
                    "assumed_relative_error": rel_error(actual_true, desired_for_decode),
                    "true_relative_error": rel_error(actual_true, d_true),
                    "residual_gap": float(abs(np.linalg.norm(actual_true - desired_for_decode) - np.linalg.norm(actual_true - d_true))),
                    "clipped": int(bool(info.get("clipped", False))),
                }
            )
    write_csv(RESULTS / "family_f_task_mismatch_seed.csv", rows)
    summary = []
    for mismatch in transforms:
        for method in methods:
            sub = [r for r in rows if r["mismatch"] == mismatch and r["method"] == method]
            summary.append(
                {
                    "mismatch": mismatch,
                    "method": method,
                    "n": len(sub),
                    "assumed_relative_error_mean": mean(safe_float(r["assumed_relative_error"]) for r in sub),
                    "true_relative_error_mean": mean(safe_float(r["true_relative_error"]) for r in sub),
                    "true_relative_error_p90": pctl((safe_float(r["true_relative_error"]) for r in sub), 90),
                    "residual_gap_mean": mean(safe_float(r["residual_gap"]) for r in sub),
                }
            )
    write_csv(RESULTS / "family_f_task_mismatch_summary.csv", summary)
    table_rows = [r for r in summary if r["method"] == "ejar_assumed_map"]
    write_table(
        RESULTS / "table_task_mismatch.tex",
        "Family F semantic task-map mismatch for EJAR with the assumed target map. Identity is the valid-map control.",
        "tab:task-mismatch",
        [
            ("mismatch", "Assumed map"),
            ("assumed_relative_error_mean", "Assumed-map err."),
            ("true_relative_error_mean", "True-map err."),
            ("true_relative_error_p90", "p90 true err."),
            ("residual_gap_mean", "Residual gap"),
        ],
        table_rows,
    )
    return {"family": "F", "rows": len(rows), "episodes": 0, "seconds": now_seconds() - t0}


def family_g_control_rate(rng, arms):
    t0 = now_seconds()
    methods = ["raw_joint", "normalized_copy", "ejar_correct_rate", "ejar_wrong_rate", "ejar_latency"]
    dt_pairs = [(1.0, 1.0), (1.0, 0.5), (1.0, 2.0), (0.5, 1.5), (2.0, 0.75)]
    rows = []
    n_trials = 4200
    for trial in range(n_trials):
        source = arms[trial % 5]
        target = arms[(trial * 5 + 6) % (len(arms) - 1) + 1]
        dt_s, dt_t = dt_pairs[trial % len(dt_pairs)]
        q_s = source.random_q(rng)
        q_t = target.random_q(rng, singular=(trial % 16 == 0))
        a_s = rng.uniform(-0.8, 0.8, size=source.n) * source.max_step
        desired = (source.jacobian(q_s) * dt_s) @ a_s
        j_true_rate = target.jacobian(q_t) * dt_t
        for method in methods:
            if method == "raw_joint":
                a_t, info = raw_joint_copy(source, target, a_s)
            elif method == "normalized_copy":
                a_t, info = normalized_copy(source, target, a_s)
            elif method == "ejar_correct_rate":
                a_t, info = decode_with_j(target, j_true_rate, desired, weighted=True)
            elif method == "ejar_wrong_rate":
                a_t, info = decode_with_j(target, target.jacobian(q_t) * dt_s, desired, weighted=True)
            else:
                q_lag = q_t + rng.normal(0.0, 0.12, size=target.n)
                a_t, info = decode_with_j(target, target.jacobian(q_lag) * dt_t, desired, weighted=True)
            actual = j_true_rate @ a_t
            rows.append(
                {
                    "trial": trial,
                    "method": method,
                    "dt_source": dt_s,
                    "dt_target": dt_t,
                    "target": target.name,
                    "relative_effect_error": rel_error(actual, desired),
                    "effect_cosine": cosine(actual, desired),
                    "residual": safe_float(info.get("residual", 0.0)),
                    "clipped": int(bool(info.get("clipped", False))),
                }
            )
    write_csv(RESULTS / "family_g_control_rate_seed.csv", rows)
    summary = summarize_groups(rows, "method", ["relative_effect_error", "effect_cosine", "residual"], extra_keys=["clipped"])
    write_csv(RESULTS / "family_g_control_rate_summary.csv", summary)
    write_table(
        RESULTS / "table_control_rate.tex",
        "Family G control-rate and latency mismatch. Correct-rate EJAR uses the target action-effect map for the target control period.",
        "tab:control-rate",
        [
            ("method", "Method"),
            ("relative_effect_error_mean", "Mean rel. err."),
            ("relative_effect_error_p90", "p90 rel. err."),
            ("effect_cosine_mean", "Cosine"),
            ("residual_mean", "Residual"),
        ],
        sorted(summary, key=lambda r: r["relative_effect_error_mean"]),
    )
    return {"family": "G", "rows": len(rows), "episodes": 0, "seconds": now_seconds() - t0}


def contact_matrix(mode):
    if mode == "stick":
        return np.array([[1.0, 0.0], [0.0, 0.65]], dtype=float)
    if mode == "slide_x":
        return np.array([[0.85, 0.0], [0.0, 0.12]], dtype=float)
    if mode == "slide_y":
        return np.array([[0.12, 0.0], [0.0, 0.85]], dtype=float)
    if mode == "rotate":
        c = math.cos(math.radians(35.0))
        s = math.sin(math.radians(35.0))
        r = np.array([[c, -s], [s, c]], dtype=float)
        return r @ np.array([[0.75, 0.0], [0.0, 0.30]], dtype=float)
    raise ValueError(mode)


def family_h_contact_proxy(rng, arms):
    t0 = now_seconds()
    modes = ["stick", "slide_x", "slide_y", "rotate"]
    methods = ["raw_joint", "endpoint_ejar", "contact_ejar_known", "contact_ejar_wrong"]
    rows = []
    n_trials = 3600
    for trial in range(n_trials):
        source = arms[trial % 6]
        target = arms[(trial * 3 + 5) % (len(arms) - 1) + 1]
        mode_true = modes[trial % len(modes)]
        mode_wrong = modes[(trial + 1) % len(modes)]
        c_s = contact_matrix(mode_true)
        c_t = contact_matrix(mode_true)
        c_wrong = contact_matrix(mode_wrong)
        q_s = source.random_q(rng)
        q_t = target.random_q(rng, singular=(trial % 18 == 0))
        a_s = rng.uniform(-0.8, 0.8, size=source.n) * source.max_step
        desired_obj = c_s @ source.jacobian(q_s) @ a_s
        endpoint_desired = source.jacobian(q_s) @ a_s
        j_endpoint = target.jacobian(q_t)
        j_contact_true = c_t @ j_endpoint
        j_contact_wrong = c_wrong @ j_endpoint
        for method in methods:
            if method == "raw_joint":
                a_t, info = raw_joint_copy(source, target, a_s)
            elif method == "endpoint_ejar":
                a_t, info = decode_with_j(target, j_endpoint, endpoint_desired, weighted=True)
            elif method == "contact_ejar_known":
                a_t, info = decode_with_j(target, j_contact_true, desired_obj, weighted=True)
            else:
                a_t, info = decode_with_j(target, j_contact_wrong, desired_obj, weighted=True)
            actual_obj = j_contact_true @ a_t
            rows.append(
                {
                    "trial": trial,
                    "mode_true": mode_true,
                    "method": method,
                    "object_relative_error": rel_error(actual_obj, desired_obj),
                    "object_cosine": cosine(actual_obj, desired_obj),
                    "object_abs_error": float(np.linalg.norm(actual_obj - desired_obj)),
                    "success_005": int(np.linalg.norm(actual_obj - desired_obj) < 0.05),
                    "clipped": int(bool(info.get("clipped", False))),
                    "residual": safe_float(info.get("residual", 0.0)),
                }
            )
    write_csv(RESULTS / "family_h_contact_proxy_seed.csv", rows)
    summary = summarize_groups(rows, "method", ["object_relative_error", "object_cosine", "object_abs_error", "residual"], extra_keys=["success_005", "clipped"])
    write_csv(RESULTS / "family_h_contact_proxy_summary.csv", summary)
    write_table(
        RESULTS / "table_contact_proxy.tex",
        "Family H contact-proxy boundary. Known contact-effect maps help in the toy proxy; wrong modes expose the boundary.",
        "tab:contact-proxy",
        [
            ("method", "Method"),
            ("object_relative_error_mean", "Mean obj. rel. err."),
            ("object_relative_error_p90", "p90 obj. rel. err."),
            ("success_005_mean", "Success 0.05"),
            ("object_cosine_mean", "Obj. cosine"),
        ],
        sorted(summary, key=lambda r: r["object_relative_error_mean"]),
    )
    return {"family": "H", "rows": len(rows), "episodes": 0, "seconds": now_seconds() - t0}


def family_i_negative_controls(rng, arms):
    t0 = now_seconds()
    scenarios = ["matched_morphology", "random_map", "zero_effect", "same_geometry_diff_limits", "same_limits_diff_geometry"]
    methods = ["normalized_copy", "ejar_absolute"]
    rows = []
    n_trials = 3600
    for trial in range(n_trials):
        scenario = scenarios[trial % len(scenarios)]
        if scenario == "matched_morphology":
            source = arms[0]
            target = PlanarArm("matched_teacher", source.links.copy(), source.max_step.copy())
        elif scenario == "same_geometry_diff_limits":
            source = arms[2]
            target = PlanarArm("same_geom_tight_limits", source.links.copy(), source.max_step * np.array([0.60] * source.n))
        elif scenario == "same_limits_diff_geometry":
            source = arms[1]
            target = PlanarArm("same_limits_diff_geom", source.links * np.array([1.25, 0.55]), source.max_step.copy())
        else:
            source = arms[trial % 5]
            target = arms[(trial * 7 + 2) % (len(arms) - 1) + 1]
        q_s = source.random_q(rng)
        q_t = q_s.copy() if target.n == source.n and scenario == "matched_morphology" else target.random_q(rng, singular=(trial % 17 == 0))
        a_s = rng.uniform(-0.8, 0.8, size=source.n) * source.max_step
        desired = source.jacobian(q_s) @ a_s
        if scenario == "zero_effect":
            desired = np.zeros(2, dtype=float)
            a_s = np.zeros(source.n, dtype=float)
        for method in methods:
            if method == "normalized_copy":
                a_t, info = normalized_copy(source, target, a_s)
                actual = target.jacobian(q_t) @ a_t
            else:
                if scenario == "random_map":
                    j_random = rng.normal(0.0, 1.0, size=target.jacobian(q_t).shape)
                    a_t, info = decode_with_j(target, j_random, desired, weighted=True)
                else:
                    a_t, info = ejar_absolute(target, q_t, desired)
                actual = target.jacobian(q_t) @ a_t
            rows.append(
                {
                    "trial": trial,
                    "scenario": scenario,
                    "method": method,
                    "relative_effect_error": rel_error(actual, desired),
                    "absolute_error": float(np.linalg.norm(actual - desired)),
                    "effect_cosine": cosine(actual, desired),
                    "clipped": int(bool(info.get("clipped", False))),
                }
            )
    write_csv(RESULTS / "family_i_negative_seed.csv", rows)
    summary = []
    for scenario in scenarios:
        for method in methods:
            sub = [r for r in rows if r["scenario"] == scenario and r["method"] == method]
            summary.append(
                {
                    "scenario": scenario,
                    "method": method,
                    "n": len(sub),
                    "relative_effect_error_mean": mean(safe_float(r["relative_effect_error"]) for r in sub),
                    "relative_effect_error_p90": pctl((safe_float(r["relative_effect_error"]) for r in sub), 90),
                    "absolute_error_mean": mean(safe_float(r["absolute_error"]) for r in sub),
                    "effect_cosine_mean": mean(safe_float(r["effect_cosine"]) for r in sub),
                    "clipped_mean": mean(safe_float(r["clipped"]) for r in sub),
                }
            )
    write_csv(RESULTS / "family_i_negative_summary.csv", summary)
    write_table(
        RESULTS / "table_negative_controls.tex",
        "Family I negative controls and sanity checks. Matched morphology is a control where normalized copy should be competitive; random maps should break EJAR.",
        "tab:negative-controls",
        [
            ("scenario", "Scenario"),
            ("method", "Method"),
            ("relative_effect_error_mean", "Mean rel. err."),
            ("relative_effect_error_p90", "p90 rel. err."),
            ("clipped_mean", "Clip rate"),
        ],
        summary,
    )
    return {"family": "I", "rows": len(rows), "episodes": 0, "seconds": now_seconds() - t0}


def read_summary_csv(path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def make_plots():
    failures = 0
    try:
        rows = read_summary_csv(RESULTS / "family_a_main_summary.csv")
        methods = [r["method"] for r in rows]
        vals = [safe_float(r["relative_effect_error_mean"]) for r in rows]
        order = np.argsort(vals)
        plt.figure(figsize=(8.0, 4.2))
        plt.bar(np.arange(len(order)), [vals[i] for i in order])
        plt.xticks(np.arange(len(order)), [methods[i] for i in order], rotation=25, ha="right")
        plt.ylabel("mean relative effect error")
        plt.title("Family A: main morphology sweep")
        plt.tight_layout()
        plt.savefig(FIGURES / "figure_main_sweep_error.png", dpi=200)
        plt.savefig(FIGURES / "figure_main_sweep_error.pdf")
        plt.close()
    except Exception:
        failures += 1
    try:
        rows = read_summary_csv(RESULTS / "family_b_trajectory_summary.csv")
        methods = [r["method"] for r in rows]
        vals = [safe_float(r["success_010_mean"]) for r in rows]
        order = np.argsort(vals)[::-1]
        plt.figure(figsize=(8.0, 4.2))
        plt.bar(np.arange(len(order)), [vals[i] for i in order], color="#2f6f9f")
        plt.xticks(np.arange(len(order)), [methods[i] for i in order], rotation=25, ha="right")
        plt.ylabel("success @ 0.10")
        plt.title("Family B: long-horizon transfer")
        plt.tight_layout()
        plt.savefig(FIGURES / "figure_trajectory_success.png", dpi=200)
        plt.savefig(FIGURES / "figure_trajectory_success.pdf")
        plt.close()
    except Exception:
        failures += 1
    try:
        rows = read_summary_csv(RESULTS / "family_c_learning_summary.csv")
        methods = sorted(set(r["method"] for r in rows))
        plt.figure(figsize=(8.0, 4.8))
        for method in methods:
            sub = sorted([r for r in rows if r["method"] == method], key=lambda r: int(r["budget"]))
            plt.plot([int(r["budget"]) for r in sub], [safe_float(r["success_010_mean"]) for r in sub], marker="o", label=method)
        plt.xscale("log")
        plt.ylim(0, 1.02)
        plt.xlabel("training samples")
        plt.ylabel("success @ 0.10")
        plt.title("Family C: learned action-interface stress")
        plt.legend(frameon=False, fontsize=8)
        plt.tight_layout()
        plt.savefig(FIGURES / "figure_learning_success.png", dpi=200)
        plt.savefig(FIGURES / "figure_learning_success.pdf")
        plt.close()
    except Exception:
        failures += 1
    try:
        rows = read_summary_csv(RESULTS / "family_d_model_error_summary.csv")
        variants = [r["variant"] for r in rows]
        vals = [safe_float(r["relative_effect_error_mean"]) for r in rows]
        plt.figure(figsize=(8.0, 4.2))
        plt.bar(np.arange(len(rows)), vals, color="#8f5a2a")
        plt.xticks(np.arange(len(rows)), variants, rotation=25, ha="right")
        plt.ylabel("mean relative effect error")
        plt.title("Family D: model error")
        plt.tight_layout()
        plt.savefig(FIGURES / "figure_model_error.png", dpi=200)
        plt.savefig(FIGURES / "figure_model_error.pdf")
        plt.close()
    except Exception:
        failures += 1
    try:
        rows = read_summary_csv(RESULTS / "family_e_residual_summary.csv")
        names = [r["score"] for r in rows]
        vals = [safe_float(r["auprc"]) for r in rows]
        plt.figure(figsize=(6.6, 4.0))
        plt.bar(np.arange(len(rows)), vals, color="#526b38")
        plt.xticks(np.arange(len(rows)), names, rotation=20, ha="right")
        plt.ylabel("AUPRC")
        plt.title("Family E: infeasible-effect detection")
        plt.tight_layout()
        plt.savefig(FIGURES / "figure_residual_auprc.png", dpi=200)
        plt.savefig(FIGURES / "figure_residual_auprc.pdf")
        plt.close()
    except Exception:
        failures += 1
    try:
        rows = [r for r in read_summary_csv(RESULTS / "family_f_task_mismatch_summary.csv") if r["method"] == "ejar_assumed_map"]
        names = [r["mismatch"] for r in rows]
        vals = [safe_float(r["true_relative_error_mean"]) for r in rows]
        plt.figure(figsize=(7.0, 4.0))
        plt.bar(np.arange(len(rows)), vals, color="#8d3f3f")
        plt.xticks(np.arange(len(rows)), names, rotation=20, ha="right")
        plt.ylabel("true-frame relative error")
        plt.title("Family F: task-map mismatch")
        plt.tight_layout()
        plt.savefig(FIGURES / "figure_task_mismatch.png", dpi=200)
        plt.savefig(FIGURES / "figure_task_mismatch.pdf")
        plt.close()
    except Exception:
        failures += 1
    try:
        rows = read_summary_csv(RESULTS / "family_h_contact_proxy_summary.csv")
        names = [r["method"] for r in rows]
        vals = [safe_float(r["object_relative_error_mean"]) for r in rows]
        plt.figure(figsize=(7.2, 4.0))
        plt.bar(np.arange(len(rows)), vals, color="#4d6f7c")
        plt.xticks(np.arange(len(rows)), names, rotation=20, ha="right")
        plt.ylabel("object relative error")
        plt.title("Family H: contact-proxy boundary")
        plt.tight_layout()
        plt.savefig(FIGURES / "figure_contact_proxy.png", dpi=200)
        plt.savefig(FIGURES / "figure_contact_proxy.pdf")
        plt.close()
    except Exception:
        failures += 1
    return failures


def write_claim_evidence_table():
    a = read_summary_csv(RESULTS / "family_a_main_summary.csv")
    b = read_summary_csv(RESULTS / "family_b_trajectory_summary.csv")
    c = read_summary_csv(RESULTS / "family_c_learning_summary.csv")
    e = read_summary_csv(RESULTS / "family_e_residual_summary.csv")
    raw_a = next(r for r in a if r["method"] == "normalized_copy")
    ejar_a = next(r for r in a if r["method"] == "ejar_absolute")
    token_a = next(r for r in a if r["method"] == "ejar_capability")
    raw_b = next(r for r in b if r["method"] == "normalized_copy")
    ejar_b = next(r for r in b if r["method"] == "ejar_absolute")
    effect_c = [r for r in c if r["method"] == "effect_label_ejar" and int(r["budget"]) == 8000][0]
    pooled_c = [r for r in c if r["method"] == "pooled_raw" and int(r["budget"]) == 8000][0]
    best_e = sorted(e, key=lambda r: -safe_float(r["auprc"]))[0]
    rows = [
        {
            "claim": "Raw normalized actions are not effect invariant",
            "evidence": f"Family A normalized-copy mean error {safe_float(raw_a['relative_effect_error_mean']):.3f}",
            "status": "supported synthetic",
        },
        {
            "claim": "EJAR absolute reduces morphology transfer error",
            "evidence": f"Family A EJAR mean error {safe_float(ejar_a['relative_effect_error_mean']):.3f}",
            "status": "supported synthetic",
        },
        {
            "claim": "Capability tokens preserve local authority, not absolute displacement",
            "evidence": f"Family A token mean error {safe_float(token_a['relative_effect_error_mean']):.3f}",
            "status": "supported with scope",
        },
        {
            "claim": "One-step mismatch compounds over trajectories",
            "evidence": f"Family B normalized success {safe_float(raw_b['success_010_mean']):.3f}; EJAR {safe_float(ejar_b['success_010_mean']):.3f}",
            "status": "supported synthetic",
        },
        {
            "claim": "Effect labels ease simple policy transfer",
            "evidence": f"Family C effect-label mean error {safe_float(effect_c['relative_goal_effect_error_mean']):.3f} vs pooled raw {safe_float(pooled_c['relative_goal_effect_error_mean']):.3f}",
            "status": "limited linear-policy evidence",
        },
        {
            "claim": "Residual is an infeasibility diagnostic under valid maps",
            "evidence": f"Family E best AUPRC {safe_float(best_e['auprc']):.3f} with {best_e['score']}",
            "status": "supported only under model validity",
        },
    ]
    write_csv(RESULTS / "family_claim_evidence.csv", rows)
    write_table(
        RESULTS / "table_claim_evidence.tex",
        "Claim-to-evidence map for the v3 synthetic suite.",
        "tab:claim-evidence",
        [("claim", "Claim"), ("evidence", "Evidence"), ("status", "Status")],
        rows,
        digits=3,
    )


def write_runtime_table(family_results, plot_failures):
    rows = []
    for item in family_results:
        rows.append(
            {
                "family": item["family"],
                "rows": item["rows"],
                "episodes": item["episodes"],
                "seconds": item["seconds"],
            }
        )
    rows.append({"family": "plots", "rows": 0, "episodes": 0, "seconds": 0.0 if plot_failures == 0 else plot_failures})
    write_csv(RESULTS / "family_runtime_summary.csv", rows)
    write_table(
        RESULTS / "table_runtime_memory.tex",
        "Runtime and artifact scale for the RAM-light full-scale runner. Rows are streamed family by family to CSV.",
        "tab:runtime",
        [("family", "Family"), ("rows", "Rows"), ("episodes", "Episodes"), ("seconds", "Seconds")],
        rows,
        digits=2,
    )


def write_evidence_summary(family_results, metadata):
    a = read_summary_csv(RESULTS / "family_a_main_summary.csv")
    b = read_summary_csv(RESULTS / "family_b_trajectory_summary.csv")
    c = read_summary_csv(RESULTS / "family_c_learning_summary.csv")
    d = read_summary_csv(RESULTS / "family_d_model_error_summary.csv")
    e = read_summary_csv(RESULTS / "family_e_residual_summary.csv")
    raw_a = next(r for r in a if r["method"] == "normalized_copy")
    ejar_a = next(r for r in a if r["method"] == "ejar_absolute")
    token_a = next(r for r in a if r["method"] == "ejar_capability")
    raw_b = next(r for r in b if r["method"] == "normalized_copy")
    ejar_b = next(r for r in b if r["method"] == "ejar_absolute")
    exact_d = next(r for r in d if r["variant"] == "exact")
    noisy_d = next(r for r in d if r["variant"] == "gaussian_020")
    best_e = sorted(e, key=lambda r: -safe_float(r["auprc"]))[0]
    effect_c = [r for r in c if r["method"] == "effect_label_ejar" and int(r["budget"]) == 8000][0]
    pooled_c = [r for r in c if r["method"] == "pooled_raw" and int(r["budget"]) == 8000][0]
    lines = [
        "# Full-Scale Evidence Summary",
        "",
        f"- Stage: {metadata['stage']}",
        f"- Total rows: {metadata['total_rows']}",
        f"- Total episodes/decision rows: {metadata['total_episodes']}",
        f"- Plot failures: {metadata['plot_failures']}",
        "",
        "## Headline Numbers",
        "",
        f"- Family A normalized-copy mean relative error: {safe_float(raw_a['relative_effect_error_mean']):.3f}.",
        f"- Family A EJAR-absolute mean relative error: {safe_float(ejar_a['relative_effect_error_mean']):.3f}.",
        f"- Family A EJAR-capability mean token-relative error: {safe_float(token_a['relative_effect_error_mean']):.3f}.",
        f"- Family B normalized-copy success at 0.10: {safe_float(raw_b['success_010_mean']):.3f}.",
        f"- Family B EJAR-absolute success at 0.10: {safe_float(ejar_b['success_010_mean']):.3f}.",
        f"- Family C effect-label EJAR mean relative error at 8000 samples: {safe_float(effect_c['relative_goal_effect_error_mean']):.3f}, versus pooled raw-action error {safe_float(pooled_c['relative_goal_effect_error_mean']):.3f}.",
        f"- Family D exact-Jacobian mean relative error: {safe_float(exact_d['relative_effect_error_mean']):.3f}.",
        f"- Family D 20 percent noisy-Jacobian mean relative error: {safe_float(noisy_d['relative_effect_error_mean']):.3f}.",
        f"- Family E best infeasibility AUPRC: {safe_float(best_e['auprc']):.3f} using {best_e['score']}.",
        "",
        "## Scope",
        "",
        "These results support a synthetic mechanism claim. They do not prove real-robot deployment, visual policy learning, contact-rich manipulation, or correspondence discovery.",
    ]
    (DOCS / "evidence_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ensure_dirs()
    rng = np.random.default_rng(SEED)
    arms = make_arm_zoo()
    family_status = {}
    family_results = []
    total_rows = 0
    total_episodes = 0
    start = now_seconds()
    record_progress("running", family_status, total_rows, total_episodes)
    for name, fn in [
        ("A", family_a_main_sweep),
        ("B", family_b_trajectory),
        ("C", family_c_learning),
        ("D", family_d_model_error),
        ("E", family_e_residual_calibration),
        ("F", family_f_task_mismatch),
        ("G", family_g_control_rate),
        ("H", family_h_contact_proxy),
        ("I", family_i_negative_controls),
    ]:
        result = fn(rng, arms)
        family_results.append(result)
        family_status[name] = "complete"
        total_rows += int(result["rows"])
        total_episodes += int(result["episodes"])
        record_progress("running", family_status, total_rows, total_episodes)
        print(json.dumps(result), flush=True)
    plot_failures = make_plots()
    write_claim_evidence_table()
    write_runtime_table(family_results, plot_failures)
    metadata = {
        "stage": "complete",
        "seed": SEED,
        "total_rows": total_rows,
        "total_episodes": total_episodes,
        "plot_failures": plot_failures,
        "families": family_results,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "matplotlib": getattr(plt.matplotlib, "__version__", "unknown"),
        "elapsed_seconds": now_seconds() - start,
        "outputs": sorted(str(p.relative_to(ROOT)) for p in RESULTS.iterdir() if p.is_file()),
    }
    (RESULTS / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    record_progress("complete", family_status, total_rows, total_episodes, plot_failures)
    write_evidence_summary(family_results, metadata)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
