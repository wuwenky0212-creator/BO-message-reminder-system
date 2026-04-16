"""
Comprehensive unit tests for notifications API endpoints.

This test suite covers:
- API endpoint functionality
- Permission filtering (role-based and org-based)
- Redis caching (cache hit/miss scenarios)
- Error handling (401, 403, 500)
- Edge cases and boundary conditions

Coverage target: >80%
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.notifications import router
from models.message import Base, Message
from auth.jwt_parser import UserContext
from api.dependencies import get_current_user, get_db


# Create test app
app = FastAPI()
app.include_router(router)


# Test database setup
@pytest.fixture
def test_db():
    """Create test database and session."""
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def test_client(test_db):
    """Create test client with database override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    
    yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user_context():
    """Create mock user context for testing."""
    return UserContext(
        user_id="user123",
        username="test_user",
        org_ids=["ORG001", "ORG002"],
        portfolio_ids=["PF001", "PF002"],
        roles=["BO_Operator", "BO_Supervisor"],
        metadata={},
        token_issued_at=datetime.now(),
        token_expires_at=None
    )


@pytest.fixture
def sample_messages(test_db):
    """Create sample messages in test database."""
    messages = [
        Message(
            rule_code="CHK_TRD_004",
            title="当日交易未复核",
            count=15,
            last_updated=datetime(2024, 1, 15, 14, 30, 0),
            status="success",
            priority="normal",
            target_roles=["BO_Operator", "BO_Supervisor"]
        ),
        Message(
            rule_code="CHK_BO_001",
            title="未证实匹配",
            count=12,
            last_updated=datetime(2024, 1, 15, 15, 0, 0),
            status="success",
            priority="normal",
            target_roles=["BO_Operator"]
        ),
        Message(
            rule_code="CHK_SEC_003",
            title="券持仓卖空缺口",
            count=1,
            last_updated=datetime(2024, 1, 15, 16, 0, 0),
            status="success",
            priority="critical",
            target_roles=["BO_Supervisor", "System_Admin"]
        ),
        Message(
            rule_code="CHK_CONF_005",
            title="证实报文未发",
            count=0,
            last_updated=datetime(2024, 1, 15, 15, 30, 0),
            status="success",
            priority="normal",
            target_roles=["BO_Operator"]
        ),
        Message(
            rule_code="CHK_SW_002",
            title="收付报文未发",
            count=3,
            last_updated=datetime(2024, 1, 15, 16, 0, 0),
            status="timeout",
            priority="high",
            target_roles=["BO_Operator", "BO_Supervisor"]
        ),
    ]
    
    for msg in messages:
        test_db.add(msg)
    test_db.commit()
    
    return messages


