"""
Service for merging data from multiple sources
Coordinates between CryptoNews and GAME X services
"""

from typing import Dict, Any, List
from app.services.cryptonews import crypto_news_service
from app.services.game_x import game_x_service
from app.agents.data_merger import DataMergerAgent
from app.agents.categorizer import CategorizerAgent
from loguru import logger


class MergerService:
    """Service for coordinating data fetching and merging"""
    
    @staticmethod
    async def fetch_and_merge_all() -> Dict[str, Any]:
        """
        Fetch data from all sources and merge into categories
        
        Returns:
            Complete merged dataset with all categories
        """
        try:
            # Fetch from both sources
            logger.info("Fetching data from CryptoNews and GAME X...")
            
            news_items = await crypto_news_service.fetch_trending_news(limit=50)
            tweets = await game_x_service.get_all_account_feeds(limit_per_account=10)
            
            # Merge all data
            merged_data = DataMergerAgent.merge_feeds(news_items, tweets)
            
            logger.info(f"Successfully merged {merged_data['total_items']} items")
            return merged_data
            
        except Exception as e:
            logger.error(f"Error in fetch_and_merge_all: {str(e)}")
            return {
                "total_items": 0,
                "news_count": 0,
                "tweets_count": 0,
                "categories": {},
                "error": str(e)
            }
    
    @staticmethod
    async def fetch_and_merge_by_category(category: str) -> Dict[str, Any]:
        """
        Fetch and merge data for a specific category
        
        Args:
            category: The category to fetch (trends, liquidity, agents, etc.)
            
        Returns:
            Merged data for the specified category
        """
        try:
            logger.info(f"Fetching data for category: {category}")
            
            # Determine search strategy based on category
            if category == "trends":
                news_items = await crypto_news_service.fetch_trending_news(limit=30)
                tweets = await game_x_service.get_all_account_feeds(limit_per_account=5)
            
            elif category == "liquidity":
                news_items = await crypto_news_service.fetch_latest_news(limit=30)
                keywords = ["liquidity", "volume", "dex", "swap", "trading"]
                tweets = await game_x_service.search_related_posts(keywords)
            
            elif category == "agents":
                news_items = await crypto_news_service.fetch_latest_news(limit=30)
                keywords = ["ai", "agent", "bot", "automation", "virtual", "llm"]
                tweets = await game_x_service.search_related_posts(keywords)
            
            elif category == "macro_events":
                news_items = await crypto_news_service.fetch_latest_news(limit=30)
                keywords = ["regulation", "sec", "fed", "etf", "government", "institutional"]
                tweets = await game_x_service.search_related_posts(keywords)
            
            elif category == "proof_of_work":
                news_items = await crypto_news_service.fetch_latest_news(limit=30)
                keywords = ["mining", "hashrate", "miner", "pow", "difficulty"]
                tweets = await game_x_service.search_related_posts(keywords)
            
            else:
                # Default: fetch general data
                news_items = await crypto_news_service.fetch_latest_news(limit=30)
                tweets = await game_x_service.get_all_account_feeds(limit_per_account=5)
            
            # Merge by category
            merged_data = DataMergerAgent.merge_by_category(
                category, 
                news_items, 
                tweets
            )
            
            logger.info(
                f"Successfully merged {merged_data['total_items']} items "
                f"for category: {category}"
            )
            return merged_data
            
        except Exception as e:
            logger.error(f"Error in fetch_and_merge_by_category: {str(e)}")
            return {
                "category": category,
                "total_items": 0,
                "news_count": 0,
                "tweets_count": 0,
                "items": [],
                "error": str(e)
            }
    
    @staticmethod
    async def search_related_content(keywords: List[str]) -> Dict[str, Any]:
        """
        Search for content related to specific keywords
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            Merged search results
        """
        try:
            logger.info(f"Searching for keywords: {', '.join(keywords)}")
            
            # Search in news (CryptoNews API doesn't have keyword search in basic plan)
            # So we fetch latest and filter
            news_items = await crypto_news_service.fetch_latest_news(limit=50)
            
            # Filter news by keywords
            filtered_news = []
            for item in news_items:
                text = f"{item.get('title', '')} {item.get('content', '')}".lower()
                if any(keyword.lower() in text for keyword in keywords):
                    filtered_news.append(item)
            
            # Search tweets
            tweets = await game_x_service.search_related_posts(keywords)
            
            # Merge results
            merged_data = DataMergerAgent.merge_feeds(filtered_news, tweets)
            
            logger.info(
                f"Found {len(filtered_news)} news and {len(tweets)} tweets "
                f"for keywords: {', '.join(keywords)}"
            )
            return merged_data
            
        except Exception as e:
            logger.error(f"Error in search_related_content: {str(e)}")
            return {
                "total_items": 0,
                "news_count": 0,
                "tweets_count": 0,
                "categories": {},
                "error": str(e)
            }


# Singleton instance
merger_service = MergerService()