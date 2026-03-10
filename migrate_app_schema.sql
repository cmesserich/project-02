-- =============================================================
-- CityScout App Schema Migration
-- Run against: urbandb on 192.168.68.51
-- Execute: docker exec -i project01-postgis psql -U urban -d urbandb < migrate_app_schema.sql
-- =============================================================

-- Create the app schema
CREATE SCHEMA IF NOT EXISTS app;

-- =============================================================
-- SESSIONS
-- One row per user. UUID is the permalink key.
-- Reset = new session, old session preserved.
-- =============================================================
CREATE TABLE IF NOT EXISTS app.sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    last_active_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    reset_count     INTEGER NOT NULL DEFAULT 0,
    previous_session_id UUID REFERENCES app.sessions(id),  -- chain of resets
    user_type       VARCHAR(20) NOT NULL DEFAULT 'consumer',
    -- future: enterprise_user_id INTEGER REFERENCES enterprise.users(id)
    metadata        JSONB  -- reserved for future use (device, referrer, etc.)
);

CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON app.sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_sessions_user_type ON app.sessions(user_type);

-- =============================================================
-- SURVEY RESPONSES
-- One row per completed survey or LLM conversation.
-- Stores everything needed to render the full dashboard
-- without re-querying public schema at render time.
-- =============================================================
CREATE TABLE IF NOT EXISTS app.survey_responses (
    id                  SERIAL PRIMARY KEY,
    session_id          UUID NOT NULL REFERENCES app.sessions(id),
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),

    -- How did the user generate this response?
    input_method        VARCHAR(10) NOT NULL DEFAULT 'survey'
                            CHECK (input_method IN ('survey', 'llm')),

    -- Raw survey answers exactly as submitted
    -- Shape: { "q1": "answer", "q2": ["a", "b"], ... }
    raw_answers         JSONB NOT NULL,

    -- LLM conversation transcript (null for survey path)
    -- Shape: [{ "role": "user"|"assistant", "content": "...", "timestamp": "..." }]
    llm_transcript      JSONB,

    -- Normalized weight vector output from weight_mapper.py
    -- Shape: { "econ_wealth": 0.12, "econ_affordability": 0.18, ... }
    weight_vector       JSONB NOT NULL,

    -- Top N ranked cities with full scoring context
    -- Stored at response time so dashboard is reproducible
    -- even if composite_index is updated later
    -- Shape: [
    --   {
    --     "rank": 1,
    --     "cbsa_code": "42660",
    --     "name": "Seattle, WA",
    --     "composite_score": 100.0,
    --     "sub_scores": {
    --       "econ": 94.2, "lifestyle": 98.1,
    --       "community": 87.3, "mobility": 96.0, "health": 91.5
    --     },
    --     "dimension_scores": {
    --       "econ_wealth": 88.0, "econ_affordability": 72.1, ...
    --     },
    --     "raw_stats": {
    --       "poi_cafe_density": 4.2,
    --       "poi_trail_density": 3.8,
    --       "bike_lane_density": 2.1,
    --       ...  (only stats relevant to user's weights)
    --     },
    --     "stat_percentiles": {
    --       "poi_cafe_density": 89,  (percentile rank vs all 50 metros)
    --       ...
    --     }
    --   },
    --   ...
    -- ]
    top_recommendations JSONB NOT NULL,

    -- Consent flags
    consent_to_data_use     BOOLEAN NOT NULL DEFAULT FALSE,
    consent_to_marketing    BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_survey_responses_session_id
    ON app.survey_responses(session_id);
CREATE INDEX IF NOT EXISTS idx_survey_responses_input_method
    ON app.survey_responses(input_method);
CREATE INDEX IF NOT EXISTS idx_survey_responses_created_at
    ON app.survey_responses(created_at);

-- =============================================================
-- VERIFICATION
-- =============================================================
SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema = 'app'
ORDER BY table_name;
