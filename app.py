# app.py
# FastAPI backend for Touchgrass.
# ELI5: This is the switchboard. It receives requests from the browser,
# calls the right modules in the right order, and sends back the right data.
#
# Routes:
#   GET  /                        → survey landing page
#   POST /submit                  → process survey, save response, redirect to results
#   GET  /results/{session_id}    → results dashboard page
#   POST /reset/{session_id}      → reset session, redirect to new survey
#   GET  /api/results/{session_id}→ raw JSON results (for dashboard JS)
#   GET  /api/city/{cbsa_code}    → full raw stats for a single city
#   POST /api/summary             → streams AI summary via SSE (proxies Anthropic API)
#   POST /api/rescore             → re-scores cities with custom weights (sliders)
#   POST /api/send-link           → emails results link to user

import os
import json
from typing import Optional

import httpx
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from weight_mapper import map_weights
from score_engine import get_top_cities
import db

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# ─────────────────────────────────────────────
# DB ENGINE (for enrichment queries)
# ─────────────────────────────────────────────

def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)


# ─────────────────────────────────────────────
# STAT ENRICHMENT
# Maps each subindex to the raw stat columns most relevant to it.
# Used to filter which stats we surface per user based on their weights.
# ─────────────────────────────────────────────

SUBINDEX_STAT_MAP = {
    "econ": {
        "table": "economic_health",
        "columns": [
            "median_household_income", "per_capita_income", "cost_of_living_index",
            "median_home_value", "median_gross_rent", "rent_to_income_ratio",
            "unemployment_rate", "job_growth_yoy", "homeownership_rate"
        ]
    },
    "lifestyle": {
        "table": "lifestyle_amenities",
        "columns": [
            "poi_restaurant_density", "poi_bar_density", "poi_cafe_density",
            "poi_grocery_density", "poi_farmers_market_density", "poi_bookstore_density",
            "poi_museum_density", "poi_music_venue_density", "poi_theater_density",
            "poi_park_density", "poi_trail_density", "poi_coworking_density"
        ]
    },
    "community": {
        "table": "community_civic",
        "columns": [
            "voter_participation_rate", "nonprofit_density", "pct_bachelors_or_higher",
            "school_quality_index", "diversity_index", "median_age"
        ]
    },
    "mobility": {
        "table": "mobility_access",
        "columns": [
            "transit_stop_density", "transit_route_density", "avg_commute_time_min",
            "pct_drive_alone", "bike_infrastructure_score", "bike_lane_density",
            "pct_public_transit", "pct_walk_or_bike", "pct_no_vehicle"
        ]
    },
    "health": {
        "table": "health_wellness",
        "columns": [
            "avg_aqi", "green_space_per_capita_sqm", "walkability_score",
            "poi_gym_density", "poi_hospital_density", "health_insurance_coverage_rate",
            "obesity_rate", "physical_inactivity_rate", "mental_health_poor_days"
        ]
    }
}

STAT_LABELS = {
    "median_household_income":        "Median Household Income",
    "per_capita_income":              "Per Capita Income",
    "cost_of_living_index":           "Cost of Living Index",
    "median_home_value":              "Median Home Value",
    "median_gross_rent":              "Median Gross Rent",
    "rent_to_income_ratio":           "Rent-to-Income Ratio",
    "unemployment_rate":              "Unemployment Rate",
    "job_growth_yoy":                 "Job Growth (YoY)",
    "homeownership_rate":             "Homeownership Rate",
    "poi_restaurant_density":         "Restaurant Density",
    "poi_bar_density":                "Bar Density",
    "poi_cafe_density":               "Café Density",
    "poi_grocery_density":            "Grocery Store Density",
    "poi_farmers_market_density":     "Farmers Market Density",
    "poi_bookstore_density":          "Bookstore Density",
    "poi_museum_density":             "Museum Density",
    "poi_music_venue_density":        "Music Venue Density",
    "poi_theater_density":            "Theater Density",
    "poi_park_density":               "Park Density",
    "poi_trail_density":              "Trail Density",
    "poi_coworking_density":          "Coworking Space Density",
    "voter_participation_rate":       "Voter Participation Rate",
    "nonprofit_density":              "Nonprofit Density",
    "pct_bachelors_or_higher":        "Bachelor's Degree or Higher",
    "school_quality_index":           "School Quality Index",
    "diversity_index":                "Diversity Index",
    "median_age":                     "Median Age",
    "transit_stop_density":           "Transit Stop Density",
    "transit_route_density":          "Transit Route Density",
    "avg_commute_time_min":           "Avg Commute Time (min)",
    "pct_drive_alone":                "Drive Alone Rate",
    "bike_infrastructure_score":      "Bike Infrastructure Score",
    "bike_lane_density":              "Bike Lane Density",
    "pct_public_transit":             "Public Transit Usage",
    "pct_walk_or_bike":               "Walk or Bike Rate",
    "pct_no_vehicle":                 "Households Without a Car",
    "walkability_score":              "Walkability Score",
    "avg_aqi":                        "Air Quality Index (lower = better)",
    "green_space_per_capita_sqm":     "Green Space per Capita (sqm)",
    "poi_gym_density":                "Gym Density",
    "poi_hospital_density":           "Hospital Density",
    "health_insurance_coverage_rate": "Health Insurance Coverage Rate",
    "obesity_rate":                   "Obesity Rate",
    "physical_inactivity_rate":       "Physical Inactivity Rate",
    "mental_health_poor_days":        "Avg Poor Mental Health Days/Month",
}


