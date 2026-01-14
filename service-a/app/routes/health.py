import logging
from fastapi import APIRouter
from shared.models import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for Kubernetes probes

    This is a lightweight endpoint that returns service status.
    It does not check external dependencies to keep it fast.

    Returns:
        HealthResponse with service status
    """
    return HealthResponse(
        status="healthy",
        service="Service A - IP Resolution"
    )
