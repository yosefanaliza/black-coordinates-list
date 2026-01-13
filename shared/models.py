from typing import Optional, List, Annotated
from pydantic import BaseModel, Field
from ipaddress import IPv4Address


IPField = Annotated[IPv4Address, Field(..., description="Valid IPv4 address")]

class IPRequest(BaseModel):
    """Request model for IP address resolution"""
    ip: IPField

class CoordinateItem(BaseModel):
    ip: IPField
    lat: Annotated[float, Field(..., ge=-90, le=90, description="Latitude between -90 and 90")]
    lon: Annotated[float, Field(..., ge=-180, le=180, description="Longitude between -180 and 180")]
    city: Optional[str] = None
    country: Optional[str] = None
    
    
##### RESPONSE MODELS #####
    
class AllCoordinatesResponse(BaseModel):
    count: int
    coordinates: List[CoordinateItem]

class HealthResponse(BaseModel):
    status: str
    service: str
    redis_connected: Optional[bool]  = None
    
class CoordinateStorageResponse(BaseModel):
    """Response model for coordinate storage operations"""
    success: bool
    message: str
    ip: IPField
    coordinates: Optional[dict[str,float]] = None

class ExternalAPIResponse(BaseModel):
    status: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None
    message: Optional[str] = None