def get_relevant_columns(weight_vector: dict, top_n_subindices: int = 3) -> dict:
    """
    Returns stat columns for the user's top N weighted subindices only.
    ELI5: If someone cares most about mobility and lifestyle, only return
    transit/bike stats and restaurant/cafe stats — not healthcare data.
    """
    sorted_subindices = sorted(weight_vector.items(), key=lambda x: x[1], reverse=True)
    top_subindices = [s for s, _ in sorted_subindices[:top_n_subindices]]
    return {s: SUBINDEX_STAT_MAP[s] for s in top_subindices if s in SUBINDEX_STAT_MAP}


def fetch_raw_stats(cbsa_codes: list, relevant_columns: dict) -> dict:
    """
    Queries public schema raw tables for given cities and columns.
    Calculates percentile rank for each stat vs all 50 metros.
    Returns dict keyed by cbsa_code.
    """
    engine = get_engine()
    stats_by_city = {code: {"raw": {}, "percentiles": {}} for code in cbsa_codes}

    for subindex, config in relevant_columns.items():
        table = config["table"]
        columns = config["columns"]
        col_list = ", ".join(columns)
        placeholders = ", ".join([f"'{code}'" for code in cbsa_codes])

        city_query = text(f"""
            SELECT geo_id, {col_list}
            FROM public.{table}
            WHERE geo_id IN ({placeholders})
            AND geo_level = 'metro'
        """)

        all_query = text(f"""
            SELECT geo_id, {col_list}
            FROM public.{table}
            WHERE geo_level = 'metro'
        """)

        with engine.connect() as conn:
            city_rows = conn.execute(city_query).fetchall()
            all_rows = conn.execute(all_query).fetchall()

        # Build all-metro value lists for percentile calculation
        all_values = {col: [] for col in columns}
        for row in all_rows:
            row_dict = row._mapping
            for col in columns:
                val = row_dict.get(col)
                if val is not None:
                    all_values[col].append(float(val))

        for row in city_rows:
            row_dict = row._mapping
            geo_id = row_dict["geo_id"]
            if geo_id not in stats_by_city:
                continue
            for col in columns:
                val = row_dict.get(col)
                if val is None:
                    continue
                val = float(val)
                stats_by_city[geo_id]["raw"][col] = val
                stats_by_city[geo_id]["raw"][f"{col}_label"] = STAT_LABELS.get(col, col)

                col_vals = sorted(all_values[col])
                if col_vals:
                    rank = sum(1 for v in col_vals if v <= val)
                    stats_by_city[geo_id]["percentiles"][col] = round((rank / len(col_vals)) * 100)

    return stats_by_city


def enrich_recommendations(cities: list, weight_vector: dict) -> list:
    """
    Merges scored cities from score_engine with raw stats from public schema.
    Returns full payload ready to store and render.
    """
    cbsa_codes = [c["geo_id"] for c in cities]
    relevant_columns = get_relevant_columns(weight_vector)
    raw_stats = fetch_raw_stats(cbsa_codes, relevant_columns)

    enriched = []
    for city in cities:
        geo_id = city["geo_id"]
        city_stats = raw_stats.get(geo_id, {"raw": {}, "percentiles": {}})
        enriched.append({
            "rank":             city["rank"],
            "cbsa_code":        geo_id,
            "name":             city["name"],
            "composite_score":  city["personalized_score"],
            "sub_scores": {
                "econ":      round(city["econ_score"] * 100, 1),
                "lifestyle": round(city["lifestyle_score"] * 100, 1),
                "community": round(city["community_score"] * 100, 1),
                "mobility":  round(city["mobility_score"] * 100, 1),
                "health":    round(city["health_score"] * 100, 1)
            },
            "raw_stats":        city_stats["raw"],
            "stat_percentiles": city_stats["percentiles"]
        })
    return enriched


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def survey_page(request: Request):
    """Survey landing page."""
    from survey_config import QUESTIONS
    return templates.TemplateResponse("index.html", {
        "request":   request,
        "questions": QUESTIONS
    })


