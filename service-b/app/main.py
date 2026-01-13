import logging
import os
from fastapi import FastAPI
from .routes import router
from . import storage

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Service B - Coordinate Storage",
    description="Storage service for geographic coordinates. Receives coordinates from Service A and stores them in Redis.",
    version="1.0.0"
)

# Include router
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection on startup"""
    try:
        storage.connect_redis()
        logger.info("Service B started successfully")
    except Exception as e:
        logger.error(f"Failed to start Service B: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Close Redis connection on shutdown"""
    try:
        storage.close_redis()
        logger.info("Service B shut down successfully")
    except Exception as e:
        logger.warning(f"Error during shutdown: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Service B - Coordinate Storage",
        "status": "running",
        "version": "1.0.0"
    }
