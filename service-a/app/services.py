import logging
import os
from typing import Dict, Any, Optional
import httpx
from .schemas import ExternalAPIResponse, CoordinatesPayload

logger = logging.getLogger(__name__)

# Configuration
IP_API_BASE_URL = "http://ip-api.com/json"
IP_API_TIMEOUT = int(os.getenv("IP_API_TIMEOUT", "5"))
MAX_RETRIES = 2


async def call_external_ip_api(ip: str) -> Optional[Dict[str, Any]]:
    """
    Call external IP geolocation API (ip-api.com)

    Args:
        ip: IP address to resolve

    Returns:
        Dictionary with geolocation data or None if failed
    """
    url = f"{IP_API_BASE_URL}/{ip}"

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Calling external API for IP: {ip} (attempt {attempt + 1}/{MAX_RETRIES})")
                response = await client.get(url, timeout=IP_API_TIMEOUT)

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"External API response for {ip}: {data.get('status')}")

                    # Validate response
                    api_response = ExternalAPIResponse(**data)

                    if api_response.status == "success":
                        return {
                            "lat": api_response.lat,
                            "lon": api_response.lon,
                            "city": api_response.city,
                            "country": api_response.country
                        }
                    else:
                        logger.warning(f"External API returned failure status for {ip}: {api_response.message}")
                        return None
                else:
                    logger.error(f"External API returned status {response.status_code} for {ip}")

        except httpx.TimeoutException:
            logger.warning(f"Timeout calling external API for {ip} (attempt {attempt + 1}/{MAX_RETRIES})")
        except httpx.ConnectError:
            logger.error(f"Connection error calling external API for {ip}")
        except Exception as e:
            logger.error(f"Unexpected error calling external API for {ip}: {e}")

        # If not the last attempt, continue to retry
        if attempt < MAX_RETRIES - 1:
            continue
        else:
            logger.error(f"All retry attempts failed for IP: {ip}")

    return None


async def forward_to_service_b(data: CoordinatesPayload) -> bool:
    """
    Forward coordinate data to Service B for storage

    Args:
        data: CoordinatesPayload containing IP and coordinates

    Returns:
        bool: True if successful, False otherwise
    """
    service_b_host = os.getenv("SERVICE_B_HOST", "service-b")
    service_b_port = os.getenv("SERVICE_B_PORT", "8000")

    if not service_b_host:
        logger.error("SERVICE_B_HOST environment variable not set")
        return False

    url = f"http://{service_b_host}:{service_b_port}/coordinates"

    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Forwarding coordinates to Service B for IP: {data.ip}")
            response = await client.post(
                url,
                json=data.model_dump(),
                timeout=10.0
            )

            if response.status_code == 200:
                logger.info(f"Successfully forwarded coordinates for IP: {data.ip} to Service B")
                return True
            else:
                logger.error(f"Service B returned status {response.status_code}")
                return False

    except httpx.TimeoutException:
        logger.error(f"Timeout forwarding to Service B for IP: {data.ip}")
        return False
    except httpx.ConnectError:
        logger.error(f"Cannot connect to Service B at {service_b_host}")
        return False
    except Exception as e:
        logger.error(f"Error forwarding to Service B: {e}")
        return False


async def resolve_ip(ip: str) -> Dict[str, Any]:
    """
    Main business logic: Resolve IP address and forward coordinates to Service B

    Args:
        ip: IP address to resolve

    Returns:
        Dictionary with result information
    """
    # Step 1: Call external API
    geo_data = await call_external_ip_api(ip)

    if not geo_data:
        return {
            "success": False,
            "message": "Failed to resolve IP address from external service",
            "ip": ip
        }

    # Step 2: Prepare payload for Service B
    payload = CoordinatesPayload(
        ip=ip,
        lat=geo_data["lat"],
        lon=geo_data["lon"],
        city=geo_data.get("city"),
        country=geo_data.get("country")
    )

    # Step 3: Forward to Service B
    forward_success = await forward_to_service_b(payload)

    if not forward_success:
        logger.warning(f"Failed to forward coordinates to Service B for IP: {ip}")
        return {
            "success": False,
            "message": "IP resolved but failed to store coordinates",
            "ip": ip,
            "coordinates": {
                "lat": geo_data["lat"],
                "lon": geo_data["lon"]
            }
        }

    # Success
    return {
        "success": True,
        "message": "IP resolved and coordinates stored successfully",
        "ip": ip,
        "coordinates": {
            "lat": geo_data["lat"],
            "lon": geo_data["lon"]
        }
    }
