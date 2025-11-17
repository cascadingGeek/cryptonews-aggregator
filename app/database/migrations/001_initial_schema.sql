-- Create signal_items table
CREATE TABLE signal_items (
    id UUID PRIMARY KEY,
    signal TEXT NOT NULL,
    sentiment VARCHAR(20),
    sentiment_value FLOAT,
    timestamp FLOAT NOT NULL,
    feed_categories TEXT[],
    short_context TEXT,
    long_context TEXT,
    sources TEXT[],
    author VARCHAR(200),
    tokens TEXT[],
    tweet_url VARCHAR(500),
    narrative_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_timestamp_categories ON signal_items(timestamp, feed_categories);
CREATE INDEX idx_sentiment ON signal_items(sentiment);
CREATE INDEX idx_signal_timestamp ON signal_items(timestamp);
CREATE INDEX idx_signal_created ON signal_items(created_at);

-- Create category_feeds table
CREATE TABLE category_feeds (
    id UUID PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    items JSON NOT NULL,
    item_count INTEGER DEFAULT 0,
    last_updated FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_category ON category_feeds(category);
CREATE INDEX idx_category_updated ON category_feeds(category, last_updated);
CREATE INDEX idx_last_updated ON category_feeds(last_updated);

-- Create payment_transactions table
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY,
    payment_hash VARCHAR(200) UNIQUE NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    amount FLOAT NOT NULL,
    verified INTEGER DEFAULT 0,
    settled INTEGER DEFAULT 0,
    user_identifier VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    verified_at TIMESTAMP,
    settled_at TIMESTAMP
);

CREATE INDEX idx_payment_hash ON payment_transactions(payment_hash);
CREATE INDEX idx_payment_endpoint ON payment_transactions(endpoint);
CREATE INDEX idx_payment_created ON payment_transactions(created_at);