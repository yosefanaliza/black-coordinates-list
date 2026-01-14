import json
import logging
from typing import List
from shared.models import CoordinateItem, IPField
from ..storage.redis import redis_client
import redis

logger = logging.getLogger(__name__)


class CoordinatesService:
    """Service for managing coordinate storage and retrieval"""

    def __init__(self):
        """Initialize the coordinates service"""
        self.redis_client = redis_client

    def save_coordinate(self, ip: IPField, data: CoordinateItem) -> bool:
        """
        Save coordinate data to Redis

        Args:
            ip: IP address (used as key)
            data: CoordinateItem containing lat, lon, city, country

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            client = self.redis_client.instance()
            json_data = data.model_dump_json(exclude={"ip"})
            client.set(str(ip), json_data)
            logger.info(f"Saved coordinates for IP: {ip}")
            return True
        except redis.RedisError as e:
            logger.error(f"Failed to save coordinate for IP {ip}: {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Failed to serialize data for IP {ip}: {e}")
            return False

    def get_all_coordinates(self) -> List[dict]:
        """
        Retrieve all stored coordinates from Redis

        Returns:
            List of coordinate dictionaries with IP addresses
        """
        try:
            client = self.redis_client.instance()
            keys = client.keys("*")

            coordinates: List[dict] = []
            for key in keys:
                try:
                    value = client.get(key)
                    if value:
                        coord_data = json.loads(value)
                        coord_data["ip"] = key
                        coordinates.append(coord_data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse data for key {key}: {e}")
                    continue

            logger.info(f"Retrieved {len(coordinates)} coordinates from Redis")
            return coordinates
        except redis.RedisError as e:
            logger.error(f"Failed to retrieve coordinates: {e}")
            raise
