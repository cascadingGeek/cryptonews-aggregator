from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database.session import SessionLocal
from app.models.news import NewsItem, MergedData
from datetime import datetime, timedelta
from loguru import logger


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
        db = SessionLocal()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Delete old news items
            deleted_news = db.query(NewsItem).filter(
                NewsItem.created_at < cutoff_time
            ).delete()
            
            # Delete old merged data
            deleted_merged = db.query(MergedData).filter(
                MergedData.created_at < cutoff_time
            ).delete()
            
            db.commit()
            
            if deleted_news > 0 or deleted_merged > 0:
                logger.info(
                    f"Cleaned up {deleted_news} news items and "
                    f"{deleted_merged} merged data records older than 24 hours"
                )
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            db.rollback()
        finally:
            db.close()


cleanup_worker = CleanupWorker()