@app.post("/submit")
async def submit_survey(request: Request):
    """
    Full pipeline on survey submission:
    parse → weight → score → enrich → save → redirect
    """
    form_data = await request.form()
    from survey_config import QUESTIONS

    responses = {}
    for question in QUESTIONS:
        qid = question["id"]
        if question["type"] == "forced":
            val = form_data.get(f"q_{qid}")
            if val is not None:
                responses[qid] = int(val)
        elif question["type"] == "ranked":
            val = form_data.get(f"q_{qid}_rank")
            if val is not None:
                responses[qid] = [int(x) for x in val.split(",")]

    consent_data       = bool(form_data.get("consent_to_data_use"))
    consent_marketing  = bool(form_data.get("consent_to_marketing"))

    weight_vector  = map_weights(responses)
    scored_cities  = get_top_cities(weight_vector, n=10)
    enriched       = enrich_recommendations(scored_cities, weight_vector)

    session_id = db.create_session()
    db.save_response(
        session_id=session_id,
        raw_answers={str(k): v for k, v in responses.items()},
        weight_vector=weight_vector,
        top_recommendations=enriched,
        input_method="survey",
        consent_to_data_use=consent_data,
        consent_to_marketing=consent_marketing
    )

    return RedirectResponse(url=f"/results/{session_id}", status_code=303)


@app.get("/results/{session_id}", response_class=HTMLResponse)
async def results_page(request: Request, session_id: str):
    """Results dashboard — reconstructed entirely from stored data."""
    if not db.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    results = db.get_results(session_id)
    if results is None:
        return RedirectResponse(url="/")

    db.touch_session(session_id)

    return templates.TemplateResponse("results.html", {
        "request":    request,
        "session_id": session_id,
        "results":    results
    })


@app.post("/reset/{session_id}")
async def reset_session(session_id: str):
    """Resets a session, preserving old data, redirects to fresh survey."""
    if not db.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    db.reset_session(session_id)
    return RedirectResponse(url="/", status_code=303)


@app.get("/api/results/{session_id}")
async def api_results(session_id: str):
    """
    JSON endpoint for the results dashboard.
    Called by frontend JS to render charts without a full page reload.
    """
    if not db.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    results = db.get_results(session_id)
    if results is None:
        raise HTTPException(status_code=404, detail="No results for this session")
    return JSONResponse(content=results)


@app.get("/api/city/{cbsa_code}")
async def api_city(cbsa_code: str, subindex: Optional[str] = None):
    """
    Full raw stats for a single city.
    Called when user clicks into a city on the dashboard for deeper detail.
    Optional: ?subindex=lifestyle to filter to one category.
    """
    engine = get_engine()

    if subindex and subindex not in SUBINDEX_STAT_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown subindex: {subindex}")

    tables_to_query = (
        {subindex: SUBINDEX_STAT_MAP[subindex]}
        if subindex
        else SUBINDEX_STAT_MAP
    )

    metro_query = text("SELECT name FROM public.metros WHERE cbsa_code = :cbsa_code")
    with engine.connect() as conn:
        metro = conn.execute(metro_query, {"cbsa_code": cbsa_code}).fetchone()
    if metro is None:
        raise HTTPException(status_code=404, detail=f"City not found: {cbsa_code}")

    city_data = {"cbsa_code": cbsa_code, "name": metro.name, "stats": {}}

    for idx, config in tables_to_query.items():
        table   = config["table"]
        columns = config["columns"]
        col_list = ", ".join(columns)

        query = text(f"""
            SELECT {col_list}
            FROM public.{table}
            WHERE geo_id = :cbsa_code AND geo_level = 'metro'
        """)
        with engine.connect() as conn:
            row = conn.execute(query, {"cbsa_code": cbsa_code}).fetchone()

        if row:
            row_dict = row._mapping
            city_data["stats"][idx] = {
                col: {
                    "value": float(row_dict[col]) if row_dict[col] is not None else None,
                    "label": STAT_LABELS.get(col, col)
                }
                for col in columns
            }

    return JSONResponse(content=city_data)


