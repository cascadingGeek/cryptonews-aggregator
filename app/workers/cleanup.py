"""
Cleanup Worker - Scheduled job to remove old data
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database.session import AsyncSessionLocal
from app.models.news import SignalItem, CategoryFeed
from app.models.payment import PaymentTransaction
from datetime import datetime, timedelta
from loguru import logger
import time


class CleanupWorker:
    """Worker for cleaning up old data from database"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        """Start the cleanup scheduler"""
        # Run cleanup every hour
        self.scheduler.add_job(
            self.cleanup_old_data,
            'interval',
            hours=1,
            id='cleanup_old_data',
            name='Cleanup old database records',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("✓ Cleanup worker started successfully")
    
    def stop(self):
        """Stop the cleanup scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Cleanup worker stopped")
    
    @staticmethod
    def cleanup_old_data():
        """Delete data older than 24 hours"""
        db = AsyncSessionLocal()
        try:
            # Calculate cutoff times
            cutoff_datetime = datetime.utcnow() - timedelta(hours=24)
            cutoff_timestamp = time.time() - (24 * 3600)
            
            # Delete old signal items (by timestamp)
            deleted_signals = db.query(SignalItem).filter(
                SignalItem.timestamp < cutoff_timestamp
            ).delete()
            
            # Delete old category feeds (by last_updated)
            deleted_feeds = db.query(CategoryFeed).filter(
                CategoryFeed.last_updated < cutoff_timestamp
            ).delete()
            
            # Delete old payment transactions (by created_at)
            deleted_payments = db.query(PaymentTransaction).filter(
                PaymentTransaction.created_at < cutoff_datetime
            ).delete()
            
            db.commit()
            
            if deleted_signals > 0 or deleted_feeds > 0 or deleted_payments > 0:
                logger.info(
                    f"Cleaned up {deleted_signals} signal items, "
                    f"{deleted_feeds} category feeds, and "
                    f"{deleted_payments} payment records older than 24 hours"
                )
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            db.rollback()
        finally:
            db.close()


cleanup_worker = CleanupWorker()