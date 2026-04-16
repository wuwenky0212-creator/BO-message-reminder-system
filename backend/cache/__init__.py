"""
Cache module for Redis-based caching.

This module provides Redis caching functionality for the notification system.
"""

from cache.redis_client import RedisCache, get_redis_cache

__all__ = ["RedisCache", "get_redis_cache"]
