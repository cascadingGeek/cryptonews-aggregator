from typing import Dict, Any
from app.services.cryptonews import crypto_news_service
from app.services.game_x import game_x_service
from app.agents.data_merger import DataMergerAgent
from app.agents.categorizer import CategorizerAgent
from app.cache.redis_client import redis_client
from app.queue.tasks import save_news_items, save_merged_data
from loguru import logger
import json


class MarketsController:
    """Controller for handling market endpoints"""
    
    @staticmethod
    async def get_trends() -> Dict[str, Any]:
        """Get trending crypto news and social updates"""
        cache_key = "markets:trends"
        
        # Check cache first
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Returning cached trends data")
            return cached
        
        # Fetch fresh data
        news = await crypto_news_service.fetch_trending_news(limit=30)
        tweets = await game_x_service.get_all_account_feeds(limit_per_account=5)
        
        # Merge data by category
        merged = DataMergerAgent.merge_by_category("trends", news, tweets)
        
        # Cache result
        redis_client.set(cache_key, merged)
        
        # Save to database in background
        all_items = news + tweets
        if all_items:
            save_news_items.send(all_items)
        
        logger.info(f"Fetched trends: {merged['total_items']} items")
        return merged
    
    @staticmethod
    async def get_liquidity() -> Dict[str, Any]:
        """Get liquidity-related news and updates"""
        cache_key = "markets:liquidity"
        
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Returning cached liquidity data")
            return cached
        
        news = await crypto_news_service.fetch_latest_news(limit=30)
        tweets = await game_x_service.get_all_account_feeds(limit_per_account=5)
        
        merged = DataMergerAgent.merge_by_category("liquidity", news, tweets)
        
        redis_client.set(cache_key, merged)
        
        all_items = news + tweets
        if all_items:
            save_news_items.send(all_items)
        
        logger.info(f"Fetched liquidity: {merged['total_items']} items")
        return merged
    
    @staticmethod
    async def get_agents() -> Dict[str, Any]:
        """Get AI agents and automation-related news"""
        cache_key = "markets:agents"
        
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Returning cached agents data")
            return cached
        
        # Focus on AI/agent keywords
        keywords = ["ai", "agent", "automation", "virtual", "bot", "llm"]
        
        news = await crypto_news_service.fetch_latest_news(limit=30)
        tweets = await game_x_service.search_related_posts(keywords)
        
        merged = DataMergerAgent.merge_by_category("agents", news, tweets)
        
        redis_client.set(cache_key, merged)
        
        all_items = news + tweets
        if all_items:
            save_news_items.send(all_items)
        
        logger.info(f"Fetched agents: {merged['total_items']} items")
        return merged
    
    @staticmethod
    async def get_macro_events() -> Dict[str, Any]:
        """Get macro economic events and regulatory news"""
        cache_key = "markets:macro_events"
        
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Returning cached macro events data")
            return cached
        
        keywords = ["regulation", "sec", "fed", "etf", "institutional", "government"]
        
        news = await crypto_news_service.fetch_latest_news(limit=30)
        tweets = await game_x_service.search_related_posts(keywords)
        
        merged = DataMergerAgent.merge_by_category("macro_events", news, tweets)
        
        redis_client.set(cache_key, merged)
        
        all_items = news + tweets
        if all_items:
            save_news_items.send(all_items)
        
        logger.info(f"Fetched macro events: {merged['total_items']} items")
        return merged
    
    @staticmethod
    async def get_proof_of_work() -> Dict[str, Any]:
        """Get mining and PoW-related news"""
        cache_key = "markets:proof_of_work"
        
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Returning cached PoW data")
            return cached
        
        keywords = ["mining", "hashrate", "miner", "pow", "difficulty"]
        
        news = await crypto_news_service.fetch_latest_news(limit=30)
        tweets = await game_x_service.search_related_posts(keywords)
        
        merged = DataMergerAgent.merge_by_category("proof_of_work", news, tweets)
        
        redis_client.set(cache_key, merged)
        
        all_items = news + tweets
        if all_items:
            save_news_items.send(all_items)
        
        logger.info(f"Fetched PoW: {merged['total_items']} items")
        return merged