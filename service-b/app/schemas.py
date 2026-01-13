from typing import Optional, List
from pydantic import BaseModel, Field


class CoordinateRequest(BaseModel):
    """Request model for storing coordinates"""
    ip: str
    lat: float = Field(..., ge=-90, le=90, description="Latitude between -90 and 90")
    lon: float = Field(..., ge=-180, le=180, description="Longitude between -180 and 180")
    city: Optional[str] = None
    country: Optional[str] = None


class CoordinateStorageResponse(BaseModel):
    """Response model for coordinate storage operations"""
    success: bool
    message: str
    ip: str


class CoordinateItem(BaseModel):
    """Model for a single coordinate item"""
    ip: str
    lat: float
    lon: float
    city: Optional[str] = None
    country: Optional[str] = None


class AllCoordinatesResponse(BaseModel):
    """Response model for retrieving all coordinates"""
    count: int
    coordinates: List[CoordinateItem]


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    redis_connected: bool
