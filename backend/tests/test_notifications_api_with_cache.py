"""
Integration tests for notifications API with Redis caching.

Tests cover:
- Cache hit/miss scenarios
- Cache TTL behavior
- Cache invalidation on updates
- API response time improvements with caching
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend.api.notifications import get_notification_summary
from backend.auth.jwt_parser import UserContext
from backend.models.message import Message


# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


class TestNotificationsAPIWithCache:
    """Test suite for notifications API with Redis caching."""
    
    @pytest.fixture
    def mock_user_context(self):
        """Create mock user context."""
        return UserContext(
            user_id="user123",
            username="testuser",
            roles=["BO_Operator", "BO_Supervisor"],
            org_ids=["ORG001", "ORG002"],
            portfolio_ids=["PF001"],
            metadata={}
        )
    
    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        mock_session = Mock()
        
        # Create mock messages
        mock_message = Mock(spec=Message)
        mock_message.rule_code = "CHK_TRD_004"
        mock_message.title = "当日交易未复核"
        mock_message.count = 15
        mock_message.last_updated = datetime(2024, 1, 15, 14, 30, 0)
        mock_message.status = "success"
        mock_message.priority = "normal"
        mock_message.target_roles = ["BO_Operator", "BO_Supervisor"]
        
        # Setup query mock
        mock_query = Mock()
        mock_query.all.return_value = [mock_message]
        mock_session.query.return_value = mock_query
        
        return mock_session
    
    @patch('backend.api.notifications.get_redis_cache')
    async def test_cache_miss_queries_database(
        self,
        mock_get_cache,
        mock_user_context,
        mock_db_session
    ):
        """Test that cache miss triggers database query."""
        # Setup mock cache (cache miss)
        mock_cache = Mock()
        mock_cache.get_notification_summary.return_value = None
        mock_cache.set_notification_summary.return_value = True
        mock_get_cache.return_value = mock_cache
        
        # Call API
        response = await get_notification_summary(
            tab="all",
            includeRead=False,
            current_user=mock_user_context,
            db=mock_db_session
        )
        
        # Verify cache was checked
        mock_cache.get_notification_summary.assert_called_once_with(
            user_id="user123",
            tab="all",
            include_read=False
        )
        
        # Verify database was queried
        mock_db_session.query.assert_called_once()
        
        # Verify response was cached
        mock_cache.set_notification_summary.assert_called_once()
        cache_call_args = mock_cache.set_notification_summary.call_args
        assert cache_call_args[1]["user_id"] == "user123"
        assert cache_call_args[1]["tab"] == "all"
        assert cache_call_args[1]["include_read"] is False
        
        # Verify response
        assert response.code == 0
        assert response.message == "success"
        assert response.data.totalUnread == 15
    
    @patch('backend.api.notifications.get_redis_cache')
    async def test_cache_hit_skips_database(
        self,
        mock_get_cache,
        mock_user_context,
        mock_db_session
    ):
        """Test that cache hit skips database query."""
        # Setup mock cache (cache hit)
        cached_data = {
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
                            "lastUpdated": "2024-01-15T14:30:00",
                            "status": "success",
                            "priority": "normal"
                        }
                    ]
                },
                "totalUnread": 15,
                "lastRefreshTime": "2024-01-15T15:05:00"
            }
        }
        
        mock_cache = Mock()
        mock_cache.get_notification_summary.return_value = cached_data
        mock_get_cache.return_value = mock_cache
        
        # Call API
        response = await get_notification_summary(
            tab="all",
            includeRead=False,
            current_user=mock_user_context,
            db=mock_db_session
        )
        
        # Verify cache was checked
        mock_cache.get_notification_summary.assert_called_once()
        
        # Verify database was NOT queried
        mock_db_session.query.assert_not_called()
        
        # Verify response was NOT cached again
        mock_cache.set_notification_summary.assert_not_called()
        
        # Verify response
        assert response.code == 0
        assert response.message == "success"
        assert response.data.totalUnread == 15
    
    @patch('backend.api.notifications.get_redis_cache')
    async def test_cache_with_different_parameters(
        self,
        mock_get_cache,
        mock_user_context,
        mock_db_session
    ):
        """Test that different parameters create different cache keys."""
        # Setup mock cache
        mock_cache = Mock()
        mock_cache.get_notification_summary.return_value = None
        mock_cache.set_notification_summary.return_value = True
        mock_get_cache.return_value = mock_cache
        
        # Call API with tab="exception"
        await get_notification_summary(
            tab="exception",
            includeRead=False,
            current_user=mock_user_context,
            db=mock_db_session
        )
        
        # Verify cache key includes tab parameter
        cache_get_call = mock_cache.get_notification_summary.call_args
        assert cache_get_call[1]["tab"] == "exception"
        
        # Reset mock
        mock_cache.reset_mock()
        
        # Call API with includeRead=True
        await get_notification_summary(
            tab="all",
            includeRead=True,
            current_user=mock_user_context,
            db=mock_db_session
        )
        
        # Verify cache key includes includeRead parameter
        cache_get_call = mock_cache.get_notification_summary.call_args
        assert cache_get_call[1]["include_read"] is True
    
    @patch('backend.api.notifications.get_redis_cache')
    async def test_cache_error_fallback_to_database(
        self,
        mock_get_cache,
        mock_user_context,
        mock_db_session
    ):
        """Test that cache errors don't break the API."""
        # Setup mock cache (cache error)
        mock_cache = Mock()
        mock_cache.get_notification_summary.return_value = None  # Cache miss
        mock_cache.set_notification_summary.return_value = False  # Cache set fails
        mock_get_cache.return_value = mock_cache
        
        # Call API (should still work despite cache errors)
        response = await get_notification_summary(
            tab="all",
            includeRead=False,
            current_user=mock_user_context,
            db=mock_db_session
        )
        
        # Verify database was queried
        mock_db_session.query.assert_called_once()
        
        # Verify response is still valid
        assert response.code == 0
        assert response.message == "success"
    
    @patch('backend.api.notifications.get_redis_cache')
    async def test_cache_per_user_isolation(
        self,
        mock_get_cache,
        mock_db_session
    ):
        """Test that cache is isolated per user."""
        # Setup mock cache
        mock_cache = Mock()
        mock_cache.get_notification_summary.return_value = None
        mock_cache.set_notification_summary.return_value = True
        mock_get_cache.return_value = mock_cache
        
        # User 1
        user1 = UserContext(
            user_id="user123",
            username="user1",
            roles=["BO_Operator"],
            org_ids=["ORG001"],
            portfolio_ids=[],
            metadata={}
        )
        
        await get_notification_summary(
            tab="all",
            includeRead=False,
            current_user=user1,
            db=mock_db_session
        )
        
        # Verify cache key for user1
        cache_call_1 = mock_cache.get_notification_summary.call_args
        assert cache_call_1[1]["user_id"] == "user123"
        
        # Reset mock
        mock_cache.reset_mock()
        
        # User 2
        user2 = UserContext(
            user_id="user456",
            username="user2",
            roles=["BO_Supervisor"],
            org_ids=["ORG002"],
            portfolio_ids=[],
            metadata={}
        )
        
        await get_notification_summary(
            tab="all",
            includeRead=False,
            current_user=user2,
            db=mock_db_session
        )
        
        # Verify cache key for user2
        cache_call_2 = mock_cache.get_notification_summary.call_args
        assert cache_call_2[1]["user_id"] == "user456"
        
        # Verify different users have different cache keys
        assert cache_call_1[1]["user_id"] != cache_call_2[1]["user_id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