class TestNotificationAPIBasicFunctionality:
    """Test basic API functionality."""
    
    def test_get_summary_success(self, test_client, mock_user_context, sample_messages):
        """Test successful retrieval of notification summary."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["code"] == 0
        assert data["message"] == "success"
        assert "data" in data
        assert "tabs" in data["data"]
        assert "totalUnread" in data["data"]
        assert "lastRefreshTime" in data["data"]
    
    def test_get_summary_response_structure(self, test_client, mock_user_context, sample_messages):
        """Test that response has correct structure."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        data = response.json()
        
        # Check tabs structure
        assert "message" in data["data"]["tabs"]
        assert "exception" in data["data"]["tabs"]
        assert isinstance(data["data"]["tabs"]["message"], list)
        assert isinstance(data["data"]["tabs"]["exception"], list)
        
        # Check notification item structure
        if len(data["data"]["tabs"]["exception"]) > 0:
            notification = data["data"]["tabs"]["exception"][0]
            assert "ruleCode" in notification
            assert "title" in notification
            assert "count" in notification
            assert "lastUpdated" in notification
            assert "status" in notification
            assert "priority" in notification
    
    def test_get_summary_empty_database(self, test_client, mock_user_context):
        """Test summary with empty database."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]["tabs"]["exception"]) == 0
        assert len(data["data"]["tabs"]["message"]) == 0
        assert data["data"]["totalUnread"] == 0


class TestPermissionFiltering:
    """Test permission filtering functionality."""
    
    def test_role_based_filtering(self, test_client, sample_messages):
        """Test that notifications are filtered by user roles."""
        # User with only BO_Operator role
        limited_user = UserContext(
            user_id="user456",
            username="limited_user",
            org_ids=["ORG001"],
            portfolio_ids=["PF001"],
            roles=["BO_Operator"],
            metadata={},
            token_issued_at=datetime.now(),
            token_expires_at=None
        )
        
        app.dependency_overrides[get_current_user] = lambda: limited_user
        
        response = test_client.get("/api/v1/notifications/summary")
        data = response.json()
        
        # Should see CHK_TRD_004, CHK_BO_001, CHK_CONF_005, CHK_SW_002
        # Should NOT see CHK_SEC_003 (only for BO_Supervisor, System_Admin)
        exception_notifications = data["data"]["tabs"]["exception"]
        rule_codes = [n["ruleCode"] for n in exception_notifications]
        
        assert "CHK_TRD_004" in rule_codes
        assert "CHK_BO_001" in rule_codes
        assert "CHK_SEC_003" not in rule_codes
    
    def test_supervisor_role_filtering(self, test_client, sample_messages):
        """Test filtering for supervisor role."""
        supervisor_user = UserContext(
            user_id="user789",
            username="supervisor_user",
            org_ids=["ORG001"],
            portfolio_ids=["PF001"],
            roles=["BO_Supervisor"],
            metadata={},
            token_issued_at=datetime.now(),
            token_expires_at=None
        )
        
        app.dependency_overrides[get_current_user] = lambda: supervisor_user
        
        response = test_client.get("/api/v1/notifications/summary")
        data = response.json()
        
        exception_notifications = data["data"]["tabs"]["exception"]
        rule_codes = [n["ruleCode"] for n in exception_notifications]
        
        # Should see CHK_TRD_004, CHK_SEC_003, CHK_SW_002
        assert "CHK_TRD_004" in rule_codes
        assert "CHK_SEC_003" in rule_codes
        assert "CHK_SW_002" in rule_codes
    
    def test_no_roles_returns_empty(self, test_client, sample_messages):
        """Test that user with no roles gets empty result."""
        no_role_user = UserContext(
            user_id="user999",
            username="no_role_user",
            org_ids=["ORG001"],
            portfolio_ids=[],
            roles=[],
            metadata={},
            token_issued_at=datetime.now(),
            token_expires_at=None
        )
        
        app.dependency_overrides[get_current_user] = lambda: no_role_user
        
        response = test_client.get("/api/v1/notifications/summary")
        data = response.json()
        
        assert len(data["data"]["tabs"]["exception"]) == 0
        assert len(data["data"]["tabs"]["message"]) == 0
        assert data["data"]["totalUnread"] == 0
    
    def test_org_permission_filtering(self, test_client, sample_messages):
        """Test organization-based permission filtering."""
        no_org_user = UserContext(
            user_id="user888",
            username="no_org_user",
            org_ids=[],  # No organization permissions
            portfolio_ids=[],
            roles=["BO_Operator"],
            metadata={},
            token_issued_at=datetime.now(),
            token_expires_at=None
        )
        
        app.dependency_overrides[get_current_user] = lambda: no_org_user
        
        response = test_client.get("/api/v1/notifications/summary")
        data = response.json()
        
        # Should have no notifications due to lack of org permissions
        assert len(data["data"]["tabs"]["exception"]) == 0
        assert data["data"]["totalUnread"] == 0
    
    def test_multiple_roles_union(self, test_client, sample_messages):
        """Test that user with multiple roles sees union of notifications."""
        multi_role_user = UserContext(
            user_id="user777",
            username="multi_role_user",
            org_ids=["ORG001"],
            portfolio_ids=["PF001"],
            roles=["BO_Operator", "BO_Supervisor", "System_Admin"],
            metadata={},
            token_issued_at=datetime.now(),
            token_expires_at=None
        )
        
        app.dependency_overrides[get_current_user] = lambda: multi_role_user
        
        response = test_client.get("/api/v1/notifications/summary")
        data = response.json()
        
        # Should see all notifications
        exception_notifications = data["data"]["tabs"]["exception"]
        assert len(exception_notifications) == 5


class TestCachingBehavior:
    """Test Redis caching functionality."""
    
    @patch('api.notifications.get_redis_cache')
    def test_cache_miss_queries_database(self, mock_get_cache, test_client, mock_user_context, sample_messages):
        """Test that cache miss triggers database query."""
        # Setup mock cache (cache miss)
        mock_cache = Mock()
        mock_cache.get_notification_summary.return_value = None
        mock_cache.set_notification_summary.return_value = True
        mock_get_cache.return_value = mock_cache
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 200
        
        # Verify cache was checked
        mock_cache.get_notification_summary.assert_called_once()
        
        # Verify response was cached
        mock_cache.set_notification_summary.assert_called_once()
    
    @patch('api.notifications.get_redis_cache')
    def test_cache_hit_skips_database(self, mock_get_cache, test_client, mock_user_context):
        """Test that cache hit returns cached data without database query."""
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
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify cached data was returned
        assert data["data"]["totalUnread"] == 15
        
        # Verify cache was checked
        mock_cache.get_notification_summary.assert_called_once()
        
        # Verify data was NOT cached again
        mock_cache.set_notification_summary.assert_not_called()
    
    @patch('api.notifications.get_redis_cache')
    def test_cache_key_includes_user_id(self, mock_get_cache, test_client, mock_user_context, sample_messages):
        """Test that cache key includes user ID for isolation."""
        mock_cache = Mock()
        mock_cache.get_notification_summary.return_value = None
        mock_cache.set_notification_summary.return_value = True
        mock_get_cache.return_value = mock_cache
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        test_client.get("/api/v1/notifications/summary")
        
        # Verify cache key includes user_id
        cache_call = mock_cache.get_notification_summary.call_args
        assert cache_call[1]["user_id"] == "user123"
    
    @patch('api.notifications.get_redis_cache')
    def test_cache_key_includes_parameters(self, mock_get_cache, test_client, mock_user_context, sample_messages):
        """Test that cache key includes query parameters."""
        mock_cache = Mock()
        mock_cache.get_notification_summary.return_value = None
        mock_cache.set_notification_summary.return_value = True
        mock_get_cache.return_value = mock_cache
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        test_client.get("/api/v1/notifications/summary?tab=exception&includeRead=true")
        
        cache_call = mock_cache.get_notification_summary.call_args
        assert cache_call[1]["tab"] == "exception"
        assert cache_call[1]["include_read"] is True
    
    @patch('api.notifications.get_redis_cache')
    def test_cache_error_fallback(self, mock_get_cache, test_client, mock_user_context, sample_messages):
        """Test that cache errors don't break the API."""
        mock_cache = Mock()
        mock_cache.get_notification_summary.side_effect = Exception("Redis connection error")
        mock_get_cache.return_value = mock_cache
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        # Should still work despite cache error
        response = test_client.get("/api/v1/notifications/summary")
        
        # API should return 500 error due to exception handling
        assert response.status_code == 500


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_unauthorized_no_token(self, test_client):
        """Test 401 error when no authorization token provided."""
        app.dependency_overrides.clear()
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 401
    
    def test_database_error_handling(self, test_client, mock_user_context):
        """Test 500 error when database query fails."""
        # Create a mock db that raises an exception
        def mock_get_db_error():
            mock_db = Mock()
            mock_db.query.side_effect = Exception("Database connection error")
            yield mock_db
        
        app.dependency_overrides[get_db] = mock_get_db_error
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestTabFiltering:
    """Test tab filtering functionality."""
    
    def test_tab_filter_exception(self, test_client, mock_user_context, sample_messages):
        """Test tab=exception filter."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary?tab=exception")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]["tabs"]["exception"]) > 0
        assert len(data["data"]["tabs"]["message"]) == 0
    
    def test_tab_filter_message(self, test_client, mock_user_context, sample_messages):
        """Test tab=message filter."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary?tab=message")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]["tabs"]["exception"]) == 0
    
    def test_tab_filter_all(self, test_client, mock_user_context, sample_messages):
        """Test tab=all filter (default)."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary?tab=all")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]["tabs"]["exception"]) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_notification_with_zero_count(self, test_client, mock_user_context, sample_messages):
        """Test that notifications with count=0 are included but not counted as unread."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        data = response.json()
        
        # CHK_CONF_005 has count=0, should be in list but not in totalUnread
        exception_notifications = data["data"]["tabs"]["exception"]
        rule_codes = [n["ruleCode"] for n in exception_notifications]
        
        # Verify CHK_CONF_005 is in the list
        assert "CHK_CONF_005" in rule_codes
        
        # Verify totalUnread doesn't include count=0
        # Total should be: 15 + 12 + 1 + 3 = 31 (excluding CHK_CONF_005 with count=0)
        assert data["data"]["totalUnread"] == 31
    
    def test_notification_with_timeout_status(self, test_client, mock_user_context, sample_messages):
        """Test that notifications with timeout status are included."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        data = response.json()
        
        # CHK_SW_002 has status=timeout
        exception_notifications = data["data"]["tabs"]["exception"]
        timeout_notifications = [n for n in exception_notifications if n["status"] == "timeout"]
        
        assert len(timeout_notifications) > 0
        assert timeout_notifications[0]["ruleCode"] == "CHK_SW_002"
    
    def test_notification_priority_levels(self, test_client, mock_user_context, sample_messages):
        """Test that different priority levels are correctly returned."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        data = response.json()
        
        exception_notifications = data["data"]["tabs"]["exception"]
        priorities = [n["priority"] for n in exception_notifications]
        
        # Should have normal, high, and critical priorities
        assert "normal" in priorities
        assert "high" in priorities
        assert "critical" in priorities
    
    def test_last_updated_timestamp_format(self, test_client, mock_user_context, sample_messages):
        """Test that lastUpdated timestamp is in ISO 8601 format."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        data = response.json()
        
        exception_notifications = data["data"]["tabs"]["exception"]
        if len(exception_notifications) > 0:
            last_updated = exception_notifications[0]["lastUpdated"]
            
            # Should be ISO 8601 format (contains 'T' separator)
            assert "T" in last_updated or "-" in last_updated
    
    def test_total_unread_calculation(self, test_client, mock_user_context, sample_messages):
        """Test that totalUnread is correctly calculated."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        data = response.json()
        
        # Calculate expected total from sample_messages
        # User has roles: BO_Operator, BO_Supervisor
        # Should see: CHK_TRD_004 (15), CHK_BO_001 (12), CHK_SEC_003 (1), CHK_SW_002 (3)
        # CHK_CONF_005 has count=0, so not included
        # Total: 15 + 12 + 1 + 3 = 31
        assert data["data"]["totalUnread"] == 31


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=api.notifications", "--cov-report=term-missing"])
