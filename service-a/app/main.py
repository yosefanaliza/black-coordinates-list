import logging
import os
from .server import app

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    """Validate environment variables on startup"""
    service_b_host = os.getenv("SERVICE_B_HOST")
    service_b_port = os.getenv("SERVICE_B_PORT", "80")

    if not service_b_host:
        logger.warning("SERVICE_B_HOST environment variable not set")
    else:
        logger.info(f"Service B configured: {service_b_host}:{service_b_port}")

    logger.info("Service A started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Service A shut down successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Service A - IP Resolution",
        "status": "running",
        "version": "1.0.0"
    }
