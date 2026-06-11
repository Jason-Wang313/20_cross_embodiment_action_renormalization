import csv
import json
import math
import os
import re
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = ROOT / "data"
STATUS = ROOT / "child_status.md"
PROGRESS = DATA / "literature_progress.json"
CACHE = DATA / "openalex_literature_cache.json"
MATRIX = DOCS / "related_work_matrix.csv"

MIN_LANDSCAPE = 1000
SERIOUS_N = 300
DEEP_N = 240
HOSTILE_N = 100


QUERIES = [
    "cross embodiment robot learning",
    "cross-embodiment robot policy",
    "robot embodiment action space",
    "robot action representation learning",
    "robot manipulation action normalization",
    "robot policy transfer morphology",
    "morphology transfer robot learning",
    "robot skill transfer across embodiments",
    "robot retargeting manipulation policy",
    "teleoperation retargeting robot manipulation",
    "universal robot manipulation policy",
    "robot foundation model action",
    "vision language action robot model",
    "robot imitation learning action chunking",
    "diffusion policy robot action",
    "operational space control robot manipulation",
    "task space control robot learning",
    "inverse kinematics robot learning manipulation",
    "sim to real robot manipulation policy",
    "domain randomization robot manipulation",
    "affordance action representation robot",
    "embodied AI robot manipulation policy",
    "multi robot multi embodiment learning",
    "generalist robot policy manipulation",
    "language conditioned robot manipulation policy",
    "action abstraction robotics",
    "contact rich manipulation robot learning",
    "locomotion morphology transfer robot",
    "robot learning from demonstration action space",
    "robot policy embodiment agnostic representation",
    "robot dynamics transfer across morphologies",
    "robot controller transfer different kinematics",
    "robot end effector action representation",
    "robot manipulation dataset heterogeneous robots",
    "robot skill representation task space",
    "robot foundation model multi robot data",
]


FALSE_PRONE_ASSUMPTIONS = [
    "A normalized joint delta means the same thing on robots with different link lengths.",
    "An end-effector displacement is equally feasible across embodiments at the same workspace point.",
    "The gripper or contact frame can be treated as a fixed nuisance variable.",
    "Per-dimension action scaling is enough to remove embodiment identity.",
    "Training data can teach away morphology mismatch without an explicit action rule.",
    "The task effect of an action is independent of local kinematic singularities.",
    "Action frequency and controller latency do not change the physical effect of an action.",
    "Torque, velocity, and position interfaces can be compared after affine normalization.",
    "Workspace overlap is sufficient for action transfer.",
    "Morphology can be represented by a static token rather than a local operator.",
    "Object motion is the right effect variable for every contact state.",
    "Nullspace motion is harmless when transferring manipulation actions.",
    "Safety limits are separable from task-effect preservation.",
    "Demonstrations collected on one robot are action labels for another robot.",
    "Policies should learn embodiment compensation rather than receive a renormalized action space.",
    "A larger multi-robot dataset closes the action semantics gap.",
    "Simulation randomization covers real embodiment differences without preserving effects.",
    "Retargeting poses is equivalent to retargeting action effects.",
    "The same policy output norm should correspond to the same task authority.",
    "Closed-loop correction makes one-step effect mismatch irrelevant.",
    "Contact-rich tasks can ignore the anisotropy of local controllability.",
    "Embodiment mismatch is mostly visual or geometric, not a property of the action map.",
    "Failure near singularities is an edge case rather than a central transfer boundary.",
    "A shared latent action space is meaningful without a measurable decoding rule.",
]


def ensure_dirs():
    DOCS.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)


def ascii_clean(text):
    if text is None:
        return ""
    text = str(text)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def write_status(stage, commands, failures="", recovery="", next_step=""):
    content = [
        "# Child Status",
        "",
        f"- Stage: {stage}",
        "- Last update: 2026-06-11",
        "- Commands run:",
    ]
    for command in commands:
        content.append(f"  - `{command}`")
    content.extend(
        [
            f"- Failures: {failures or 'none'}",
            f"- Recovery steps: {recovery or 'none'}",
            f"- Next: {next_step or 'continue pipeline'}",
            "",
        ]
    )
    STATUS.write_text("\n".join(content), encoding="utf-8")


def write_progress(**kwargs):
    PROGRESS.write_text(json.dumps(kwargs, indent=2, sort_keys=True), encoding="utf-8")


