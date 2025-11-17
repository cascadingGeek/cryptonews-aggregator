"""
Routes module - API endpoint definitions
"""

from app.routes.health import router as health_router
from app.routes.markets import router as markets_router

__all__ = ["health_router", "markets_router"]