from typing import Optional, List, Annotated
from pydantic import BaseModel, Field
from ipaddress import IPv4Address


class CoordinateItem(BaseModel):
    """Request model for storing coordinates"""
    ip: Annotated[IPv4Address, Field(..., description="Valid IPv4 address")]
    lat: Annotated[float, Field(..., ge=-90, le=90, description="Latitude between -90 and 90")]
    lon: Annotated[float, Field(..., ge=-180, le=180, description="Longitude between -180 and 180")]
    city: Optional[str] = None
    country: Optional[str] = None


class CoordinateStorageResponse(BaseModel):
    """Response model for coordinate storage operations"""
    success: bool
    message: str
    ip: IPv4Address



class AllCoordinatesResponse(BaseModel):
    """Response model for retrieving all coordinates"""
    count: int
    coordinates: List[CoordinateItem]


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    redis_connected: bool