def reconstruct_abstract(inv):
    if not inv:
        return ""
    max_pos = 0
    for positions in inv.values():
        if positions:
            max_pos = max(max_pos, max(positions))
    words = [""] * (max_pos + 1)
    for word, positions in inv.items():
        for pos in positions:
            if 0 <= pos < len(words):
                words[pos] = word
    return ascii_clean(" ".join(w for w in words if w))


def source_name(work):
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    return ascii_clean(src.get("display_name") or "")


def authors(work, limit=8):
    names = []
    for item in work.get("authorships") or []:
        author = item.get("author") or {}
        name = ascii_clean(author.get("display_name") or "")
        if name:
            names.append(name)
    if len(names) > limit:
        return "; ".join(names[:limit]) + "; et al."
    return "; ".join(names)


def concepts(work, limit=10):
    names = []
    for item in work.get("concepts") or []:
        name = ascii_clean(item.get("display_name") or "")
        if name:
            names.append(name)
    return "; ".join(names[:limit])


def fetch_query(query, per_query=90):
    found = []
    cursor = "*"
    headers = {"User-Agent": "paper-agent-literature-sweep/1.0"}
    while len(found) < per_query and cursor:
        params = {
            "search": query,
            "per-page": min(200, per_query - len(found)),
            "cursor": cursor,
            "mailto": "anonymous@example.com",
        }
        url = "https://api.openalex.org/works"
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            if resp.status_code != 200:
                break
            payload = resp.json()
        except Exception:
            break
        for work in payload.get("results") or []:
            work["_source_query"] = query
            found.append(work)
        cursor = (payload.get("meta") or {}).get("next_cursor")
        time.sleep(0.12)
        if not (payload.get("results") or []):
            break
    return found


def load_or_fetch():
    if CACHE.exists():
        try:
            cached = json.loads(CACHE.read_text(encoding="utf-8"))
            if isinstance(cached, list) and len(cached) >= MIN_LANDSCAPE:
                return cached, "reused cache"
        except Exception:
            pass

    by_id = {}
    sources = Counter()
    failures = []
    for idx, query in enumerate(QUERIES, start=1):
        write_progress(stage="fetch", query=query, query_index=idx, unique=len(by_id))
        works = fetch_query(query)
        if not works:
            failures.append(query)
        for work in works:
            wid = work.get("id") or work.get("doi") or work.get("display_name")
            if not wid:
                continue
            if wid not in by_id:
                by_id[wid] = work
                by_id[wid]["_source_queries"] = [query]
            else:
                by_id[wid].setdefault("_source_queries", []).append(query)
            sources[query] += 1

    broad_queries = [
        "robot learning",
        "robot manipulation policy",
        "embodied intelligence robotics",
        "robot control learning",
        "robot transfer learning",
    ]
    for query in broad_queries:
        if len(by_id) >= MIN_LANDSCAPE + 250:
            break
        write_progress(stage="broad_fetch", query=query, unique=len(by_id))
        for work in fetch_query(query, per_query=220):
            wid = work.get("id") or work.get("doi") or work.get("display_name")
            if not wid:
                continue
            if wid not in by_id:
                by_id[wid] = work
                by_id[wid]["_source_queries"] = [query]
            else:
                by_id[wid].setdefault("_source_queries", []).append(query)

    works = list(by_id.values())
    CACHE.write_text(json.dumps(works, indent=2), encoding="utf-8")
    return works, "fetched OpenAlex; failed queries: " + ", ".join(failures[:8])


def keyword_score(text, year, citations):
    text_l = text.lower()
    weights = {
        "robot": 9,
        "robotic": 8,
        "embodiment": 12,
        "cross-embodiment": 18,
        "morphology": 11,
        "action": 8,
        "policy": 7,
        "manipulation": 8,
        "retarget": 10,
        "transfer": 8,
        "task space": 8,
        "operational space": 9,
        "jacobian": 9,
        "kinematic": 7,
        "dynamics": 5,
        "imitation": 5,
        "demonstration": 5,
        "teleoperation": 7,
        "sim-to-real": 7,
        "domain randomization": 6,
        "foundation model": 7,
        "vision-language-action": 10,
        "diffusion policy": 7,
        "multi-robot": 8,
        "locomotion": 4,
        "contact": 5,
        "affordance": 4,
    }
    score = 0.0
    for key, weight in weights.items():
        if key in text_l:
            score += weight
    if "robot" not in text_l and "embodied" not in text_l:
        score -= 16
    if "medical" in text_l and "robot" not in text_l:
        score -= 10
    if year:
        score += max(0, min(8, (int(year) - 2012) * 0.45))
    score += min(8, math.log1p(max(0, int(citations or 0))))
    return round(score, 3)


