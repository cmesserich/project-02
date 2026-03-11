# survey_diagnostic.py
# Enumerates every possible survey answer combination,
# computes the weight vector for each, scores all cities,
# and reports the full distribution of results.
#
# Run from the app directory:
#   python survey_diagnostic.py

import itertools
from collections import Counter
from weight_mapper import map_weights
from score_engine import get_subindex_scores, SUBINDEX_CHILDREN
from survey_config import QUESTIONS

ALL_COLUMNS = [col for cols in SUBINDEX_CHILDREN.values() for col in cols]

def rescore_in_memory(df, weights):
    """
    Rescores using a pre-fetched dataframe — no DB call.
    """
    col_weights = {}
    for subindex, child_cols in SUBINDEX_CHILDREN.items():
        subindex_weight = weights.get(subindex, 0.2)
        per_child = subindex_weight / len(child_cols)
        for col in child_cols:
            col_weights[col] = per_child

    df = df.copy()
    df["personalized_score"] = sum(
        df[col] * col_weights[col] for col in ALL_COLUMNS
    )

    min_score = df["personalized_score"].min()
    max_score = df["personalized_score"].max()
    if max_score > min_score:
        df["personalized_score"] = (
            (df["personalized_score"] - min_score) /
            (max_score - min_score) * 100
        )

    df = df.sort_values("personalized_score", ascending=False)
    return list(df["name"].values)


def run_diagnostic():
    print("Fetching city data once from DB...")
    df = get_subindex_scores()
    print(f"Loaded {len(df)} cities.\n")

    forced_questions = [q for q in QUESTIONS if q["type"] == "forced"]
    ranked_questions = [q for q in QUESTIONS if q["type"] == "ranked"]

    forced_ranges = [list(range(len(q["options"]))) for q in forced_questions]
    ranked_perms  = [list(itertools.permutations(range(len(q["options"])))) for q in ranked_questions]

    forced_combos = list(itertools.product(*forced_ranges))
    ranked_combos = list(itertools.product(*ranked_perms))

    total = len(forced_combos) * len(ranked_combos)
    print(f"Total possible answer combinations: {total:,}")
    print(f"  Forced question combos: {len(forced_combos):,}")
    print(f"  Ranked question permutations: {len(ranked_combos):,}")
    print("─" * 50)

    forced_qids = [q["id"] for q in forced_questions]
    ranked_qids  = [q["id"] for q in ranked_questions]

    top1_counter   = Counter()
    top3_counter   = Counter()
    weight_vectors = []

    count = 0
    for f_combo in forced_combos:
        for r_combo in ranked_combos:
            responses = {}
            for qid, answer in zip(forced_qids, f_combo):
                responses[qid] = answer
            for qid, perm in zip(ranked_qids, r_combo):
                responses[qid] = list(perm)

            weights = map_weights(responses)
            weight_vectors.append(weights)
            ranked = rescore_in_memory(df, weights)

            top1_counter[ranked[0]] += 1
            for city in ranked[:3]:
                top3_counter[city] += 1

            count += 1
            if count % 100000 == 0:
                print(f"  ...processed {count:,} / {total:,}")

    print(f"\n#1 CITY DISTRIBUTION (across {total:,} combinations):")
    print("─" * 50)
    for city, cnt in top1_counter.most_common():
        pct = cnt / total * 100
        bar = "█" * int(pct / 2)
        print(f"  {city:<35} {cnt:>7,} ({pct:5.1f}%)  {bar}")

    print(f"\nTOP 3 APPEARANCES:")
    print("─" * 50)
    for city, cnt in top3_counter.most_common(15):
        pct = cnt / total * 100
        print(f"  {city:<35} {cnt:>7,} ({pct:5.1f}%)")

    print(f"\nWEIGHT VECTOR RANGES:")
    print("─" * 50)
    for subindex in ["econ", "lifestyle", "community", "mobility", "health"]:
        vals = [w[subindex] for w in weight_vectors]
        print(f"  {subindex:<12} min: {min(vals):.4f}  max: {max(vals):.4f}  range: {max(vals)-min(vals):.4f}")

    all_cities = set(df["name"].values)
    never_top1 = all_cities - set(top1_counter.keys())
    print(f"\nCITIES THAT NEVER REACH #1 ({len(never_top1)} of {len(all_cities)}):")
    print("─" * 50)
    for city in sorted(never_top1):
        print(f"  {city}")


if __name__ == "__main__":
    run_diagnostic()