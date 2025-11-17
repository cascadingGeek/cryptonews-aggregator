import httpx
from typing import List, Dict, Any
from app.core.config import settings
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


class CryptoNewsService:
    def __init__(self):
        self.api_key = settings.CRYPTO_NEWS_API_KEY
        self.base_url = "https://cryptonews-api.com/api/v1"
        self.client = None
    
    async def initialize(self):
        """Initialize HTTP client and test connection"""
        try:
            self.client = httpx.AsyncClient(timeout=30.0)
            # Test API connection
            response = await self.client.get(
                f"{self.base_url}/category",
                params={"token": self.api_key, "items": 1}
            )
            if response.status_code == 200:
                logger.info("✓ CryptoNews API connection verified")
                return True
            else:
                logger.error(f"✗ CryptoNews API verification failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ CryptoNews API initialization failed: {str(e)}")
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def fetch_trending_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch trending crypto news"""
        try:
            response = await self.client.get(
                f"{self.base_url}/category",
                params={
                    "token": self.api_key,
                    "items": limit,
                    "page": 1
                }
            )
            response.raise_for_status()
            data = response.json()
            
            news_items = []
            if data.get("data"):
                for item in data["data"]:
                    news_items.append({
                        "source": "cryptonews",
                        "title": item.get("title", ""),
                        "content": item.get("text", ""),
                        "url": item.get("news_url", ""),
                        "published_at": item.get("date", ""),
                        "source_name": item.get("source_name", ""),
                        "image_url": item.get("image_url", ""),
                        "sentiment": item.get("sentiment", "neutral"),
                        "topics": item.get("topics", [])
                    })
            
            logger.info(f"Fetched {len(news_items)} trending news items")
            return news_items
        except Exception as e:
            logger.error(f"Error fetching trending news: {str(e)}")
            return []
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def fetch_latest_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch latest crypto news"""
        try:
            response = await self.client.get(
                f"{self.base_url}/latest",
                params={
                    "token": self.api_key,
                    "items": limit
                }
            )
            response.raise_for_status()
            data = response.json()
            
            news_items = []
            if data.get("data"):
                for item in data["data"]:
                    news_items.append({
                        "source": "cryptonews",
                        "title": item.get("title", ""),
                        "content": item.get("text", ""),
                        "url": item.get("news_url", ""),
                        "published_at": item.get("date", ""),
                        "source_name": item.get("source_name", ""),
                        "image_url": item.get("image_url", ""),
                        "sentiment": item.get("sentiment", "neutral")
                    })
            
            logger.info(f"Fetched {len(news_items)} latest news items")
            return news_items
        except Exception as e:
            logger.error(f"Error fetching latest news: {str(e)}")
            return []
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()


crypto_news_service = CryptoNewsService()