import os
import logging
from typing import Optional
import redis

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis connection manager"""

    def __init__(self):
        """Initialize Redis client configuration"""
        self.redis_host = os.getenv("REDIS_HOST", "redis")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self._client: Optional[redis.Redis] = None

    def connect(self) -> None:
        """Initialize Redis connection"""
        try:
            self._client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            self._client.ping()
            logger.info(f"Successfully connected to Redis at {self.redis_host}:{self.redis_port}")
        except redis.RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def close(self) -> None:
        """Close Redis connection"""
        if self._client:
            self._client.close()
            logger.info("Redis connection closed")
            self._client = None

    def instance(self) -> redis.Redis:
        """Get the active Redis client instance"""
        if self._client is None:
            raise RuntimeError("Redis client not initialized. Call connect() first.")
        return self._client

    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        try:
            if self._client is None:
                return False
            self._client.ping()
            return True
        except (redis.RedisError, Exception):
            return False


# Global Redis client instance
redis_client = RedisClient()
