CREATE TABLE IF NOT EXISTS samples (
    sample_id TEXT PRIMARY KEY,
    essay_text TEXT,
    grade_level TEXT,
    subject TEXT,
    prompt TEXT,
    grammar_level TEXT,
    flow_level TEXT,
    content_level TEXT,
    created_ts TIMESTAMP,
    modified_ts TIMESTAMP
);
