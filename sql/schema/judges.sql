CREATE TABLE IF NOT EXISTS judges (
    sample_id TEXT PRIMARY KEY,
    
    -- Judge 1
    judge_1_tone TEXT,
    judge_1_detailed TEXT,
    judge_1_grammar TEXT,
    judge_1_structure TEXT,
    judge_1_content TEXT,
    
    -- Judge 2
    judge_2_tone TEXT,
    judge_2_detailed TEXT,
    judge_2_grammar TEXT,
    judge_2_structure TEXT,
    judge_2_content TEXT,
    
    -- Judge 3
    judge_3_tone TEXT,
    judge_3_detailed TEXT,
    judge_3_grammar TEXT,
    judge_3_structure TEXT,
    judge_3_content TEXT,
    
    -- Timestamps
    created_ts TIMESTAMP,
    modified_ts TIMESTAMP
);
