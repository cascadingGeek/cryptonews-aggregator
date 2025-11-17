"""
Routes module - API endpoint definitions
"""

from app.routes.markets import router as markets_router

__all__ = ["markets_router"]