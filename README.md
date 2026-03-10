# Touchgrass — City Match Engine

A personalized city-finding tool. Take a short survey about what you value in a place to live, and get back a ranked list of US metro areas tailored to your priorities — with the data to back it up.

Built on top of the Project 01 urban data pipeline (49 quality-of-life variables across 50 metros).

**Live:** `http://[server]:8002`

---

## How It Works

1. User answers 12 survey questions about lifestyle priorities
2. `weight_mapper.py` converts answers into a normalized weight vector across 5 dimensions
3. `score_engine.py` re-ranks all 50 metros using those custom weights
4. `app.py` enriches the top 10 results with relevant raw stats and percentile rankings
5. An AI-generated narrative explains why the top city fits the user's profile
6. Results are saved to the DB and accessible via a permanent permalink URL

---

## Architecture

```
project-02/
├── survey_config.py      # All questions, options, and weight mappings
├── weight_mapper.py      # Converts survey answers → normalized weight vector
├── score_engine.py       # Queries project-01 DB, re-scores cities by custom weights
├── db.py                 # Session management and response persistence
├── app.py                # FastAPI backend — routes, enrichment, AI summary proxy
├── templates/
│   ├── index.html        # Survey UI
│   └── results.html      # Results dashboard
├── migrate_app_schema.sql # One-time DB schema setup
├── requirements.txt
└── .env.example
```

### Data Flow

```
Survey submit
  → weight_mapper   → weight vector
  → score_engine    → ranked cities (scores only)
  → app.py enriches → raw stats + percentiles per city
  → db.py saves     → session + full results payload stored
  → redirect        → /results/{session_id}

Results page
  → reads stored payload from DB (no re-scoring)
  → /api/summary streams AI narrative via Anthropic API
  → /api/rescore re-ranks with custom slider weights (live, not saved)
  → /api/city/{cbsa_code} returns full stats for any city on demand
```

---

## Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Survey landing page |
| POST | `/submit` | Process survey → redirect to results |
| GET | `/results/{session_id}` | Results dashboard (permanent URL) |
| POST | `/reset/{session_id}` | Reset session → redirect to fresh survey |
| GET | `/api/results/{session_id}` | JSON results payload |
| GET | `/api/city/{cbsa_code}` | Full raw stats for a single city |
| POST | `/api/summary` | Streams AI narrative (Anthropic proxy) |
| POST | `/api/rescore` | Re-ranks cities with custom weights |
| POST | `/api/send-link` | Stores email for session (send stub) |

---

## Setup

### Prerequisites
- Python 3.10+
- Access to the project-01 PostGIS database (`urbandb` on `192.168.68.51`)
- Anthropic API key (for AI summary)

### Install

```bash
git clone https://github.com/cmesserich/project-02
cd project-02
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# fill in .env with DB credentials and ANTHROPIC_API_KEY
```

### Database setup (first time only)

```bash
# Run against the project-01 PostGIS container
docker exec -i project01-postgis psql -U urban -d urbandb < migrate_app_schema.sql
```

### Run

```bash
uvicorn app:app --host 0.0.0.0 --port 8002 --reload
```

---

## Deployment (OptiPlex 7050)

```bash
# On server (192.168.68.52)
git clone https://github.com/cmesserich/project-02
cd project-02
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in credentials

# Run with systemd or nohup
nohup uvicorn app:app --host 0.0.0.0 --port 8002 &
```

---

## Project Roadmap

| # | Project | Status |
|---|---------|--------|
| 01 | Urban Data Pipeline | ✅ Complete |
| 02 | City Match Engine (this repo) | ✅ Active |
| 03 | LLM Conversation Interface | 🔜 Next |

Project 03 will add a chat-based entry point — same backend, same scoring engine, same results dashboard. The survey and LLM paths will produce identical output and share the same session/results infrastructure.
