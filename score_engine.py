# score_engine.py
# Connects to the Project 01 PostGIS database and rescores cities
# using custom weights from the survey.
# ELI5: Project 01 scored every city equally weighted.
# This file rescores them based on what YOU care about.

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)

def get_subindex_scores() -> pd.DataFrame:
    """
    Pulls the subindex scores for all metros from Project 01.
    ELI5: Gets the raw scores for each city across all 5 dimensions
    so we can reweight them based on user preferences.
    """
    query = text("""
        SELECT
            ci.geo_id,
            m.name,
            ci.econ_score,
            ci.lifestyle_score,
            ci.community_score,
            ci.mobility_score,
            ci.health_score
        FROM composite_index ci
        JOIN metros m ON ci.geo_id = m.cbsa_code
        WHERE ci.geo_level = 'metro'
        ORDER BY ci.econ_score DESC
    """)
    with get_engine().connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def rescore_cities(weights: dict) -> list:
    """
    Takes a weight vector and rescores all cities.
    Returns a ranked list of cities with their personalized scores.
    ELI5: Instead of each subindex counting equally (20% each),
    we multiply each subindex by how much the user cares about it.
    A mobility-focused user makes transit scores count more.
    """
    df = get_subindex_scores()

    # Apply custom weights to each subindex
    df["personalized_score"] = (
        df["econ_score"]      * weights.get("econ", 0.2) +
        df["lifestyle_score"] * weights.get("lifestyle", 0.2) +
        df["community_score"] * weights.get("community", 0.2) +
        df["mobility_score"]  * weights.get("mobility", 0.2) +
        df["health_score"]    * weights.get("health", 0.2)
    ) / sum(weights.values())

    # Normalize to 0-100
    min_score = df["personalized_score"].min()
    max_score = df["personalized_score"].max()
    df["personalized_score"] = (
        (df["personalized_score"] - min_score) /
        (max_score - min_score) * 100
    ).round(1)

    # Sort by personalized score
    df = df.sort_values("personalized_score", ascending=False)

    # Return as list of dicts
    results = []
    for rank, (_, row) in enumerate(df.iterrows(), 1):
        results.append({
            "rank": rank,
            "name": row["name"],
            "geo_id": row["geo_id"],
            "personalized_score": row["personalized_score"],
            "econ_score": round(float(row["econ_score"]), 1),
            "lifestyle_score": round(float(row["lifestyle_score"]), 1),
            "community_score": round(float(row["community_score"]), 1),
            "mobility_score": round(float(row["mobility_score"]), 1),
            "health_score": round(float(row["health_score"]), 1)
        })
    return results

def get_top_cities(weights: dict, n: int = 10) -> list:
    """Returns just the top N cities for a given weight vector."""
    return rescore_cities(weights)[:n]

if __name__ == "__main__":
    # Test with mobility-focused weights
    test_weights = {
        "econ": 0.108,
        "lifestyle": 0.292,
        "community": 0.186,
        "mobility": 0.281,
        "health": 0.132
    }
    print("Top 10 cities for mobility + lifestyle focused user:")
    print("─" * 50)
    cities = get_top_cities(test_weights)
    for city in cities:
        print(f"{city['rank']:2}. {city['name']:<35} {city['personalized_score']:.1f}")