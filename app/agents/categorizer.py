from typing import Dict, Any, List
import re
from loguru import logger


class CategorizerAgent:
    """Agent for categorizing crypto news and social media updates"""
    
    # Category keywords mapping
    CATEGORY_KEYWORDS = {
        "trends": [
            "trend", "trending", "viral", "popular", "momentum", "surge",
            "rally", "pump", "moon", "bullish", "bearish", "sentiment"
        ],
        "liquidity": [
            "liquidity", "volume", "tvl", "trading volume", "market depth",
            "liquidation", "liquidity pool", "dex", "swap", "exchange"
        ],
        "agents": [
            "agent", "ai", "bot", "automation", "virtual", "autonomous",
            "ai agent", "llm", "chatbot", "game", "virtuals"
        ],
        "macro_events": [
            "fed", "interest rate", "inflation", "regulation", "sec", "government",
            "policy", "ban", "law", "compliance", "legal", "etf", "institutional",
            "blackrock", "fidelity", "election"
        ],
        "proof_of_work": [
            "mining", "miner", "hashrate", "difficulty", "pow", "proof of work",
            "asic", "gpu", "energy", "bitcoin mining", "ethereum mining"
        ]
    }
    
    @classmethod
    def categorize_item(cls, item: Dict[str, Any]) -> str:
        """Categorize a single item based on content"""
        text = ""
        
        # Extract text content
        if "title" in item:
            text += item["title"].lower() + " "
        if "content" in item:
            text += item["content"].lower() + " "
        if "text" in item:
            text += item["text"].lower() + " "
        
        # Score each category
        category_scores = {}
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            category_scores[category] = score
        
        # Return category with highest score, default to trends
        if max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        
        return "trends"  # Default category
    
    @classmethod
    def categorize_items(cls, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize multiple items into buckets"""
        categorized = {
            "trends": [],
            "liquidity": [],
            "agents": [],
            "macro_events": [],
            "proof_of_work": []
        }
        
        for item in items:
            category = cls.categorize_item(item)
            item["category"] = category
            categorized[category].append(item)
        
        logger.info(f"Categorized {len(items)} items: " +
                   ", ".join([f"{k}={len(v)}" for k, v in categorized.items()]))
        
        return categorized
    
    @classmethod
    def extract_keywords(cls, text: str, limit: int = 10) -> List[str]:
        """Extract key terms from text for search"""
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "is", "are", "was", "were"
        }
        
        # Clean and split
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Get unique keywords, prioritize crypto terms
        crypto_terms = []
        other_terms = []
        
        for word in keywords:
            if any(term in word for term in ["crypto", "token", "coin", "blockchain", "defi"]):
                crypto_terms.append(word)
            else:
                other_terms.append(word)
        
        # Return crypto terms first, then others
        unique_keywords = list(dict.fromkeys(crypto_terms + other_terms))
        return unique_keywords[:limit]