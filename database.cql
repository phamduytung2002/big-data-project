-- Create keyspace
CREATE KEYSPACE IF NOT EXISTS topic_keyspace2
WITH replication = {'class':'SimpleStrategy', 'replication_factor':1};

-- Use keyspace
USE topic_keyspace;

-- Create table for articles
CREATE TABLE IF NOT EXISTS article (
    id INT PRIMARY KEY,
    author TEXT,
    title TEXT,
    url TEXT,
    source TEXT,
    topic INT
);

-- Create table for source count
CREATE TABLE IF NOT EXISTS source_count (
    window TIMESTAMP,
    source TEXT PRIMARY KEY,
    count INT
);

-- Create table for trending word count
CREATE TABLE IF NOT EXISTS trending_word_count (
    window TIMESTAMP,
    word TEXT PRIMARY KEY,
    count INT
);

-- Create table for total word count
CREATE TABLE IF NOT EXISTS total_word_count (
    word TEXT PRIMARY KEY,
    count INT
);

-- Insert sample data
INSERT INTO article (id, author, title, url, source, topic)
VALUES (1, 'authorr', 'titlee', 'https://www.google.com/', 'google', 0);

INSERT INTO source_count (window, source, count)
VALUES (dateof(now()), 'google', 1);

INSERT INTO trending_word_count (window, word, count)
VALUES (dateof(now()), 'hello', 1);

INSERT INTO total_word_count (word, count)
VALUES ('hello', 1);
