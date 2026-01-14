import logging
from fastapi import APIRouter, HTTPException, status
from .services import resolve_ip
from shared.models import (
    CoordinateStorageResponse, 
    HealthResponse,
    IPRequest
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/resolve", response_model=CoordinateStorageResponse)
async def resolve_ip_address(request: IPRequest):
    """
    Resolve IP address to geographic coordinates

    This endpoint:
    1. Receives an IP address
    2. Calls external geolocation API (ip-api.com)
    3. Forwards coordinates to Service B for storage
    4. Returns success/failure status

    Args:
        request: IPRequest containing IP address

    Returns:
        IPResolutionResponse with resolution status
    """
    try:
        logger.info(f"Received IP resolution request for: {request.ip}")

        result = await resolve_ip(request.ip)

        if not result["success"]:
            # Determine appropriate HTTP status code
            if "Failed to resolve" in result["message"]:
                status_code = status.HTTP_502_BAD_GATEWAY
            elif "failed to store" in result["message"]:
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            raise HTTPException(
                status_code=status_code,
                detail=result["message"]
            )

        return CoordinateStorageResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error resolving IP {request.ip}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


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
