"""
Redis cache client for notification system.

This module provides a Redis-based caching layer with:
- 30-second TTL for notification summary data
- Cache key generation based on user context
- Automatic cache invalidation on notification updates
"""

import json
import os
from typing import Optional, Any, Dict
from redis import Redis, ConnectionPool
from redis.exceptions import RedisError


class RedisCache:
    """
    Redis cache client for notification system.
    
    Provides caching functionality with automatic TTL management and
    cache invalidation support.
    """
    
    # Cache TTL in seconds (30 seconds as per design)
    NOTIFICATION_SUMMARY_TTL = 30
    
    # Cache key prefixes
    NOTIFICATION_SUMMARY_PREFIX = "notification:summary"
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
        max_connections: int = 10
    ):
        """
        Initialize Redis cache client.
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (optional)
            decode_responses: Whether to decode responses to strings
            max_connections: Maximum number of connections in the pool
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        
        # Create connection pool
        self.pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses,
            max_connections=max_connections
        )
        
        # Create Redis client
        self.client = Redis(connection_pool=self.pool)
        
    def _generate_summary_cache_key(
        self,
        user_id: str,
        tab: str = "all",
        include_read: bool = False
    ) -> str:
        """
        Generate cache key for notification summary.
        
        Cache key format: notification:summary:{user_id}:{tab}:{include_read}
        
        Args:
            user_id: User ID
            tab: Tab type (message/exception/all)
            include_read: Whether to include read notifications
        
        Returns:
            str: Cache key
        """
        return f"{self.NOTIFICATION_SUMMARY_PREFIX}:{user_id}:{tab}:{int(include_read)}"
    
    def get_notification_summary(
        self,
        user_id: str,
        tab: str = "all",
        include_read: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached notification summary.
        
        Args:
            user_id: User ID
            tab: Tab type (message/exception/all)
            include_read: Whether to include read notifications
        
        Returns:
            Optional[Dict[str, Any]]: Cached notification summary or None if not found
        """
        try:
            cache_key = self._generate_summary_cache_key(user_id, tab, include_read)
            cached_data = self.client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
        
        except RedisError as e:
            # Log error but don't fail the request
            print(f"Redis get error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            # Log error and return None for invalid JSON
            print(f"JSON decode error: {str(e)}")
            return None
    
    def set_notification_summary(
        self,
        user_id: str,
        data: Dict[str, Any],
        tab: str = "all",
        include_read: bool = False,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache notification summary data.
        
        Args:
            user_id: User ID
            data: Notification summary data to cache
            tab: Tab type (message/exception/all)
            include_read: Whether to include read notifications
            ttl: Time to live in seconds (default: 30 seconds)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_key = self._generate_summary_cache_key(user_id, tab, include_read)
            cache_ttl = ttl if ttl is not None else self.NOTIFICATION_SUMMARY_TTL
            
            # Serialize data to JSON
            json_data = json.dumps(data)
            
            # Set with TTL
            self.client.setex(cache_key, cache_ttl, json_data)
            
            return True
        
        except RedisError as e:
            # Log error but don't fail the request
            print(f"Redis set error: {str(e)}")
            return False
        except (TypeError, ValueError) as e:
            # Log error for serialization issues
            print(f"JSON serialization error: {str(e)}")
            return False
    
    def invalidate_notification_summary(
        self,
        user_id: Optional[str] = None
    ) -> int:
        """
        Invalidate notification summary cache.
        
        If user_id is provided, only invalidate cache for that user.
        If user_id is None, invalidate cache for all users.
        
        Args:
            user_id: User ID (optional, None = invalidate all)
        
        Returns:
            int: Number of keys deleted
        """
        try:
            if user_id:
                # Invalidate cache for specific user
                pattern = f"{self.NOTIFICATION_SUMMARY_PREFIX}:{user_id}:*"
            else:
                # Invalidate cache for all users
                pattern = f"{self.NOTIFICATION_SUMMARY_PREFIX}:*"
            
            # Find all matching keys
            keys = list(self.client.scan_iter(match=pattern))
            
            if keys:
                # Delete all matching keys
                return self.client.delete(*keys)
            
            return 0
        
        except RedisError as e:
            # Log error but don't fail the request
            print(f"Redis invalidate error: {str(e)}")
            return 0
    
    def ping(self) -> bool:
        """
        Check if Redis connection is alive.
        
        Returns:
            bool: True if connection is alive, False otherwise
        """
        try:
            return self.client.ping()
        except RedisError:
            return False
    
    def close(self) -> None:
        """
        Close Redis connection pool.
        """
        try:
            self.pool.disconnect()
        except RedisError as e:
            print(f"Redis close error: {str(e)}")


# Global Redis cache instance
_redis_cache: Optional[RedisCache] = None


def get_redis_cache() -> RedisCache:
    """
    Get or create global Redis cache instance.
    
    This function creates a singleton Redis cache instance based on
    environment variables:
    - REDIS_HOST: Redis server host (default: localhost)
    - REDIS_PORT: Redis server port (default: 6379)
    - REDIS_DB: Redis database number (default: 0)
    - REDIS_PASSWORD: Redis password (optional)
    
    Returns:
        RedisCache: Global Redis cache instance
    """
    global _redis_cache
    
    if _redis_cache is None:
        # Read configuration from environment
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "0"))
        password = os.getenv("REDIS_PASSWORD")
        
        # Create Redis cache instance
        _redis_cache = RedisCache(
            host=host,
            port=port,
            db=db,
            password=password
        )
    
    return _redis_cache
