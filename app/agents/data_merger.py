from typing import List, Dict, Any
from app.agents.date_normalizer import DateNormalizerAgent
from app.agents.categorizer import CategorizerAgent
from loguru import logger


class DataMergerAgent:
    """Agent for merging data from CryptoNews and X feeds"""
    
    @classmethod
    def merge_feeds(
        cls,
        news_items: List[Dict[str, Any]],
        tweets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge and organize news and tweets"""
        
        # Normalize dates for all items
        normalized_news = [
            DateNormalizerAgent.normalize_item(item) for item in news_items
        ]
        normalized_tweets = [
            DateNormalizerAgent.normalize_item(item) for item in tweets
        ]
        
        # Combine all items
        all_items = normalized_news + normalized_tweets
        
        # Sort by date (most recent first)
        sorted_items = DateNormalizerAgent.sort_by_date(all_items)
        
        # Categorize items
        categorized = CategorizerAgent.categorize_items(sorted_items)
        
        # Build merged response
        merged_data = {
            "total_items": len(sorted_items),
            "news_count": len(normalized_news),
            "tweets_count": len(normalized_tweets),
            "categories": {},
            "recent_items": sorted_items[:20],  # Top 20 most recent
            "timestamp": DateNormalizerAgent.normalize_date("now").isoformat()
        }
        
        # Add categorized data
        for category, items in categorized.items():
            merged_data["categories"][category] = {
                "count": len(items),
                "items": cls._format_items(items[:10])  # Top 10 per category
            }
        
        logger.info(f"Merged {len(sorted_items)} items into {len(categorized)} categories")
        return merged_data
    
    @classmethod
    def merge_by_category(
        cls,
        category: str,
        news_items: List[Dict[str, Any]],
        tweets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge feeds for a specific category"""
        
        # Normalize dates
        normalized_news = [
            DateNormalizerAgent.normalize_item(item) for item in news_items
        ]
        normalized_tweets = [
            DateNormalizerAgent.normalize_item(item) for item in tweets
        ]
        
        # Filter by category
        news_filtered = [
            item for item in normalized_news 
            if CategorizerAgent.categorize_item(item) == category
        ]
        tweets_filtered = [
            item for item in normalized_tweets 
            if CategorizerAgent.categorize_item(item) == category
        ]
        
        # Combine and sort
        all_items = news_filtered + tweets_filtered
        sorted_items = DateNormalizerAgent.sort_by_date(all_items)
        
        return {
            "category": category,
            "total_items": len(sorted_items),
            "news_count": len(news_filtered),
            "tweets_count": len(tweets_filtered),
            "items": cls._format_items(sorted_items[:50]),  # Top 50 items
            "timestamp": DateNormalizerAgent.normalize_date("now").isoformat()
        }
    
    @staticmethod
    def _format_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format items for API response"""
        formatted = []
        
        for item in items:
            formatted_item = {
                "source": item.get("source"),
                "published_at": item.get("normalized_date").isoformat(),
                "url": item.get("url", "")
            }
            
            # Add source-specific fields
            if item.get("source") == "cryptonews":
                formatted_item.update({
                    "title": item.get("title"),
                    "content": item.get("content", "")[:500],  # Truncate content
                    "source_name": item.get("source_name"),
                    "sentiment": item.get("sentiment"),
                    "image_url": item.get("image_url")
                })
            elif item.get("source") == "twitter":
                formatted_item.update({
                    "text": item.get("text"),
                    "username": item.get("username"),
                    "author": item.get("author"),
                    "engagement": {
                        "likes": item.get("like_count", 0),
                        "retweets": item.get("retweet_count", 0),
                        "replies": item.get("reply_count", 0)
                    }
                })
            
            formatted.append(formatted_item)
        
        return formatted