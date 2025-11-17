import dramatiq
from dramatiq.brokers.redis import RedisBroker
from app.core.config import settings
from app.database.session import SessionLocal
from app.models.news import NewsItem, MergedData
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger
import json

# Setup Dramatiq broker
redis_broker = RedisBroker(url=settings.DRAMATIQ_REDIS_URL)
dramatiq.set_broker(redis_broker)


@dramatiq.actor(queue_name="data_storage", max_retries=3)
def save_news_items(items: List[Dict[str, Any]]):
    """
    Background task to save news items to database
    
    Args:
        items: List of news items to save
    """
    db = SessionLocal()
    try:
        saved_count = 0
        for item in items:
            # Check if item already exists
            existing = db.query(NewsItem).filter(
                NewsItem.url == item.get("url"),
                NewsItem.source == item.get("source")
            ).first()
            
            if not existing:
                news_item = NewsItem(
                    category=item.get("category", "trends"),
                    source=item.get("source"),
                    title=item.get("title"),
                    content=item.get("content") or item.get("text"),
                    url=item.get("url"),
                    author=item.get("author") or item.get("username"),
                    published_at=item.get("published_at"),
                    normalized_date=item.get("normalized_date"),
                    metadata=item.get("metadata", {})
                )
                db.add(news_item)
                saved_count += 1
        
        db.commit()
        logger.info(f"Saved {saved_count} new items to database")
        
    except Exception as e:
        logger.error(f"Error saving news items: {str(e)}")
        db.rollback()
    finally:
        db.close()


@dramatiq.actor(queue_name="data_storage", max_retries=3)
def save_merged_data(category: str, data: Dict[str, Any]):
    """
    Background task to save merged data to database
    
    Args:
        category: Data category
        data: Merged data to save
    """
    db = SessionLocal()
    try:
        merged = MergedData(
            category=category,
            data=data
        )
        db.add(merged)
        db.commit()
        logger.info(f"Saved merged data for category: {category}")
        
    except Exception as e:
        logger.error(f"Error saving merged data: {str(e)}")
        db.rollback()
    finally:
        db.close()


@dramatiq.actor(queue_name="data_processing")
def process_and_categorize(news_items: List[Dict], tweets: List[Dict]):
    """
    Background task to process and categorize data
    
    Args:
        news_items: News items to process
        tweets: Tweet items to process
    """
    try:
        from app.agents.data_merger import DataMergerAgent
        
        # Merge data
        merged = DataMergerAgent.merge_feeds(news_items, tweets)
        
        # Save to database
        for category in merged.get("categories", {}).keys():
            category_data = merged["categories"][category]
            save_merged_data.send(category, category_data)
        
        logger.info("Data processing and categorization completed")
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")