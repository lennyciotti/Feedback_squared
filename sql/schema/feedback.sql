CREATE TABLE IF NOT EXISTS feedback (
    sample_id TEXT PRIMARY KEY,
    high_level_feedback TEXT,
    comments TEXT,  -- JSON stored as TEXT
    created_ts TIMESTAMP,
    modified_ts TIMESTAMP
);
