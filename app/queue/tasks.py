"""
Background tasks for saving data to database
Uses Dramatiq for async processing
"""

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from app.core.config import settings
from app.database.session import AsyncSessionLocal
from app.models.news import SignalItem, CategoryFeed
from app.services.cryptonews import crypto_news_service
from app.services.game_x import game_x_service
from app.agents.data_merger import DataMergerAgent

import asyncio
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger
import time

# Setup Dramatiq broker
redis_broker = RedisBroker(url=settings.DRAMATIQ_REDIS_URL)
dramatiq.set_broker(redis_broker)


@dramatiq.actor(queue_name="data_storage", max_retries=3)
def save_signal_items(items: List[Dict[str, Any]]):
    """
    Save signal items to database
    
    Args:
        items: List of signal items
    """
    db = AsyncSessionLocal()
    try:
        saved_count = 0
        for item in items:
            # Check if item already exists by id
            existing = db.query(SignalItem).filter(
                SignalItem.id == item.get("id")
            ).first()
            
            if not existing:
                signal_item = SignalItem(
                    id=item.get("id"),
                    signal=item.get("signal"),
                    sentiment=item.get("sentiment"),
                    sentiment_value=item.get("sentiment_value"),
                    timestamp=item.get("timestamp"),
                    feed_categories=item.get("feed_categories", []),
                    short_context=item.get("short_context"),
                    long_context=item.get("long_context"),
                    sources=item.get("sources", []),
                    author=item.get("author"),
                    tokens=item.get("tokens", []),
                    tweet_url=item.get("tweet_url"),
                    narrative_id=item.get("narrative_id", "None")
                )
                db.add(signal_item)
                saved_count += 1
        
        db.commit()
        logger.info(f"Saved {saved_count} new signal items to database")
        
    except Exception as e:
        logger.error(f"Error saving signal items: {str(e)}")
        db.rollback()
    finally:
        db.close()


@dramatiq.actor(queue_name="data_storage", max_retries=3)
def save_category_feed(category: str, items: List[Dict[str, Any]]):
    """
    Save category feed to database
    
    Args:
        category: Category name
        items: List of signal items for this category
    """
    db = AsyncSessionLocal()
    try:
        # Check if feed exists for this category
        existing = db.query(CategoryFeed).filter(
            CategoryFeed.category == category
        ).order_by(CategoryFeed.last_updated.desc()).first()
        
        current_timestamp = time.time()
        
        # Update existing or create new
        if existing and (current_timestamp - existing.last_updated) < 3600:
            # Update existing feed if less than 1 hour old
            existing.items = items
            existing.item_count = len(items)
            existing.last_updated = current_timestamp
            logger.info(f"Updated category feed for: {category}")
        else:
            # Create new feed entry
            category_feed = CategoryFeed(
                category=category,
                items=items,
                item_count=len(items),
                last_updated=current_timestamp
            )
            db.add(category_feed)
            logger.info(f"Created new category feed for: {category}")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error saving category feed: {str(e)}")
        db.rollback()
    finally:
        db.close()


@dramatiq.actor(queue_name="data_processing")
def process_and_merge_feeds(category: str = None):
    """
    Background task to fetch and process feeds
    
    Args:
        category: Optional category to process
    """
    try:
        # Run async operations
        loop = asyncio.get_event_loop()
        
        async def fetch_and_merge():
            news = await crypto_news_service.fetch_trending_news(limit=50)
            tweets = await game_x_service.fetch_latest_tweets(max_results=50)
            
            if category:
                merged = DataMergerAgent.merge_by_category(category, news, tweets)
            else:
                merged = DataMergerAgent.merge_feeds(news, tweets)
            
            return merged
        
        result = loop.run_until_complete(fetch_and_merge())
        
        # Save results
        for cat_name, cat_data in result.items():
            items = cat_data.get("items", [])
            if items:
                save_signal_items.send(items)
                save_category_feed.send(cat_name, items)
        
        logger.info(f"Processed and merged feeds for category: {category or 'all'}")
        
    except Exception as e:
        logger.error(f"Error processing feeds: {str(e)}")


@dramatiq.actor(queue_name="data_cleanup", max_retries=1)
def cleanup_old_signals():
    """
    Clean up old signal items (older than 24 hours)
    """
    db = AsyncSessionLocal()
    try:
        cutoff_timestamp = time.time() - (24 * 3600)  # 24 hours ago
        
        # Delete old signals
        deleted_count = db.query(SignalItem).filter(
            SignalItem.timestamp < cutoff_timestamp
        ).delete()
        
        # Delete old category feeds
        deleted_feeds = db.query(CategoryFeed).filter(
            CategoryFeed.last_updated < cutoff_timestamp
        ).delete()
        
        db.commit()
        
        if deleted_count > 0 or deleted_feeds > 0:
            logger.info(
                f"Cleaned up {deleted_count} old signals and "
                f"{deleted_feeds} old category feeds"
            )
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        db.rollback()
    finally:
        db.close()