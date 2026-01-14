import logging
from fastapi import APIRouter, HTTPException, status
from ..services.coordinates import CoordinatesService
from shared.models import (
    CoordinateStorageResponse,
    IPRequest,
    AllCoordinatesResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/coordinates")

# Initialize coordinates service
coordinates_service = CoordinatesService()


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

        result = await coordinates_service.resolve_ip(request.ip)

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


@router.get("/", response_model=AllCoordinatesResponse)
async def get_all_coordinates():
    """
    Retrieve all stored coordinates from Service B

    This endpoint:
    1. Fetches all coordinates from Service B
    2. Returns the complete list with count

    Returns:
        AllCoordinatesResponse with all stored coordinates
    """
    try:
        logger.info("Received request to fetch all coordinates")

        result = await coordinates_service.fetch_all_coordinates()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to fetch coordinates from Service B"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching coordinates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