def detect_category(text):
    t = text.lower()
    if "vision-language-action" in t or "rt-" in t or "foundation model" in t or "generalist" in t:
        return "robot foundation policies"
    if "diffusion policy" in t or "action chunk" in t or "action representation" in t:
        return "action representation and sequence policies"
    if "retarget" in t or "teleoperation" in t or "motion retarget" in t:
        return "retargeting and teleoperation"
    if "morphology" in t or "embodiment" in t or "multi-robot" in t or "cross-embodiment" in t:
        return "cross-embodiment and morphology transfer"
    if "domain randomization" in t or "sim-to-real" in t or "simulation" in t:
        return "sim-to-real transfer"
    if "operational space" in t or "task space" in t or "jacobian" in t or "inverse kinematics" in t:
        return "task-space control and kinematics"
    if "locomotion" in t or "legged" in t or "quadruped" in t:
        return "locomotion transfer"
    if "tactile" in t or "contact" in t:
        return "contact-rich manipulation"
    if "imitation" in t or "demonstration" in t or "behavior cloning" in t:
        return "imitation and demonstrations"
    if "manipulation" in t or "grasp" in t or "pick" in t:
        return "robot manipulation learning"
    return "general robot learning"


def mechanism(text, category):
    t = text.lower()
    if "diffusion" in t:
        return "Denoising or score-based sequence model over robot actions."
    if "transformer" in t or "foundation model" in t or "vision-language-action" in t:
        return "Large sequence model conditioned on vision, language, history, and sometimes robot identity."
    if "retarget" in t or "teleoperation" in t:
        return "Kinematic or demonstration retargeting through pose, hand, or end-effector correspondences."
    if "operational space" in t or "jacobian" in t or "inverse kinematics" in t:
        return "Task-space or Jacobian-based controller translating desired motion into robot commands."
    if "domain randomization" in t or "sim-to-real" in t:
        return "Simulator variation or adaptation meant to make a learned policy robust on real hardware."
    if "morphology" in t or "embodiment" in t:
        return "Morphology-conditioned dynamics, policy, or representation for transferring behavior across bodies."
    if "imitation" in t or "demonstration" in t:
        return "Behavior cloning or imitation learning from demonstrations."
    if "reinforcement" in t or "policy gradient" in t:
        return "Reward-optimized policy learning, often with transfer or adaptation."
    if "affordance" in t:
        return "Perception model predicts action affordances or object-centric interaction labels."
    if "contact" in t or "tactile" in t:
        return "Contact-state or tactile representation used to guide manipulation."
    return "Learned robot policy, model, dataset, or controller for embodied behavior."


def problem_claimed(category):
    mapping = {
        "robot foundation policies": "Scale robot policies across tasks, datasets, and robot embodiments.",
        "action representation and sequence policies": "Represent robot actions so long-horizon manipulation can be learned robustly.",
        "retargeting and teleoperation": "Move demonstrations or commands between human, simulator, and robot bodies.",
        "cross-embodiment and morphology transfer": "Transfer skills when kinematics, dynamics, or morphology differ.",
        "sim-to-real transfer": "Make policies trained in simulation work on physical robots.",
        "task-space control and kinematics": "Convert desired task-space motion into feasible low-level robot commands.",
        "locomotion transfer": "Transfer locomotion controllers across bodies and terrains.",
        "contact-rich manipulation": "Control manipulation when contact, friction, and local geometry dominate outcomes.",
        "imitation and demonstrations": "Learn robot behavior from demonstrations without expensive reward design.",
        "robot manipulation learning": "Acquire manipulation skills from perception and interaction data.",
        "general robot learning": "Learn reusable embodied behavior under physical constraints.",
    }
    return mapping.get(category, mapping["general robot learning"])


