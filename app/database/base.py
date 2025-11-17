"""
Database base configuration and utilities
Import all models here to ensure they are registered with SQLAlchemy
"""

from app.database.session import Base
from app.models.news import NewsItem, MergedData
from app.models.payment import PaymentTransaction

# Export Base for Alembic migrations
__all__ = ["Base"]