from sqlalchemy import Column, String, DateTime, Text, JSON, Float, Integer, ARRAY, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database.session import Base


class SignalItem(Base):
    """
    Model for storing aggregated crypto signals/news items
    """
    __tablename__ = "signal_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signal = Column(Text, nullable=False)  # Main headline/signal
    sentiment = Column(String(20))  # bullish, bearish, neutral
    sentiment_value = Column(Float)  # 0.0 to 1.0
    timestamp = Column(Float, nullable=False, index=True)  # Unix timestamp
    feed_categories = Column(ARRAY(String))  # Array of categories
    short_context = Column(Text)  # Brief summary
    long_context = Column(Text)  # Detailed context
    sources = Column(ARRAY(String))  # Array of source URLs
    author = Column(String(200))  # Author/source name
    tokens = Column(ARRAY(String))  # Mentioned tokens (e.g., $BTC, $ETH)
    tweet_url = Column(String(500))  # If source is Twitter
    narrative_id = Column(String(100))  # Optional narrative ID
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_timestamp_categories', 'timestamp', 'feed_categories'),
        Index('idx_sentiment', 'sentiment'),
    )


class CategoryFeed(Base):
    """
    Model for storing category-specific feeds
    Maps to response structure: { "category_name": { "items": [...] } }
    """
    __tablename__ = "category_feeds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(50), nullable=False, index=True)  # rwa, defi, etc.
    items = Column(JSON, nullable=False)  # Array of signal items
    item_count = Column(Integer, default=0)
    last_updated = Column(Float, index=True)  # Unix timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_category_updated', 'category', 'last_updated'),
    )