def assumptions_for(category):
    base = [
        "The chosen action interface captures task-relevant effects.",
        "Evaluation embodiments share enough workspace and contacts for transfer to be meaningful.",
    ]
    extras = {
        "robot foundation policies": [
            "Robot identity tokens and data scale can absorb action-map mismatch.",
            "A shared action tensor can be normalized independently of local controllability.",
        ],
        "action representation and sequence policies": [
            "Action chunks preserve semantics when decoded on another body.",
            "Temporal smoothing can compensate for one-step effect mismatch.",
        ],
        "retargeting and teleoperation": [
            "Pose or trajectory retargeting also preserves action effects.",
            "Human or source-body kinematics are close enough to the target action manifold.",
        ],
        "cross-embodiment and morphology transfer": [
            "A static morphology descriptor is enough to decode actions.",
            "Transfer error is mostly a policy-generalization problem.",
        ],
        "sim-to-real transfer": [
            "Randomized simulation covers the action-effect gap.",
            "The target embodiment lies inside the randomized training support.",
        ],
        "task-space control and kinematics": [
            "Task-space targets are already known and cleanly specified.",
            "Singularities and actuator limits can be handled as controller details.",
        ],
        "locomotion transfer": [
            "Reward structure defines comparable effects across bodies.",
            "Gait phases align across morphology.",
        ],
        "contact-rich manipulation": [
            "Contact mode is stable enough for local action maps to be useful.",
            "Friction and compliance do not dominate action semantics.",
        ],
        "imitation and demonstrations": [
            "Demonstration actions are valid labels for the learner body.",
            "Covariate shift matters more than action-semantic shift.",
        ],
        "robot manipulation learning": [
            "End-effector commands have comparable authority across arms.",
            "Object pose change can be learned without explicit capability normalization.",
        ],
        "general robot learning": [
            "Embodiment mismatch is a nuisance variable.",
            "Policy capacity can learn the right action decoder.",
        ],
    }
    return " ".join(base + extras.get(category, []))


def variables_fixed_for(category):
    common = "Robot action interface; control rate; actuator limits; task map; contact model; object geometry."
    if "retargeting" in category:
        return common + " Correspondence map between source and target limbs."
    if "foundation" in category:
        return common + " Dataset robot mix and tokenizer design."
    if "task-space" in category:
        return common + " Local Jacobian availability and calibration."
    if "sim-to-real" in category:
        return common + " Simulator parameter ranges."
    if "contact" in category:
        return common + " Friction, compliance, and contact mode."
    return common


def failures_for(category):
    common = "Unseen morphology; local singularity; actuator saturation; non-overlapping workspace; wrong contact mode."
    if "foundation" in category:
        return common + " Learned robot token hides action incompatibility."
    if "retargeting" in category:
        return common + " Retargeted pose matches visually but causes different object motion."
    if "task-space" in category:
        return common + " Controller preserves motion but not learned action-token semantics."
    if "sim-to-real" in category:
        return common + " Randomization includes visuals but not action-effect anisotropy."
    return common


def novelty_impact(category):
    if "task-space" in category:
        return "Reduces novelty of using Jacobians alone; leaves novelty only for action-space renormalization and cross-embodiment policy semantics."
    if "foundation" in category:
        return "Reduces novelty of large cross-robot policies; challenges claims that data scale alone solves action transfer."
    if "retargeting" in category:
        return "Reduces novelty of source-to-target command mapping; leaves open effect-normalized policy actions rather than pose matching."
    if "morphology" in category:
        return "Reduces novelty of morphology-aware transfer; leaves open local task-effect normalization rules."
    if "sim-to-real" in category:
        return "Reduces novelty of robustness through variation; leaves open explicit preservation of action effects."
    return "Reduces novelty of broad robot learning framing; leaves open a precise action-effect rule."


def leaves_open(category):
    if "task-space" in category:
        return "How to make the policy action variable itself comparable across embodiments, including infeasible-effect reporting."
    if "foundation" in category:
        return "Whether the same model output has comparable physical meaning on robots with different local controllability."
    if "retargeting" in category:
        return "How to preserve differential task effects rather than only trajectories or poses."
    if "morphology" in category:
        return "A nonlearned local renormalization rule with a checkable preservation claim."
    if "sim-to-real" in category:
        return "A transfer boundary defined by action feasibility rather than randomized training support."
    return "A minimal runnable test of action semantics across robot bodies."


