CREATE TABLE IF NOT EXISTS samples (
    sample_id TEXT PRIMARY KEY,
    essay_text LONGTEXT,
    grade_level TEXT,
    subject TEXT,
    prompt TEXT,
    grammar_level TEXT,
    flow_level TEXT,
    content_level TEXT,
    created_ts DATETIME,
    modified_ts DATETIME
);
