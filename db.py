# db.py
# Handles all reads and writes to the app schema in urbandb.
# ELI5: This is the filing cabinet. score_engine.py does the math,
# weight_mapper.py translates answers — this file saves and retrieves everything.
#
# Public functions:
#   create_session()              → creates a new session, returns session_id (UUID)
#   save_response(...)            → saves a completed survey/LLM response
#   get_results(session_id)       → retrieves full dashboard data for a session
#   reset_session(session_id)     → creates a new session chained to the old one
#   touch_session(session_id)     → updates last_active_at timestamp

import os
import json
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# ENGINE
# ─────────────────────────────────────────────

def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)


# ─────────────────────────────────────────────
# SESSION MANAGEMENT
# ─────────────────────────────────────────────

def create_session(user_type: str = "consumer") -> str:
    """
    Creates a new session row and returns the UUID as a string.
    This UUID becomes the permalink for the user's results dashboard.
    ELI5: Think of this as handing someone a ticket number when they walk in.
    """
    session_id = str(uuid.uuid4())
    query = text("""
        INSERT INTO app.sessions (id, user_type)
        VALUES (:id, :user_type)
    """)
    with get_engine().begin() as conn:
        conn.execute(query, {"id": session_id, "user_type": user_type})
    return session_id


def touch_session(session_id: str) -> None:
    """
    Updates last_active_at to now.
    Call this whenever a user interacts with their dashboard.
    """
    query = text("""
        UPDATE app.sessions
        SET last_active_at = NOW()
        WHERE id = :session_id
    """)
    with get_engine().begin() as conn:
        conn.execute(query, {"session_id": session_id})


def reset_session(session_id: str) -> str:
    """
    Creates a new session linked to the old one via previous_session_id.
    Old session and its responses are preserved — never deleted.
    Returns the new session_id.
    ELI5: Starting a fresh page in the same notebook.
    """
    # Increment reset_count on old session
    update_query = text("""
        UPDATE app.sessions
        SET reset_count = reset_count + 1
        WHERE id = :session_id
    """)
    # Create new session chained to old one
    insert_query = text("""
        INSERT INTO app.sessions (id, user_type, previous_session_id)
        SELECT :new_id, user_type, :old_id
        FROM app.sessions
        WHERE id = :old_id
    """)
    new_session_id = str(uuid.uuid4())
    with get_engine().begin() as conn:
        conn.execute(update_query, {"session_id": session_id})
        conn.execute(insert_query, {
            "new_id": new_session_id,
            "old_id": session_id
        })
    return new_session_id


def session_exists(session_id: str) -> bool:
    """Returns True if a session with this UUID exists."""
    query = text("""
        SELECT 1 FROM app.sessions WHERE id = :session_id
    """)
    with get_engine().connect() as conn:
        result = conn.execute(query, {"session_id": session_id}).fetchone()
    return result is not None


# ─────────────────────────────────────────────
# SAVING RESPONSES
# ─────────────────────────────────────────────

def save_response(
    session_id: str,
    raw_answers: dict,
    weight_vector: dict,
    top_recommendations: list,
    input_method: str = "survey",
    llm_transcript: Optional[list] = None,
    consent_to_data_use: bool = False,
    consent_to_marketing: bool = False
) -> int:
    """
    Saves a completed survey or LLM conversation response.
    Returns the new response row id.

    Args:
        session_id:           UUID string from create_session()
        raw_answers:          Dict of question_id → answer, exactly as submitted
        weight_vector:        Normalized weight dict from weight_mapper.py
                              e.g. {"econ_wealth": 0.12, "lifestyle_food": 0.08, ...}
        top_recommendations:  List of ranked city dicts from score_engine.py,
                              enriched with raw_stats and stat_percentiles
        input_method:         'survey' or 'llm'
        llm_transcript:       List of {role, content, timestamp} dicts (LLM path only)
        consent_to_data_use:  User opted in to data use
        consent_to_marketing: User opted in to marketing

    ELI5: Writes everything we know about this user's session into one row
    so we can reconstruct their full dashboard at any point in the future.
    """
    if input_method not in ("survey", "llm"):
        raise ValueError(f"input_method must be 'survey' or 'llm', got '{input_method}'")

    query = text("""
        INSERT INTO app.survey_responses (
            session_id,
            input_method,
            raw_answers,
            weight_vector,
            top_recommendations,
            llm_transcript,
            consent_to_data_use,
            consent_to_marketing
        ) VALUES (
            :session_id,
            :input_method,
            :raw_answers,
            :weight_vector,
            :top_recommendations,
            :llm_transcript,
            :consent_to_data_use,
            :consent_to_marketing
        )
        RETURNING id
    """)
    with get_engine().begin() as conn:
        result = conn.execute(query, {
            "session_id":            session_id,
            "input_method":          input_method,
            "raw_answers":           json.dumps(raw_answers),
            "weight_vector":         json.dumps(weight_vector),
            "top_recommendations":   json.dumps(top_recommendations),
            "llm_transcript":        json.dumps(llm_transcript) if llm_transcript else None,
            "consent_to_data_use":   consent_to_data_use,
            "consent_to_marketing":  consent_to_marketing
        })
        row_id = result.fetchone()[0]

    # Update session activity
    touch_session(session_id)
    return row_id


