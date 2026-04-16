"""
Unit tests for Redis cache functionality.

Tests cover:
- Cache key generation
- Cache get/set operations
- Cache TTL behavior
- Cache invalidation
- Error handling
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from redis.exceptions import RedisError

from backend.cache.redis_client import RedisCache, get_redis_cache
from backend.cache.invalidation import invalidate_notification_cache, invalidate_all_notification_caches


class TestRedisCache:
    """Test suite for RedisCache class."""
    
    def test_init_creates_connection_pool(self):
        """Test that RedisCache initializes with connection pool."""
        cache = RedisCache(
            host="localhost",
            port=6379,
            db=0,
            password=None
        )
        
        assert cache.host == "localhost"
        assert cache.port == 6379
        assert cache.db == 0
        assert cache.password is None
        assert cache.pool is not None
        assert cache.client is not None
    
    def test_generate_summary_cache_key(self):
        """Test cache key generation for notification summary."""
        cache = RedisCache()
        
        # Test with default parameters
        key1 = cache._generate_summary_cache_key("user123")
        assert key1 == "notification:summary:user123:all:0"
        
        # Test with custom tab
        key2 = cache._generate_summary_cache_key("user123", tab="exception")
        assert key2 == "notification:summary:user123:exception:0"
        
        # Test with include_read=True
        key3 = cache._generate_summary_cache_key("user123", include_read=True)
        assert key3 == "notification:summary:user123:all:1"
        
        # Test with all custom parameters
        key4 = cache._generate_summary_cache_key(
            "user456",
            tab="message",
            include_read=True
        )
        assert key4 == "notification:summary:user456:message:1"
    
    @patch('backend.cache.redis_client.Redis')
    def test_get_notification_summary_cache_hit(self, mock_redis_class):
        """Test getting cached notification summary (cache hit)."""
        # Setup mock
        mock_client = Mock()
        mock_redis_class.return_value = mock_client
        
        test_data = {
            "code": 0,
            "message": "success",
            "data": {
                "tabs": {
                    "message": [],
                    "exception": [
                        {
                            "ruleCode": "CHK_TRD_004",
                            "title": "当日交易未复核",
                            "count": 15,
                            "lastUpdated": "2024-01-15T14:30:00Z",
                            "status": "success",
                            "priority": "normal"
                        }
                    ]
                },
                "totalUnread": 15,
                "lastRefreshTime": "2024-01-15T15:05:00Z"
            }
        }
        
        mock_client.get.return_value = json.dumps(test_data)
        
        cache = RedisCache()
        cache.client = mock_client
        
        # Get cached data
        result = cache.get_notification_summary("user123")
        
        # Verify
        assert result == test_data
        mock_client.get.assert_called_once_with("notification:summary:user123:all:0")
    
    @patch('backend.cache.redis_client.Redis')
    def test_get_notification_summary_cache_miss(self, mock_redis_class):
        """Test getting cached notification summary (cache miss)."""
        # Setup mock
        mock_client = Mock()
        mock_redis_class.return_value = mock_client
        mock_client.get.return_value = None
        
        cache = RedisCache()
        cache.client = mock_client
        
        # Get cached data
        result = cache.get_notification_summary("user123")
        
        # Verify
        assert result is None
        mock_client.get.assert_called_once()
    
    @patch('backend.cache.redis_client.Redis')
    def test_get_notification_summary_redis_error(self, mock_redis_class):
        """Test getting cached data when Redis raises error."""
        # Setup mock
        mock_client = Mock()
        mock_redis_class.return_value = mock_client
        mock_client.get.side_effect = RedisError("Connection failed")
        
        cache = RedisCache()
        cache.client = mock_client
        
        # Get cached data (should return None on error)
        result = cache.get_notification_summary("user123")
        
        # Verify
        assert result is None
    
    @patch('backend.cache.redis_client.Redis')
    def test_set_notification_summary(self, mock_redis_class):
        """Test caching notification summary data."""
        # Setup mock
        mock_client = Mock()
        mock_redis_class.return_value = mock_client
        
        cache = RedisCache()
        cache.client = mock_client
        
        test_data = {
            "code": 0,
            "message": "success",
            "data": {"totalUnread": 15}
        }
        
        # Set cache
        result = cache.set_notification_summary("user123", test_data)
        
        # Verify
        assert result is True
        mock_client.setex.assert_called_once()
        
        # Verify cache key and TTL
        call_args = mock_client.setex.call_args
        assert call_args[0][0] == "notification:summary:user123:all:0"
        assert call_args[0][1] == 30  # TTL = 30 seconds
        assert json.loads(call_args[0][2]) == test_data
    
    @patch('backend.cache.redis_client.Redis')
    def test_set_notification_summary_custom_ttl(self, mock_redis_class):
        """Test caching with custom TTL."""
        # Setup mock
        mock_client = Mock()
        mock_redis_class.return_value = mock_client
        
        cache = RedisCache()
        cache.client = mock_client
        
        test_data = {"code": 0}
        
        # Set cache with custom TTL
        result = cache.set_notification_summary("user123", test_data, ttl=60)
        
        # Verify TTL
        call_args = mock_client.setex.call_args
        assert call_args[0][1] == 60
    
    @patch('backend.cache.redis_client.Redis')
    def test_set_notification_summary_redis_error(self, mock_redis_class):
        """Test caching when Redis raises error."""
        # Setup mock
        mock_client = Mock()
        mock_redis_class.return_value = mock_client
        mock_client.setex.side_effect = RedisError("Connection failed")
        
        cache = RedisCache()
        cache.client = mock_client
        
        # Set cache (should return False on error)
        result = cache.set_notification_summary("user123", {"code": 0})
        
        # Verify
        assert result is False
    
    @patch('backend.cache.redis_client.Redis')
    def test_invalidate_notification_summary_specific_user(self, mock_redis_class):
        """Test invalidating cache for specific user."""
        # Setup mock
        mock_client = Mock()
        mock_redis_class.return_value = mock_client
        
        # Mock scan_iter to return some keys
        mock_client.scan_iter.return_value = [
            "notification:summary:user123:all:0",
            "notification:summary:user123:exception:0"
        ]
        mock_client.delete.return_value = 2
        
        cache = RedisCache()
        cache.client = mock_client
        
        # Invalidate cache for user123
        deleted_count = cache.invalidate_notification_summary("user123")
        
        # Verify
        assert deleted_count == 2
        mock_client.scan_iter.assert_called_once_with(
            match="notification:summary:user123:*"
        )
        mock_client.delete.assert_called_once()
    
    @patch('backend.cache.redis_client.Redis')
    def test_invalidate_notification_summary_all_users(self, mock_redis_class):
        """Test invalidating cache for all users."""
        # Setup mock
        mock_client = Mock()
        mock_redis_class.return_value = mock_client
        
        # Mock scan_iter to return keys for multiple users
        mock_client.scan_iter.return_value = [
            "notification:summary:user123:all:0",
            "notification:summary:user456:all:0",
            "notification:summary:user789:exception:0"
        ]
        mock_client.delete.return_value = 3
        
        cache = RedisCache()
        cache.client = mock_client
        
        # Invalidate cache for all users
        deleted_count = cache.invalidate_notification_summary(user_id=None)
        
        # Verify
        assert deleted_count == 3
        mock_client.scan_iter.assert_called_once_with(
            match="notification:summary:*"
        )
    
    @patch('backend.cache.redis_client.Redis')
    def test_invalidate_notification_summary_no_keys(self, mock_redis_class):
        """Test invalidating cache when no keys exist."""
        # Setup mock
        mock_client = Mock()
        mock_redis_class.return_value = mock_client
        mock_client.scan_iter.return_value = []
        
        cache = RedisCache()
        cache.client = mock_client
        
        # Invalidate cache
        deleted_count = cache.invalidate_notification_summary("user123")
        
        # Verify
        assert deleted_count == 0
        mock_client.delete.assert_not_called()
    
    @patch('backend.cache.redis_client.Redis')
    def test_ping_success(self, mock_redis_class):
        """Test Redis connection check (success)."""
        # Setup mock
        mock_client = Mock()
        mock_redis_class.return_value = mock_client
        mock_client.ping.return_value = True
        
        cache = RedisCache()
        cache.client = mock_client
        
        # Check connection
        result = cache.ping()
        
        # Verify
        assert result is True
        mock_client.ping.assert_called_once()
    
    @patch('backend.cache.redis_client.Redis')
    def test_ping_failure(self, mock_redis_class):
        """Test Redis connection check (failure)."""
        # Setup mock
        mock_client = Mock()
        mock_redis_class.return_value = mock_client
        mock_client.ping.side_effect = RedisError("Connection failed")
        
        cache = RedisCache()
        cache.client = mock_client
        
        # Check connection
        result = cache.ping()
        
        # Verify
        assert result is False


class TestGetRedisCache:
    """Test suite for get_redis_cache function."""
    
    @patch('backend.cache.redis_client.RedisCache')
    @patch.dict('os.environ', {
        'REDIS_HOST': 'redis.example.com',
        'REDIS_PORT': '6380',
        'REDIS_DB': '1',
        'REDIS_PASSWORD': 'secret'
    })
    def test_get_redis_cache_from_env(self, mock_redis_cache_class):
        """Test creating Redis cache from environment variables."""
        # Clear global cache
        import backend.cache.redis_client as redis_module
        redis_module._redis_cache = None
        
        # Get cache
        cache = get_redis_cache()
        
        # Verify RedisCache was created with env vars
        mock_redis_cache_class.assert_called_once_with(
            host='redis.example.com',
            port=6380,
            db=1,
            password='secret'
        )
    
    @patch('backend.cache.redis_client.RedisCache')
    @patch.dict('os.environ', {}, clear=True)
    def test_get_redis_cache_defaults(self, mock_redis_cache_class):
        """Test creating Redis cache with default values."""
        # Clear global cache
        import backend.cache.redis_client as redis_module
        redis_module._redis_cache = None
        
        # Get cache
        cache = get_redis_cache()
        
        # Verify RedisCache was created with defaults
        mock_redis_cache_class.assert_called_once_with(
            host='localhost',
            port=6379,
            db=0,
            password=None
        )


class TestCacheInvalidation:
    """Test suite for cache invalidation utilities."""
    
    @patch('backend.cache.invalidation.get_redis_cache')
    def test_invalidate_notification_cache_specific_user(self, mock_get_cache):
        """Test invalidating cache for specific user."""
        # Setup mock
        mock_cache = Mock()
        mock_cache.invalidate_notification_summary.return_value = 2
        mock_get_cache.return_value = mock_cache
        
        # Invalidate cache
        deleted_count = invalidate_notification_cache("user123")
        
        # Verify
        assert deleted_count == 2
        mock_cache.invalidate_notification_summary.assert_called_once_with(
            user_id="user123"
        )
    
    @patch('backend.cache.invalidation.get_redis_cache')
    def test_invalidate_notification_cache_all_users(self, mock_get_cache):
        """Test invalidating cache for all users."""
        # Setup mock
        mock_cache = Mock()
        mock_cache.invalidate_notification_summary.return_value = 5
        mock_get_cache.return_value = mock_cache
        
        # Invalidate cache
        deleted_count = invalidate_notification_cache(user_id=None)
        
        # Verify
        assert deleted_count == 5
        mock_cache.invalidate_notification_summary.assert_called_once_with(
            user_id=None
        )
    
    @patch('backend.cache.invalidation.get_redis_cache')
    def test_invalidate_all_notification_caches(self, mock_get_cache):
        """Test convenience function for invalidating all caches."""
        # Setup mock
        mock_cache = Mock()
        mock_cache.invalidate_notification_summary.return_value = 10
        mock_get_cache.return_value = mock_cache
        
        # Invalidate all caches
        deleted_count = invalidate_all_notification_caches()
        
        # Verify
        assert deleted_count == 10
        mock_cache.invalidate_notification_summary.assert_called_once_with(
            user_id=None
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
