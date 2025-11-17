from sqlalchemy import Column, String, DateTime, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database.session import Base


class NewsItem(Base):
    __tablename__ = "news_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(50), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # 'cryptonews' or 'twitter'
    title = Column(String(500))
    content = Column(Text)
    url = Column(String(1000))
    author = Column(String(200))
    published_at = Column(DateTime, nullable=False, index=True)
    normalized_date = Column(DateTime, nullable=False)

    # FIX: rename Python attribute, keep DB column name "metadata"
    extra_metadata = Column("metadata", JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_category_date', 'category', 'normalized_date'),
        Index('idx_source_date', 'source', 'published_at'),
    )


class MergedData(Base):
    __tablename__ = "merged_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(50), nullable=False, index=True)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_category_created', 'category', 'created_at'),
    )
