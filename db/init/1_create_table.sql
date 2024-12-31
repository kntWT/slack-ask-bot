CREATE DATABASE IF NOT EXISTS slack_ask_bot_db;

USE slack_ask_bot_db;

CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    channel_id VARCHAR(255) NOT NULL,
    thread_ts VARCHAR(255) NOT NULL,
    question VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    dm_id VARCHAR(255) NOT NULL,
    tags VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FULLTEXT question_index (question) WITH PARSER ngram,
    FULLTEXT tags_index (tags)
);
