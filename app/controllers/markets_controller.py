"""
Controller for handling market endpoints
"""

from typing import Dict, Any
from app.services.cryptonews import crypto_news_service
from app.services.game_x import game_x_service
from app.agents.data_merger import DataMergerAgent
from app.cache.redis_client import redis_client
from app.queue.tasks import save_signal_items, save_category_feed
from loguru import logger
import time


class MarketsController:
    """Controller for handling market endpoints"""
    
    @staticmethod
    async def get_trends() -> Dict[str, Any]:
        """
        Get trending crypto signals
        
        Returns:
            { "trends": { "items": [...] } }
        """
        cache_key = "markets:trends"
        
        # Check cache
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Returning cached trends data")
            return cached
        
        # Fetch fresh data
        news = await crypto_news_service.fetch_trending_news(limit=30)
        tweets = await game_x_service.fetch_latest_tweets(max_results=50)
        
        # Merge and format
        merged = DataMergerAgent.merge_by_category("trends", news, tweets)
        
        # Add metadata
        result = {
            **merged,
            "_metadata": {
                "total_items": len(merged.get("trends", {}).get("items", [])),
                "timestamp": time.time(),
                "cache_ttl": 3600
            }
        }
        
        # Cache result
        redis_client.set(cache_key, result)
        
        # Save to database in background
        items = merged.get("trends", {}).get("items", [])
        if items:
            save_signal_items.send(items)
            save_category_feed.send("trends", items)
        
        logger.info(f"Fetched trends: {len(items)} items")
        return result
    
    @staticmethod
    async def get_liquidity() -> Dict[str, Any]:
        """
        Get liquidity-related signals
        
        Returns:
            { "liquidity": { "items": [...] } }
        """
        cache_key = "markets:liquidity"
        
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Returning cached liquidity data")
            return cached
        
        # Fetch with liquidity keywords
        keywords = ["liquidity", "volume", "dex", "trading", "swap", "pool"]
        
        news = await crypto_news_service.fetch_latest_news(limit=30)
        tweets = await game_x_service.search_tweets_by_keywords(keywords, max_results=30)
        
        merged = DataMergerAgent.merge_by_category("defi", news, tweets)
        
        # Rename to liquidity for response
        result = {
            "liquidity": merged.get("defi", {"items": []}),
            "_metadata": {
                "total_items": len(merged.get("defi", {}).get("items", [])),
                "timestamp": time.time(),
                "cache_ttl": 3600
            }
        }
        
        items = result["liquidity"]["items"]
        redis_client.set(cache_key, result)
        
        if items:
            save_signal_items.send(items)
            save_category_feed.send("liquidity", items)
        
        logger.info(f"Fetched liquidity: {len(items)} items")
        return result
    
    @staticmethod
    async def get_agents() -> Dict[str, Any]:
        """
        Get AI agents signals
        
        Returns:
            { "ai": { "items": [...] } }
        """
        cache_key = "markets:agents"
        
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Returning cached agents data")
            return cached
        
        keywords = ["ai", "agent", "bot", "llm", "autonomous", "virtual"]
        
        news = await crypto_news_service.fetch_latest_news(limit=30)
        tweets = await game_x_service.search_tweets_by_keywords(keywords, max_results=30)
        
        merged = DataMergerAgent.merge_by_category("ai", news, tweets)
        
        result = {
            "ai": merged.get("ai", {"items": []}),
            "_metadata": {
                "total_items": len(merged.get("ai", {}).get("items", [])),
                "timestamp": time.time(),
                "cache_ttl": 3600
            }
        }
        
        items = result["ai"]["items"]
        redis_client.set(cache_key, result)
        
        if items:
            save_signal_items.send(items)
            save_category_feed.send("ai", items)
        
        logger.info(f"Fetched AI agents: {len(items)} items")
        return result
    
    @staticmethod
    async def get_macro_events() -> Dict[str, Any]:
        """
        Get macro events signals
        
        Returns:
            { "macro": { "items": [...] } }
        """
        cache_key = "markets:macro_events"
        
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Returning cached macro events data")
            return cached
        
        keywords = ["regulation", "sec", "fed", "etf", "government", "policy", "institutional"]
        
        news = await crypto_news_service.fetch_latest_news(limit=30)
        tweets = await game_x_service.search_tweets_by_keywords(keywords, max_results=30)
        
        merged = DataMergerAgent.merge_by_category("macro", news, tweets)
        
        result = {
            "macro": merged.get("macro", {"items": []}),
            "_metadata": {
                "total_items": len(merged.get("macro", {}).get("items", [])),
                "timestamp": time.time(),
                "cache_ttl": 3600
            }
        }
        
        items = result["macro"]["items"]
        redis_client.set(cache_key, result)
        
        if items:
            save_signal_items.send(items)
            save_category_feed.send("macro", items)
        
        logger.info(f"Fetched macro events: {len(items)} items")
        return result
    
    @staticmethod
    async def get_proof_of_work() -> Dict[str, Any]:
        """
        Get PoW mining signals
        
        Returns:
            { "mining": { "items": [...] } }
        """
        cache_key = "markets:proof_of_work"
        
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Returning cached PoW data")
            return cached
        
        keywords = ["mining", "hashrate", "miner", "pow", "difficulty", "asic"]
        
        news = await crypto_news_service.fetch_latest_news(limit=30)
        tweets = await game_x_service.search_tweets_by_keywords(keywords, max_results=30)
        
        # Create mining category
        all_items = news + tweets
        signals = []
        
        from app.agents.data_merger import DataMergerAgent
        for item in all_items:
            if item.get("source") == "cryptonews":
                signal = DataMergerAgent._transform_news_to_signal(item)
            else:
                signal = DataMergerAgent._transform_tweet_to_signal(item)
            
            if signal:
                # Filter for mining-related content
                text = signal.get("signal", "").lower()
                if any(kw in text for kw in keywords):
                    signals.append(signal)
        
        # Sort by timestamp
        signals.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        result = {
            "mining": {"items": signals[:50]},
            "_metadata": {
                "total_items": len(signals),
                "timestamp": time.time(),
                "cache_ttl": 3600
            }
        }
        
        redis_client.set(cache_key, result)
        
        if signals:
            save_signal_items.send(signals)
            save_category_feed.send("mining", signals)
        
        logger.info(f"Fetched PoW: {len(signals)} items")
        return result