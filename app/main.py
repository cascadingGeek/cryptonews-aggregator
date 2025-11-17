from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.startup import startup_checks, shutdown_handlers
from app.middleware.x402 import X402PaymentMiddleware
from app.routes import markets, health
from app.database.session import init_db
import sys

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="0xMeta Crypto News Aggregator",
    description="Real-time crypto news and social media aggregation service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# X402 Payment middleware
app.add_middleware(X402PaymentMiddleware)

# Include routers
app.include_router(health.router)
app.include_router(markets.router)

# Serve frontend
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
except:
    logger.warning("Frontend directory not found, skipping static file serving")


@app.on_event("startup")
async def startup_event():
    """Run startup checks"""
    # Initialize database first
    if not init_db():
        logger.error("Database initialization failed. Exiting...")
        sys.exit(1)
    
    # Then run other startup checks
    success = await startup_checks()
    if not success:
        logger.error("Startup checks failed. Exiting...")
        sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """Run shutdown handlers"""
    await shutdown_handlers()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=settings.APP_ENV == "development"
    )