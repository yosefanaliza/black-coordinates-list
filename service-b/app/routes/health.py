import logging
from fastapi import APIRouter, HTTPException, status
from ..storage import redis
from shared.models import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for Kubernetes probes

    Returns:
        HealthResponse with service status and Redis connectivity
    """
    redis_connected = redis.is_redis_connected()

    if not redis_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis is not connected"
        )

    return HealthResponse(
        status="healthy",
        service="Service B - Coordinate Storage",
        redis_connected=redis_connected
    )
