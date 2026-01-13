from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import re


class IPRequest(BaseModel):
    """Request model for IP address resolution"""
    ip: str = Field(..., description="IPv4 address to resolve")

    @field_validator('ip')
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IP address format"""
        # Basic IPv4 format check
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, v):
            raise ValueError('Invalid IP address format. Must be in format: X.X.X.X')

        # Validate each octet is 0-255
        octets = v.split('.')
        for octet in octets:
            if not 0 <= int(octet) <= 255:
                raise ValueError(f'Invalid IP address. Octet {octet} must be between 0 and 255')

        return v


class IPResolutionResponse(BaseModel):
    """Response model for IP resolution"""
    success: bool
    message: str
    ip: Optional[str] = None
    coordinates: Optional[Dict[str, Any]] = None


class CoordinatesPayload(BaseModel):
    """Payload sent to Service B for coordinate storage"""
    ip: str
    lat: float
    lon: float
    city: Optional[str] = None
    country: Optional[str] = None


class ExternalAPIResponse(BaseModel):
    """Response model from ip-api.com external service"""
    status: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
