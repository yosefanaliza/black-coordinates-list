import json
import os
import logging
from typing import List, Optional, Dict, Any
import redis

logger = logging.getLogger(__name__)

# Global Redis client
_redis_client: Optional[redis.Redis] = None


def connect_redis() -> None:
    """Initialize Redis connection using environment variables"""
    global _redis_client

    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_db = int(os.getenv("REDIS_DB", "0"))

    try:
        _redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True
        )
        # Test connection
        _redis_client.ping()
        logger.info(f"Successfully connected to Redis at {redis_host}:{redis_port}")
    except redis.RedisError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise


def close_redis() -> None:
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        _redis_client.close()
        logger.info("Redis connection closed")


def get_redis_client() -> redis.Redis:
    """Get the active Redis client"""
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized. Call connect_redis() first.")
    return _redis_client


def is_redis_connected() -> bool:
    """Check if Redis is connected"""
    try:
        if _redis_client is None:
            return False
        _redis_client.ping()
        return True
    except (redis.RedisError, Exception):
        return False


def save_coordinate(ip: str, data: Dict[str, Any]) -> bool:
    """
    Save coordinate data to Redis

    Args:
        ip: IP address (used as key)
        data: Dictionary containing lat, lon, city, country

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_redis_client()
        json_data = json.dumps(data)
        client.set(ip, json_data)
        logger.info(f"Saved coordinates for IP: {ip}")
        return True
    except redis.RedisError as e:
        logger.error(f"Failed to save coordinate for IP {ip}: {e}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Failed to serialize data for IP {ip}: {e}")
        return False


def get_all_coordinates() -> List[Dict[str, Any]]:
    """
    Retrieve all stored coordinates from Redis

    Returns:
        List of coordinate dictionaries with IP addresses
    """
    try:
        client = get_redis_client()
        keys = client.keys("*")

        coordinates = []
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