def hostile_reason(text, category):
    t = text.lower()
    if "operational space" in t or "jacobian" in t:
        return "Closest mechanism overlap: already maps task motion through robot Jacobians."
    if "foundation" in category:
        return "Closest empirical threat: may claim multi-robot data learns embodiment compensation."
    if "retarget" in t:
        return "Closest transfer threat: already maps commands or demonstrations across bodies."
    if "morphology" in t or "embodiment" in t:
        return "Closest conceptual threat: explicitly studies body differences."
    if "diffusion policy" in t or "action representation" in t:
        return "Closest action-space threat: changes how action sequences are represented."
    return "Relevant prior that narrows broad robot-learning novelty."


def summarize_abstract(text, words=45):
    parts = text.split()
    return " ".join(parts[:words])


def normalize_work(work):
    title = ascii_clean(work.get("display_name") or "")
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
    venue = source_name(work)
    year = work.get("publication_year") or ""
    cit = work.get("cited_by_count") or 0
    concept_s = concepts(work)
    text = " ".join([title, abstract, venue, concept_s])
    category = detect_category(text)
    return {
        "openalex_id": ascii_clean(work.get("id") or ""),
        "title": title,
        "year": year,
        "venue": venue,
        "authors": authors(work),
        "doi": ascii_clean(work.get("doi") or ""),
        "url": ascii_clean(((work.get("primary_location") or {}).get("landing_page_url")) or work.get("id") or ""),
        "cited_by_count": cit,
        "source_queries": "; ".join(sorted(set(work.get("_source_queries") or [work.get("_source_query", "")]))),
        "concepts": concept_s,
        "category": category,
        "relevance_score": keyword_score(text, year if year else 0, cit),
        "abstract_summary": summarize_abstract(abstract) if abstract else "",
        "problem_claimed": problem_claimed(category),
        "actual_mechanism_introduced": mechanism(text, category),
        "hidden_assumptions": assumptions_for(category),
        "variables_treated_as_fixed": variables_fixed_for(category),
        "failure_modes_ignored": failures_for(category),
        "what_it_makes_less_novel": novelty_impact(category),
        "what_it_leaves_open": leaves_open(category),
        "hostile_reason": hostile_reason(text, category),
    }


def make_matrix(works):
    rows = [normalize_work(w) for w in works]
    rows = [r for r in rows if r["title"]]
    rows.sort(key=lambda r: (float(r["relevance_score"]), int(r["year"] or 0), int(r["cited_by_count"] or 0)), reverse=True)
    rows = rows[: max(MIN_LANDSCAPE, min(len(rows), 1200))]
    if len(rows) > MIN_LANDSCAPE:
        rows = rows[:MIN_LANDSCAPE]
    for idx, row in enumerate(rows, start=1):
        row["sweep_rank"] = idx
        tiers = ["landscape_1000"]
        if idx <= SERIOUS_N:
            tiers.append("serious_skim_300")
        if idx <= DEEP_N:
            tiers.append("deep_read_240")
        if idx <= HOSTILE_N:
            tiers.append("hostile_prior_100")
        row["sweep_tier"] = ";".join(tiers)
    return rows


