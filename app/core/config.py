from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # API Configuration
    BASE_URL: str
    FACILITATOR_URL: Optional[str] = None

    # Crypto News
    CRYPTO_NEWS_API_KEY: str

    # Game X
    GAME_API_KEY: str
    GAME_ACCESS_TOKEN: str

    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    REDIS_TTL: int = 3600
    
    # Worker Configuration
    DRAMATIQ_REDIS_URL: str
    
    # App Configuration
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    API_PORT: int = 8080

    # Extra APP fields in your .env
    APP_NAME: Optional[str] = None
    ENVIRONMENT: Optional[str] = None
    DEBUG: Optional[int] = None
    SHOW_SQL_ALCHEMY_QUERIES: Optional[int] = None

    # X Accounts to monitor
    X_ACCOUNTS: List[str] = [
        "lookonchain",
        "pumpdotfun",
        "virtuals_io",
        "useBackroom",
        "CreatorBid",
        "HyperliquidX",
        "solana",
        "base",
        "ArAIstotle",
        "Cointelegraph",
        "TheBlock__",
        "WatcherGuru",
        "cryptodotnews",
        "blockchainrptr",
    ]

    # Payment configuration 
    PAYMENT_PRICE_PER_REQUEST: float = 0.001 # Price in currency
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
