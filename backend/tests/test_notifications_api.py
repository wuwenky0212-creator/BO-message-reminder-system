"""
Unit tests for notifications API endpoints.

Tests the GET /api/v1/notifications/summary endpoint with various scenarios:
- Successful retrieval with valid token
- Permission filtering based on user roles
- Tab filtering (message/exception/all)
- Error handling (401, 403, 500)
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
from unittest.mock import Mock, patch

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
    # Use a unique in-memory database with StaticPool to ensure same connection
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool  # Use StaticPool to ensure same connection is reused
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
    # Store the test_db session to be reused
    def override_get_db():
        try:
            yield test_db
        finally:
            # Don't close the session here, let test_db fixture handle it
            pass
    
    # Override the dependency before creating the client
    app.dependency_overrides[get_db] = override_get_db
    
    # Create the test client
    client = TestClient(app)
    
    yield client
    
    # Clean up overrides after test
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
    ]
    
    for msg in messages:
        test_db.add(msg)
    test_db.commit()
    
    return messages


class TestNotificationSummaryEndpoint:
    """Test cases for GET /api/v1/notifications/summary endpoint."""
    
    def test_get_summary_success(self, test_client, mock_user_context, sample_messages):
        """Test successful retrieval of notification summary."""
        # Override authentication dependency
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        # Make request
        response = test_client.get("/api/v1/notifications/summary")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert data["code"] == 0
        assert data["message"] == "success"
        assert "data" in data
        assert "tabs" in data["data"]
        assert "totalUnread" in data["data"]
        assert "lastRefreshTime" in data["data"]
        
        # Check that notifications are returned
        exception_notifications = data["data"]["tabs"]["exception"]
        assert len(exception_notifications) > 0
        
        # Verify total unread count (sum of counts > 0)
        # User has roles: BO_Operator, BO_Supervisor
        # Should see: CHK_TRD_004 (15), CHK_BO_001 (12), CHK_SEC_003 (1)
        # Total: 15 + 12 + 1 = 28
        assert data["data"]["totalUnread"] == 28
    
    def test_get_summary_with_tab_filter_exception(self, test_client, mock_user_context, sample_messages):
        """Test summary with tab=exception filter."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary?tab=exception")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have exception tab notifications
        assert len(data["data"]["tabs"]["exception"]) > 0
        # Message tab should be empty when tab=exception
        assert len(data["data"]["tabs"]["message"]) == 0
    
    def test_get_summary_with_tab_filter_message(self, test_client, mock_user_context, sample_messages):
        """Test summary with tab=message filter."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary?tab=message")
        
        assert response.status_code == 200
        data = response.json()
        
        # Exception tab should be empty when tab=message
        assert len(data["data"]["tabs"]["exception"]) == 0
    
    def test_get_summary_with_tab_filter_all(self, test_client, mock_user_context, sample_messages):
        """Test summary with tab=all filter (default)."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary?tab=all")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have exception tab notifications (all go to exception for now)
        assert len(data["data"]["tabs"]["exception"]) > 0
    
    def test_get_summary_permission_filtering(self, test_client, sample_messages):
        """Test that notifications are filtered by user roles."""
        # Create user with only BO_Operator role
        limited_user = UserContext(
            user_id="user456",
            username="limited_user",
            org_ids=["ORG001"],
            portfolio_ids=["PF001"],
            roles=["BO_Operator"],  # Only BO_Operator role
            metadata={},
            token_issued_at=datetime.now(),
            token_expires_at=None
        )
        
        app.dependency_overrides[get_current_user] = lambda: limited_user
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # User should only see notifications with BO_Operator in target_roles
        # CHK_TRD_004, CHK_BO_001, CHK_CONF_005
        exception_notifications = data["data"]["tabs"]["exception"]
        rule_codes = [n["ruleCode"] for n in exception_notifications]
        
        assert "CHK_TRD_004" in rule_codes  # Has BO_Operator
        assert "CHK_BO_001" in rule_codes   # Has BO_Operator
        assert "CHK_SEC_003" not in rule_codes  # Only has BO_Supervisor, System_Admin
    
    def test_get_summary_no_roles(self, test_client, sample_messages):
        """Test that user with no roles gets empty result."""
        no_role_user = UserContext(
            user_id="user789",
            username="no_role_user",
            org_ids=["ORG001"],
            portfolio_ids=[],
            roles=[],  # No roles
            metadata={},
            token_issued_at=datetime.now(),
            token_expires_at=None
        )
        
        app.dependency_overrides[get_current_user] = lambda: no_role_user
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have no notifications
        assert len(data["data"]["tabs"]["exception"]) == 0
        assert len(data["data"]["tabs"]["message"]) == 0
        assert data["data"]["totalUnread"] == 0
    
    def test_get_summary_no_org_permissions(self, test_client, sample_messages):
        """Test that user with no organization permissions gets empty result."""
        no_org_user = UserContext(
            user_id="user999",
            username="no_org_user",
            org_ids=[],  # No organization permissions
            portfolio_ids=[],
            roles=["BO_Operator"],  # Has role but no org permissions
            metadata={},
            token_issued_at=datetime.now(),
            token_expires_at=None
        )
        
        app.dependency_overrides[get_current_user] = lambda: no_org_user
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have no notifications due to lack of org permissions
        assert len(data["data"]["tabs"]["exception"]) == 0
        assert len(data["data"]["tabs"]["message"]) == 0
        assert data["data"]["totalUnread"] == 0
    
    def test_get_summary_with_org_permissions(self, test_client, sample_messages):
        """Test that user with organization permissions can see notifications."""
        user_with_orgs = UserContext(
            user_id="user888",
            username="user_with_orgs",
            org_ids=["ORG001", "ORG002"],  # Has org permissions
            portfolio_ids=["PF001"],
            roles=["BO_Operator"],
            metadata={},
            token_issued_at=datetime.now(),
            token_expires_at=None
        )
        
        app.dependency_overrides[get_current_user] = lambda: user_with_orgs
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should see notifications (has both role and org permissions)
        exception_notifications = data["data"]["tabs"]["exception"]
        assert len(exception_notifications) > 0
        
        # Should see CHK_TRD_004 and CHK_BO_001 (both have BO_Operator role)
        rule_codes = [n["ruleCode"] for n in exception_notifications]
        assert "CHK_TRD_004" in rule_codes
        assert "CHK_BO_001" in rule_codes
    
    def test_get_summary_unauthorized_no_token(self, test_client):
        """Test 401 error when no authorization token provided."""
        # Don't override get_current_user, so it will check for real token
        app.dependency_overrides.clear()
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 401
    
    def test_get_summary_notification_item_format(self, test_client, mock_user_context, sample_messages):
        """Test that notification items have correct format."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check first notification item format
        notifications = data["data"]["tabs"]["exception"]
        if len(notifications) > 0:
            notification = notifications[0]
            
            # Verify all required fields are present
            assert "ruleCode" in notification
            assert "title" in notification
            assert "count" in notification
            assert "lastUpdated" in notification
            assert "status" in notification
            assert "priority" in notification
            
            # Verify field types
            assert isinstance(notification["ruleCode"], str)
            assert isinstance(notification["title"], str)
            assert isinstance(notification["count"], int)
            assert isinstance(notification["lastUpdated"], str)
            assert isinstance(notification["status"], str)
            assert isinstance(notification["priority"], str)
    
    def test_get_summary_empty_database(self, test_client, mock_user_context):
        """Test summary with empty database."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty tabs
        assert len(data["data"]["tabs"]["exception"]) == 0
        assert len(data["data"]["tabs"]["message"]) == 0
        assert data["data"]["totalUnread"] == 0
    
    def test_get_summary_include_read_parameter(self, test_client, mock_user_context, sample_messages):
        """Test includeRead parameter (currently not implemented, but should not error)."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = test_client.get("/api/v1/notifications/summary?includeRead=true")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return valid response
        assert data["code"] == 0
        assert "data" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