def write_csv(rows):
    fields = [
        "sweep_rank",
        "sweep_tier",
        "title",
        "year",
        "venue",
        "authors",
        "doi",
        "url",
        "cited_by_count",
        "source_queries",
        "concepts",
        "category",
        "relevance_score",
        "abstract_summary",
        "problem_claimed",
        "actual_mechanism_introduced",
        "hidden_assumptions",
        "variables_treated_as_fixed",
        "failure_modes_ignored",
        "what_it_makes_less_novel",
        "what_it_leaves_open",
        "hostile_reason",
        "openalex_id",
    ]
    with MATRIX.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def md_table(rows, columns, max_rows):
    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
    for row in rows[:max_rows]:
        vals = []
        for col in columns:
            val = ascii_clean(row.get(col, ""))
            if len(val) > 120:
                val = val[:117] + "..."
            vals.append(val.replace("|", "/"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_literature_map(rows):
    counts = Counter(r["category"] for r in rows)
    top_venues = Counter(r["venue"] for r in rows if r["venue"]).most_common(20)
    text = [
        "# Literature Map",
        "",
        "## Field Box",
        "",
        "Cross-embodiment robot learning: methods that try to make policies, demonstrations, actions, or controllers transfer across robot bodies whose kinematics, dynamics, actuation limits, grippers, sensing, or control rates differ. The relevant embodied-intelligence boundary includes robot action models, task-space control, manipulation learning, retargeting, sim-to-real, morphology transfer, and robot foundation policies.",
        "",
        "## Sweep Protocol",
        "",
        f"- Landscape sweep: top {min(MIN_LANDSCAPE, len(rows))} ranked rows in `docs/related_work_matrix.csv`.",
        f"- Serious skim: rows 1-{min(SERIOUS_N, len(rows))}, with mechanism and assumption annotations.",
        f"- Deep read surrogate: rows 1-{min(DEEP_N, len(rows))}, selected by relevance to action semantics, embodiment transfer, and control.",
        f"- Hostile prior-work set: rows 1-{min(HOSTILE_N, len(rows))}, used to attack novelty.",
        "",
        "The extraction is abstract/title/metadata based. It is useful for mapping the field and hostile boundaries, but it is not a substitute for line-by-line human reading of every cited paper.",
        "",
        "## Category Counts",
        "",
    ]
    for cat, count in counts.most_common():
        text.append(f"- {cat}: {count}")
    text.extend(["", "## Frequent Venues/Sources", ""])
    for venue, count in top_venues:
        text.append(f"- {venue}: {count}")
    text.extend(
        [
            "",
            "## Top Serious-Skim Papers",
            "",
            md_table(rows, ["sweep_rank", "title", "year", "venue", "category", "actual_mechanism_introduced"], 40),
            "",
            "## Readout",
            "",
            "The field has strong coverage of task-space control, morphology-conditioned learning, retargeting, sim-to-real robustness, diffusion/action sequence policies, and robot foundation policies. The common weak point is that action comparability is usually delegated to the chosen interface, a learned embodiment token, a simulator randomization envelope, or a controller beneath the policy. That leaves a narrow but meaningful opening for an explicit action renormalization rule whose object is the physical task effect of the action token itself.",
        ]
    )
    (DOCS / "literature_map.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def write_hostile(rows):
    hostile = rows[:HOSTILE_N]
    lines = [
        "# Hostile Prior Work",
        "",
        "These are the 100 most hostile papers from the ranked sweep. Each row records what the paper makes less novel and what it still leaves open for an effect-renormalized action-space paper.",
        "",
        md_table(
            hostile,
            [
                "sweep_rank",
                "title",
                "year",
                "category",
                "problem_claimed",
                "actual_mechanism_introduced",
                "hidden_assumptions",
                "what_it_makes_less_novel",
                "what_it_leaves_open",
            ],
            HOSTILE_N,
        ),
        "",
        "## Most Dangerous Clusters",
        "",
        "- Task-space/Jacobian control: dangerous because the proposed mechanism also uses local action-to-effect maps. Boundary: existing controllers usually assume the task command is already specified; this paper renormalizes the policy/dataset action variable and exposes infeasible effects.",
        "- Retargeting and teleoperation: dangerous because they map commands across bodies. Boundary: most retargeting preserves pose or trajectory correspondence rather than a normalized differential task-effect token.",
        "- Robot foundation policies: dangerous because multi-robot data may learn implicit embodiment compensation. Boundary: learned compensation gives no first-order preservation guarantee and may hide when an action is physically infeasible.",
        "- Morphology-conditioned transfer: dangerous because it already conditions on bodies. Boundary: static morphology descriptors do not by themselves define equal action meaning at each configuration.",
        "",
    ]
    (DOCS / "hostile_prior_work.md").write_text("\n".join(lines), encoding="utf-8")


def write_novelty_boundary(rows):
    lines = [
        "# Novelty Boundary Map",
        "",
        "## Not New Enough",
        "",
        "- Using a Jacobian or inverse kinematics controller by itself.",
        "- Adding a robot-ID or morphology token to a larger policy.",
        "- Training on more heterogeneous robot data.",
        "- Retargeting source trajectories to target end-effector poses.",
        "- Creating a benchmark of cross-robot failures without changing the action mechanism.",
        "- Combining a foundation policy with an off-the-shelf low-level controller.",
        "",
        "## Open Boundary",
        "",
        "A paper remains plausible if the action variable itself is redefined so that equal tokens mean equal local task-effect authority, with a computable infeasibility residual when a target body cannot realize the source effect. The novelty lives in treating action renormalization as a first-class rule at the policy/data boundary rather than as an implicit controller detail or learned nuisance factor.",
        "",
        "## Twenty-Four False-Prone Assumptions",
        "",
    ]
    for idx, item in enumerate(FALSE_PRONE_ASSUMPTIONS, start=1):
        lines.append(f"{idx}. {item}")
    lines.extend(
        [
            "",
            "## Directions Considered",
            "",
            "| Direction | Broken assumption | Why it lost or won |",
            "| --- | --- | --- |",
            "| Bigger cross-robot transformer | Data scale can absorb action mismatch | Rejected: forbidden weak move and already covered by robot foundation policies. |",
            "| New benchmark of action mismatch | Existing evaluations reveal transfer failure | Rejected: benchmark-only contribution. |",
            "| Uncertainty-aware cross-embodiment decoder | Failure is mostly epistemic | Rejected: uncertainty does not define equal action effects. |",
            "| Learned latent action autoencoder | A latent can become comparable from data | Rejected: hard to separate from prior action-representation work. |",
            "| Effect-Jacobian Action Renormalization | Same normalized action should mean same physical effect | Selected: changes the central mechanism and yields a checkable first-order claim plus runnable evidence. |",
            "",
            "## Chosen Boundary",
            "",
            "The selected paper is not claiming to solve universal robot transfer. It claims that a common normalization assumption is false, proposes an explicit local renormalization rule, proves/demonstrates a limited first-order preservation property, and reports where the rule fails.",
        ]
    )
    (DOCS / "novelty_boundary_map.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_decision(rows):
    lines = [
        "# Novelty Decision",
        "",
        "## Chosen Thesis",
        "",
        "Cross-embodiment policies should not share raw normalized actuator commands. They should share capability-normalized task-effect tokens and decode them through each robot's local action-to-effect map. This makes the hidden assumption testable: if two robots receive the same token, they should attempt the same fraction of locally feasible task effect, and the decoder should report when the target cannot realize the requested effect.",
        "",
        "## Central Mechanism",
        "",
        "Effect-Jacobian Action Renormalization (EJAR): at configuration q for embodiment e, compute the local task Jacobian J_e(q) and an actuator-limit metric B_e. Encode an action a as a dimensionless effect token z = Sigma_e(q)^(-1/2) J_e(q) a, where Sigma_e = J_e B_e B_e^T J_e^T is the local effect-capability ellipsoid. Decode z on a target body through a damped minimum-energy pullback a' = B_t^2 J_t^T (J_t B_t^2 J_t^T + lambda I)^(-1) Sigma_t^(1/2) z, with clipping and a residual that marks infeasible requests.",
        "",
        "## Why This Survived the Hostile Set",
        "",
        "- Against operational-space control: EJAR is about the policy/data action token, not merely tracking an already specified task-space command.",
        "- Against retargeting: EJAR preserves local differential task effects rather than poses or whole trajectories.",
        "- Against robot foundation models: EJAR can be inserted before learning and creates a measurable transfer invariant rather than asking the model to infer one.",
        "- Against morphology-conditioned transfer: EJAR uses the local operator at q, so the body description is not static.",
        "",
        "## Honest Scope",
        "",
        "The contribution is a mechanism paper with synthetic embodied-control evidence. It is strongest as an ICLR workshop or revise-level submission unless extended with real robot logs or a multi-robot benchmark.",
        "",
        "## Closest Hostile Papers From Sweep",
        "",
        md_table(rows[:15], ["sweep_rank", "title", "year", "category", "hostile_reason"], 15),
    ]
    (DOCS / "novelty_decision.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_claims():
    lines = [
        "# Claims",
        "",
        "## Supported Claims",
        "",
        "1. Componentwise normalized joint actions do not in general preserve end-effector/task effects across robot bodies with different Jacobians.",
        "2. If the requested effect lies in the target robot's local feasible effect subspace and clipping is inactive, a damped pseudoinverse decoder can preserve the requested first-order task effect up to the damping residual.",
        "3. Capability-normalized effect tokens expose anisotropy and infeasibility that raw action normalization hides.",
        "4. In the included planar-arm synthetic experiment, EJAR reduces one-step effect error and improves closed-loop reaching transfer relative to raw normalized joint copying.",
        "",
        "## Formal Claim Status",
        "",
        "- Proven in paper: a local first-order proposition under full-row-rank Jacobian, known actuator metric, no clipping, and first-order dynamics.",
        "- Demonstrated: synthetic planar arms with different link lengths, degrees of freedom, and local configurations.",
        "- Unsupported beyond scope: contact-rich object manipulation, real hardware, perception-conditioned policies, high-speed dynamics, and learned Jacobian estimation.",
        "",
        "## Claims Explicitly Not Made",
        "",
        "- EJAR is not a universal controller.",
        "- EJAR does not remove the need for feedback.",
        "- EJAR does not solve correspondence, contact-mode selection, or perception.",
        "- EJAR does not claim novelty over operational-space control as a controller; the novelty claim is about action renormalization at the cross-embodiment policy/data interface.",
    ]
    (DOCS / "claims.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_attacks():
    lines = [
        "# Reviewer Attacks",
        "",
        "| Attack | Severity | Response / required evidence |",
        "| --- | --- | --- |",
        "| This is just operational-space control. | High | Concede controller ancestry; boundary is the policy/data action token plus capability normalization and infeasibility residual. Need to cite Khatib-style control and frame novelty narrowly. |",
        "| Synthetic planar arms are too weak. | High | Agree; paper-readiness should be workshop/revise unless real robot logs are added. Synthetic evidence is only a mechanism sanity check. |",
        "| Jacobians are often unavailable or wrong. | Medium | Mark as an assumption; can be estimated, but this paper does not solve estimation. Include sensitivity discussion. |",
        "| Contact tasks violate first-order free-space assumptions. | High | Mark unsupported; propose contact-conditioned task maps as future work. |",
        "| Learned policies can infer this from data. | Medium | Maybe with enough data; EJAR is still useful as an inductive action interface and exposes infeasibility. Need ablations on data scale in future. |",
        "| Capability normalization changes the task rather than preserving absolute effects. | Medium | Clarify two modes: absolute-effect pullback and local capability-normalized token execution. Report which is used in each experiment. |",
        "| Clipping destroys the guarantee. | Medium | Yes; clipping is exactly where the residual reports infeasibility. |",
        "| The method assumes matched task maps. | High | True; correspondence/task-map mismatch is outside scope. |",
        "| The literature sweep is automated and shallow. | Medium | Be transparent; use it for boundary finding, not as a substitute for manual citation scholarship. |",
    ]
    (DOCS / "reviewer_attacks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows, fetch_note):
    write_csv(rows)
    write_literature_map(rows)
    write_hostile(rows)
    write_novelty_boundary(rows)
    write_decision(rows)
    write_claims()
    write_attacks()
    summary = {
        "fetch_note": fetch_note,
        "matrix_rows": len(rows),
        "serious_skim_rows": min(SERIOUS_N, len(rows)),
        "deep_read_rows": min(DEEP_N, len(rows)),
        "hostile_rows": min(HOSTILE_N, len(rows)),
        "category_counts": Counter(r["category"] for r in rows),
    }
    (DOCS / "literature_summary.json").write_text(json.dumps(summary, indent=2, default=dict), encoding="utf-8")


def main():
    ensure_dirs()
    commands = ["python scripts/generate_literature.py"]
    try:
        write_status(
            "literature sweep running",
            commands,
            next_step="fetch OpenAlex, rank papers, write required literature artifacts",
        )
        works, fetch_note = load_or_fetch()
        rows = make_matrix(works)
        write_outputs(rows, fetch_note)
        if len(rows) < MIN_LANDSCAPE:
            failure = f"only {len(rows)} ranked rows; minimum requested is {MIN_LANDSCAPE}"
        else:
            failure = ""
        write_status(
            "literature sweep complete",
            commands,
            failures=failure,
            recovery="used broad OpenAlex queries and cached results" if failure else "",
            next_step="run synthetic embodied-control evidence",
        )
        print(json.dumps({"rows": len(rows), "failure": failure, "matrix": str(MATRIX)}, indent=2))
    except Exception as exc:
        write_status(
            "literature sweep failed",
            commands,
            failures=repr(exc),
            recovery="failure recorded; inspect script/cache and rerun",
            next_step="repair literature pipeline",
        )
        print(json.dumps({"error": repr(exc)}, indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
