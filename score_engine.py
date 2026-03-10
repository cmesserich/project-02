# score_engine.py
# Connects to the Project 01 PostGIS database and rescores cities
# using custom weights from the survey.
# v2 — now weights sub-subindices directly for real score separation.

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Maps each top-level subindex to its constituent sub-subindex columns.
# Weights passed in from the survey (econ, lifestyle, etc.) are distributed
# equally across each subindex's children, then applied to the raw scores.
SUBINDEX_CHILDREN = {
    "econ":      ["econ_wealth", "econ_affordability", "econ_housing", "econ_inequality"],
    "lifestyle": ["lifestyle_food", "lifestyle_arts", "lifestyle_outdoor"],
    "community": ["community_capital", "community_civic", "community_equity"],
    "mobility":  ["mobility_commute", "mobility_transit", "mobility_housing"],
    "health":    ["health_air", "health_access", "health_outcomes"],
}

ALL_COLUMNS = [col for cols in SUBINDEX_CHILDREN.values() for col in cols]

def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)

def get_subindex_scores() -> pd.DataFrame:
    """
    Pulls sub-subindex scores for all metros from Project 01.
    Also pulls rolled-up subindex scores for display purposes only.
    """
    cols = ", ".join(f"ci.{c}" for c in ALL_COLUMNS)
    query = text(f"""
        SELECT
            ci.geo_id,
            m.name,
            ci.econ_score,
            ci.lifestyle_score,
            ci.community_score,
            ci.mobility_score,
            ci.health_score,
            {cols}
        FROM composite_index ci
        JOIN metros m ON ci.geo_id = m.cbsa_code
        WHERE ci.geo_level = 'metro'
    """)
    with get_engine().connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def rescore_cities(weights: dict) -> list:
    """
    Takes a weight vector keyed by subindex (econ, lifestyle, etc.)
    and rescores all cities using sub-subindex scores directly.

    Each subindex weight is distributed equally across its children.
    This means a high econ weight punishes Seattle specifically on
    econ_affordability (0.21) and econ_housing (0.32) rather than
    being absorbed by its strong econ_wealth (0.92).
    """
    df = get_subindex_scores()

    # Build per-column weights by distributing each subindex weight
    # equally across its children
    col_weights = {}
    for subindex, child_cols in SUBINDEX_CHILDREN.items():
        subindex_weight = weights.get(subindex, 0.2)
        per_child = subindex_weight / len(child_cols)
        for col in child_cols:
            col_weights[col] = per_child

    # Compute weighted score
    df["personalized_score"] = sum(
        df[col] * col_weights[col] for col in ALL_COLUMNS
    )

    # Normalize to 0-100
    min_score = df["personalized_score"].min()
    max_score = df["personalized_score"].max()
    if max_score > min_score:
        df["personalized_score"] = (
            (df["personalized_score"] - min_score) /
            (max_score - min_score) * 100
        ).round(1)
    else:
        df["personalized_score"] = 50.0

    df = df.sort_values("personalized_score", ascending=False)

    results = []
    for rank, (_, row) in enumerate(df.iterrows(), 1):
        results.append({
            "rank": rank,
            "name": row["name"],
            "geo_id": row["geo_id"],
            "personalized_score": row["personalized_score"],
            "econ_score":      round(float(row["econ_score"]), 3),
            "lifestyle_score": round(float(row["lifestyle_score"]), 3),
            "community_score": round(float(row["community_score"]), 3),
            "mobility_score":  round(float(row["mobility_score"]), 3),
            "health_score":    round(float(row["health_score"]), 3),
        })
    return results

def get_top_cities(weights: dict, n: int = 10) -> list:
    """Returns just the top N cities for a given weight vector."""
    return rescore_cities(weights)[:n]

if __name__ == "__main__":
    # Test 1 — cost-focused user (should hurt Seattle badly)
    cost_weights = {
        "econ": 0.6,
        "lifestyle": 0.1,
        "community": 0.1,
        "mobility": 0.1,
        "health": 0.1
    }
    print("Cost-focused user (should NOT be Seattle):")
    print("─" * 50)
    for city in get_top_cities(cost_weights):
        print(f"{city['rank']:2}. {city['name']:<35} {city['personalized_score']}")

    print()

    # Test 2 — nature/outdoor focused (Seattle might still appear but shouldn't dominate)
    outdoor_weights = {
        "econ": 0.1,
        "lifestyle": 0.5,
        "community": 0.1,
        "mobility": 0.1,
        "health": 0.2
    }
    print("Outdoor/lifestyle focused user:")
    print("─" * 50)
    for city in get_top_cities(outdoor_weights):
        print(f"{city['rank']:2}. {city['name']:<35} {city['personalized_score']}")