@app.post("/api/summary")
async def api_summary(request: Request):
    """
    Streams an AI-generated summary explaining why the top city matches the user.
    Proxies the Anthropic API server-side so the API key is never exposed to the browser.
    Returns a text/event-stream (SSE) response the frontend reads chunk by chunk.

    TODO (Project 03): persist the generated summary text to app.survey_responses
    alongside the chat transcript once the LLM conversation interface is built.
    The session_id is available in the request body for that hookup.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    body = await request.json()
    prompt = body.get("prompt", "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing prompt")

    session_id = body.get("session_id", "unknown")
    print(f"[/api/summary] Streaming summary for session {session_id}")

    async def stream_anthropic():
        """
        Opens a streaming connection to Anthropic and yields each SSE chunk
        straight through to the browser. Frontend parser is unchanged —
        it sees the same event format as if it called Anthropic directly.
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key":         api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type":      "application/json",
                },
                json={
                    "model":      "claude-sonnet-4-20250514",
                    "max_tokens": 300,
                    "stream":     True,
                    "messages":   [{"role": "user", "content": prompt}],
                },
            ) as resp:
                if resp.status_code != 200:
                    error_body = await resp.aread()
                    print(f"[/api/summary] Anthropic error {resp.status_code}: {error_body}")
                    yield f"data: {json.dumps({'type': 'error', 'message': str(resp.status_code)})}\n\n"
                    return

                async for line in resp.aiter_lines():
                    if line:
                        print(f"[/api/summary] chunk: {line}")
                        yield f"{line}\n\n"

    return StreamingResponse(
        stream_anthropic(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":      "no-cache",
            "X-Accel-Buffering":  "no",  # prevents nginx buffering the stream
        },
    )


@app.post("/api/send-link")
async def api_send_link(request: Request):
    """
    Emails the user a link back to their results.
    Stores the email against the session for reference.
    Email sending is stubbed — swap in SendGrid/Resend/etc when ready.
    """
    body = await request.json()
    email   = body.get("email", "").strip()
    session_id = body.get("session_id", "").strip()
    url     = body.get("url", "").strip()

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email")
    if not session_id or not url:
        raise HTTPException(status_code=400, detail="Missing session_id or url")

    # Store email in session metadata for reference
    try:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE app.sessions
                    SET metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object('email', :email)
                    WHERE id = :session_id
                """),
                {"email": email, "session_id": session_id}
            )
    except Exception as e:
        print(f"[send-link] DB update failed: {e}")

    # ── EMAIL STUB ──
    # Replace this block with your email provider when ready.
    # Example (SendGrid):
    #   import sendgrid
    #   sg = sendgrid.SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])
    #   sg.client.mail.send.post(request_body={...})
    print(f"[send-link] Would send to {email}: {url}")

    return JSONResponse(content={"ok": True})



async def api_rescore(request: Request):
    """
    Re-score all cities with a custom weight vector supplied by the frontend.
    Returns the full ranked list with new composite + sub scores.
    Called when user adjusts sliders on the results page.
    """
    body = await request.json()
    raw_weights = body.get("weights", {})

    # Validate keys
    allowed = {"econ", "lifestyle", "community", "mobility", "health"}
    if not raw_weights or not set(raw_weights.keys()) <= allowed:
        raise HTTPException(status_code=400, detail="Invalid weight keys")

    # Normalize to sum exactly 1.0
    total = sum(float(v) for v in raw_weights.values())
    if total <= 0:
        raise HTTPException(status_code=400, detail="Weights must sum to > 0")

    weights = {k: float(v) / total for k, v in raw_weights.items()}

    from score_engine import rescore_cities
    cities = rescore_cities(weights)

    rankings = []
    for city in cities:
        rankings.append({
            "rank":            city["rank"],
            "cbsa_code":       city["geo_id"],
            "name":            city["name"],
            "composite_score": city["personalized_score"],
            "sub_scores": {
                "econ":      round(city["econ_score"] * 100, 1),
                "lifestyle": round(city["lifestyle_score"] * 100, 1),
                "community": round(city["community_score"] * 100, 1),
                "mobility":  round(city["mobility_score"] * 100, 1),
                "health":    round(city["health_score"] * 100, 1)
            }
        })

    return JSONResponse(content={"rankings": rankings})


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=True)