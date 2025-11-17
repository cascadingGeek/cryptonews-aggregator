from fastapi import APIRouter
from app.cache.redis_client import redis_client
from app.database.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns service status and component health
    """
    health_status = {
        "status": "healthy",
        "components": {}
    }
    
    # Check database
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health_status["components"]["database"] = "connected"
    except:
        health_status["components"]["database"] = "disconnected"
        health_status["status"] = "degraded"
    
    # Check redis
    try:
        if redis_client.client:
            redis_client.client.ping()
            health_status["components"]["redis"] = "connected"
        else:
            health_status["components"]["redis"] = "disconnected"
            health_status["status"] = "degraded"
    except:
        health_status["components"]["redis"] = "disconnected"
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "0xMeta Crypto News Aggregator",
        "version": "1.0.0",
        "endpoints": {
            "markets": [
                "/markets/trends",
                "/markets/liquidity",
                "/markets/agents",
                "/markets/macro_events",
                "/markets/proof_of_work"
            ],
            "health": ["/health"]
        },
        "payment": {
            "protocol": "X402",
            "required": True,
            "header": "X-Payment-Hash"
        }
    }