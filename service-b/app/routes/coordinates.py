import logging
from fastapi import APIRouter, HTTPException, status
from ..storage import redis
from shared.models import (
    CoordinateItem,
    CoordinateStorageResponse,
    AllCoordinatesResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/coordinates")


@router.post("/", response_model=CoordinateStorageResponse)
async def store_coordinates(request: CoordinateItem):
    """
    Store coordinates received from Service A

    Args:
        request: CoordinateRequest containing IP and coordinate data

    Returns:
        CoordinateStorageResponse with success status
    """
    try:

        success = redis.save_coordinate(request.ip, request)

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


@router.get("/", response_model=AllCoordinatesResponse)
async def get_coordinates():
    """
    Retrieve all stored coordinates from Redis

    Returns:
        AllCoordinatesResponse with list of all coordinates
    """
    try:
        coordinates_data = redis.get_all_coordinates()

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
