import logging
from fastapi import APIRouter, HTTPException, status
from . import storage
from .schemas import (
    CoordinateRequest,
    CoordinateStorageResponse,
    AllCoordinatesResponse,
    CoordinateItem,
    HealthResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/coordinates", response_model=CoordinateStorageResponse)
async def store_coordinates(request: CoordinateRequest):
    """
    Store coordinates received from Service A

    Args:
        request: CoordinateRequest containing IP and coordinate data

    Returns:
        CoordinateStorageResponse with success status
    """
    try:
        data = {
            "lat": request.lat,
            "lon": request.lon,
            "city": request.city,
            "country": request.country
        }

        success = storage.save_coordinate(request.ip, data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store coordinates in Redis"
            )

        logger.info(f"Successfully stored coordinates for IP: {request.ip}")
        return CoordinateStorageResponse(
            success=True,
            message="Coordinates stored successfully",
            ip=request.ip
        )

    except Exception as e:
        logger.error(f"Error storing coordinates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/coordinates", response_model=AllCoordinatesResponse)
async def get_coordinates():
    """
    Retrieve all stored coordinates from Redis

    Returns:
        AllCoordinatesResponse with list of all coordinates
    """
    try:
        coordinates_data = storage.get_all_coordinates()

        coordinates = [
            CoordinateItem(**coord) for coord in coordinates_data
        ]

        logger.info(f"Retrieved {len(coordinates)} coordinates")
        return AllCoordinatesResponse(
            count=len(coordinates),
            coordinates=coordinates
        )

    except Exception as e:
        logger.error(f"Error retrieving coordinates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve coordinates: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for Kubernetes probes

    Returns:
        HealthResponse with service status and Redis connectivity
    """
    redis_connected = storage.is_redis_connected()

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