# ─────────────────────────────────────────────
# READING RESULTS
# ─────────────────────────────────────────────

def get_results(session_id: str) -> Optional[dict]:
    """
    Retrieves the full dashboard payload for a given session.
    Returns None if session doesn't exist or has no responses yet.

    Returns a dict with:
        session_id, created_at, input_method,
        weight_vector, top_recommendations, raw_answers
    ELI5: Given a ticket number, pull up everything we stored for that person.
    """
    query = text("""
        SELECT
            sr.id               AS response_id,
            sr.session_id,
            sr.created_at,
            sr.input_method,
            sr.raw_answers,
            sr.weight_vector,
            sr.top_recommendations,
            s.reset_count,
            s.user_type
        FROM app.survey_responses sr
        JOIN app.sessions s ON sr.session_id = s.id
        WHERE sr.session_id = :session_id
        ORDER BY sr.created_at DESC
        LIMIT 1
    """)
    with get_engine().connect() as conn:
        row = conn.execute(query, {"session_id": session_id}).fetchone()

    if row is None:
        return None

    return {
        "response_id":        row.response_id,
        "session_id":         str(row.session_id),
        "created_at":         row.created_at.isoformat(),
        "input_method":       row.input_method,
        "user_type":          row.user_type,
        "reset_count":        row.reset_count,
        "raw_answers":        row.raw_answers,
        "weight_vector":      row.weight_vector,
        "top_recommendations": row.top_recommendations
    }


def get_session_history(session_id: str) -> list:
    """
    Walks the chain of sessions linked by previous_session_id.
    Returns all responses across all sessions in reverse chronological order.
    ELI5: Shows everything someone has ever done, including past resets.
    """
    query = text("""
        WITH RECURSIVE session_chain AS (
            SELECT id, previous_session_id, created_at, reset_count
            FROM app.sessions
            WHERE id = :session_id

            UNION ALL

            SELECT s.id, s.previous_session_id, s.created_at, s.reset_count
            FROM app.sessions s
            JOIN session_chain sc ON s.id = sc.previous_session_id
        )
        SELECT
            sr.session_id,
            sr.created_at,
            sr.input_method,
            sr.weight_vector,
            sr.top_recommendations
        FROM app.survey_responses sr
        JOIN session_chain sc ON sr.session_id = sc.id
        ORDER BY sr.created_at DESC
    """)
    with get_engine().connect() as conn:
        rows = conn.execute(query, {"session_id": session_id}).fetchall()

    return [
        {
            "session_id":         str(r.session_id),
            "created_at":         r.created_at.isoformat(),
            "input_method":       r.input_method,
            "weight_vector":      r.weight_vector,
            "top_recommendations": r.top_recommendations
        }
        for r in rows
    ]


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("Running db.py smoke test...")
    print("─" * 50)

    # 1. Create a session
    sid = create_session()
    print(f"✓ Created session: {sid}")

    # 2. Confirm it exists
    assert session_exists(sid), "Session not found after creation"
    print(f"✓ Session exists: True")

    # 3. Save a mock response
    mock_answers = {"q1": "remote_work", "q2": ["coffee", "trails"], "q3": "rent"}
    mock_weights = {
        "econ_wealth": 0.05, "econ_affordability": 0.18, "econ_inequality": 0.04,
        "econ_housing": 0.12, "lifestyle_food": 0.10, "lifestyle_arts": 0.04,
        "lifestyle_outdoor": 0.14, "community_capital": 0.06, "community_civic": 0.04,
        "community_equity": 0.04, "mobility_commute": 0.08, "mobility_transit": 0.06,
        "health_air": 0.05, "health_access": 0.05, "health_outcomes": 0.05
    }
    mock_recommendations = [
        {
            "rank": 1, "cbsa_code": "42660", "name": "Seattle, WA",
            "composite_score": 100.0,
            "sub_scores": {"econ": 94.2, "lifestyle": 98.1, "community": 87.3,
                           "mobility": 96.0, "health": 91.5},
            "raw_stats": {"poi_cafe_density": 4.2, "poi_trail_density": 3.8},
            "stat_percentiles": {"poi_cafe_density": 89, "poi_trail_density": 91}
        }
    ]

    response_id = save_response(
        session_id=sid,
        raw_answers=mock_answers,
        weight_vector=mock_weights,
        top_recommendations=mock_recommendations,
        consent_to_data_use=True
    )
    print(f"✓ Saved response, row id: {response_id}")

    # 4. Retrieve results
    results = get_results(sid)
    assert results is not None
    assert results["top_recommendations"][0]["name"] == "Seattle, WA"
    print(f"✓ Retrieved results, top city: {results['top_recommendations'][0]['name']}")

    # 5. Reset session
    new_sid = reset_session(sid)
    print(f"✓ Reset session, new id: {new_sid}")
    assert session_exists(new_sid)
    assert new_sid != sid
    print(f"✓ New session exists and differs from old")

    # 6. History walk
    history = get_session_history(new_sid)
    print(f"✓ Session history entries visible from new session: {len(history)}")

    print("─" * 50)
    print("All checks passed.")
