"""
Unit tests for Admin API endpoints.

Tests cover:
- POST /api/v1/admin/rules/config endpoint
- Parameter validation
- System_Admin role requirement
- Cache invalidation after update
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.admin import (
    save_rule_config,
    require_system_admin,
    RuleConfigRequest
)
from auth.jwt_parser import UserContext
from models.rule_config import RuleConfig


class TestRequireSystemAdmin:
    """Tests for require_system_admin dependency."""
    
    def test_system_admin_authorized(self):
        """Test that System_Admin role is authorized."""
        user_context = UserContext(
            user_id="admin001",
            username="admin",
            roles=["System_Admin"],
            org_ids=["ORG001"],
            portfolio_ids=[],
            metadata={}
        )
        
        result = require_system_admin(user_context)
        assert result == user_context
    
    def test_non_admin_forbidden(self):
        """Test that non-admin users are forbidden."""
        user_context = UserContext(
            user_id="user001",
            username="user",
            roles=["BO_Operator"],
            org_ids=["ORG001"],
            portfolio_ids=[],
            metadata={}
        )
        
        with pytest.raises(HTTPException) as exc_info:
            require_system_admin(user_context)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "System_Admin role required" in exc_info.value.detail
    
    def test_no_roles_forbidden(self):
        """Test that users with no roles are forbidden."""
        user_context = UserContext(
            user_id="user001",
            username="user",
            roles=[],
            org_ids=["ORG001"],
            portfolio_ids=[],
            metadata={}
        )
        
        with pytest.raises(HTTPException) as exc_info:
            require_system_admin(user_context)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestRuleConfigRequest:
    """Tests for RuleConfigRequest validation."""
    
    def test_valid_request(self):
        """Test valid request data."""
        request = RuleConfigRequest(
            ruleCode="CHK_TRD_004",
            scheduledTime="14:30",
            targetRoles=["BO_Operator", "BO_Supervisor"],
            enabled=True,
            description="Test description"
        )
        
        assert request.ruleCode == "CHK_TRD_004"
        assert request.scheduledTime == "14:30"
        assert request.targetRoles == ["BO_Operator", "BO_Supervisor"]
        assert request.enabled is True
        assert request.description == "Test description"
    
    def test_invalid_scheduled_time_format(self):
        """Test that invalid scheduled time format is rejected."""
        with pytest.raises(ValueError):
            RuleConfigRequest(
                ruleCode="CHK_TRD_004",
                scheduledTime="25:00",  # Invalid hour
                targetRoles=["BO_Operator"],
                enabled=True
            )
        
        with pytest.raises(ValueError):
            RuleConfigRequest(
                ruleCode="CHK_TRD_004",
                scheduledTime="14:60",  # Invalid minute
                targetRoles=["BO_Operator"],
                enabled=True
            )
        
        with pytest.raises(ValueError):
            RuleConfigRequest(
                ruleCode="CHK_TRD_004",
                scheduledTime="14-30",  # Invalid format
                targetRoles=["BO_Operator"],
                enabled=True
            )
    
    def test_empty_target_roles(self):
        """Test that empty targetRoles is rejected."""
        with pytest.raises(ValueError) as exc_info:
            RuleConfigRequest(
                ruleCode="CHK_TRD_004",
                scheduledTime="14:30",
                targetRoles=[],
                enabled=True
            )
        
        # Pydantic v2 error message format
        assert "at least 1 item" in str(exc_info.value).lower()
    
    def test_optional_description(self):
        """Test that description is optional."""
        request = RuleConfigRequest(
            ruleCode="CHK_TRD_004",
            scheduledTime="14:30",
            targetRoles=["BO_Operator"],
            enabled=True
        )
        
        assert request.description is None


class TestSaveRuleConfig:
    """Tests for save_rule_config endpoint."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock(spec=Session)
        return db
    
    @pytest.fixture
    def admin_user(self):
        """Create admin user context."""
        return UserContext(
            user_id="admin001",
            username="admin",
            roles=["System_Admin"],
            org_ids=["ORG001"],
            portfolio_ids=[],
            metadata={}
        )
    
    @pytest.fixture
    def valid_request(self):
        """Create valid rule config request."""
        return RuleConfigRequest(
            ruleCode="CHK_TRD_004",
            scheduledTime="14:30",
            targetRoles=["BO_Operator", "BO_Supervisor"],
            enabled=True,
            description="Updated description"
        )
    
    def test_save_rule_config_success(self, mock_db, admin_user, valid_request):
        """Test successful rule configuration save."""
        # Mock existing rule config
        existing_rule = RuleConfig(
            id=1,
            rule_code="CHK_TRD_004",
            rule_name="交易复核提醒",
            scheduled_time="14:00",
            cron_expression="0 14 * * 1-5",
            target_roles=["BO_Operator"],
            enabled=False,
            description="Old description",
            query_sql="SELECT * FROM trades",
            timeout_seconds=10,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            updated_by="old_user"
        )
        
        # Mock database query
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = existing_rule
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Mock Redis cache
        mock_redis = Mock()
        mock_redis.invalidate_notification_summary.return_value = 5
        
        with patch('api.admin.get_redis_cache', return_value=mock_redis):
            # Call endpoint using asyncio.run
            response = asyncio.run(save_rule_config(valid_request, admin_user, mock_db))
        
        # Verify database operations
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(existing_rule)
        
        # Verify rule config was updated
        assert existing_rule.scheduled_time == "14:30"
        assert existing_rule.target_roles == ["BO_Operator", "BO_Supervisor"]
        assert existing_rule.enabled is True
        assert existing_rule.description == "Updated description"
        assert existing_rule.updated_by == "admin001"
        assert existing_rule.cron_expression == "30 14 * * 1-5"
        
        # Verify cache invalidation
        mock_redis.invalidate_notification_summary.assert_called_once()
        
        # Verify response
        assert response.code == 0
        assert "配置保存成功" in response.message
        assert response.data.ruleCode == "CHK_TRD_004"
        assert response.data.scheduledTime == "14:30"
        assert response.data.targetRoles == ["BO_Operator", "BO_Supervisor"]
        assert response.data.enabled is True
        assert response.data.updatedBy == "admin001"
    
    def test_save_rule_config_not_found(self, mock_db, admin_user, valid_request):
        """Test rule configuration not found."""
        # Mock database query returning None
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Call endpoint and expect 404
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(save_rule_config(valid_request, admin_user, mock_db))
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Rule configuration not found" in exc_info.value.detail
        
        # Verify rollback was called
        mock_db.rollback.assert_called_once()
    
    def test_save_rule_config_database_error(self, mock_db, admin_user, valid_request):
        """Test database error handling."""
        # Mock database query to raise exception
        mock_db.query.side_effect = Exception("Database connection error")
        
        # Call endpoint and expect 500
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(save_rule_config(valid_request, admin_user, mock_db))
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Internal server error" in exc_info.value.detail
        
        # Verify rollback was called
        mock_db.rollback.assert_called_once()
    
    def test_cron_expression_generation(self, mock_db, admin_user):
        """Test that cron expression is correctly generated from scheduled time."""
        # Test various scheduled times
        test_cases = [
            ("00:00", "00 00 * * 1-5"),  # Note: Python split() preserves leading zeros
            ("09:30", "30 09 * * 1-5"),
            ("14:30", "30 14 * * 1-5"),
            ("23:59", "59 23 * * 1-5"),
        ]
        
        for scheduled_time, expected_cron in test_cases:
            # Create request
            request = RuleConfigRequest(
                ruleCode="CHK_TRD_004",
                scheduledTime=scheduled_time,
                targetRoles=["BO_Operator"],
                enabled=True
            )
            
            # Mock existing rule config
            existing_rule = RuleConfig(
                id=1,
                rule_code="CHK_TRD_004",
                rule_name="Test Rule",
                scheduled_time="00:00",
                cron_expression="0 0 * * 1-5",
                target_roles=["BO_Operator"],
                enabled=True,
                query_sql="SELECT 1",
                timeout_seconds=10
            )
            
            # Mock database query
            mock_query = Mock()
            mock_filter = Mock()
            mock_filter.first.return_value = existing_rule
            mock_query.filter.return_value = mock_filter
            mock_db.query.return_value = mock_query
            
            # Mock Redis cache
            mock_redis = Mock()
            mock_redis.invalidate_notification_summary.return_value = 0
            
            with patch('api.admin.get_redis_cache', return_value=mock_redis):
                # Call endpoint
                response = asyncio.run(save_rule_config(request, admin_user, mock_db))
            
            # Verify cron expression
            assert existing_rule.cron_expression == expected_cron
            
            # Reset mock
            mock_db.reset_mock()
    
    def test_description_update_optional(self, mock_db, admin_user):
        """Test that description update is optional."""
        # Create request without description
        request = RuleConfigRequest(
            ruleCode="CHK_TRD_004",
            scheduledTime="14:30",
            targetRoles=["BO_Operator"],
            enabled=True
        )
        
        # Mock existing rule config with description
        existing_rule = RuleConfig(
            id=1,
            rule_code="CHK_TRD_004",
            rule_name="Test Rule",
            scheduled_time="14:00",
            cron_expression="0 14 * * 1-5",
            target_roles=["BO_Operator"],
            enabled=True,
            description="Original description",
            query_sql="SELECT 1",
            timeout_seconds=10
        )
        
        # Mock database query
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = existing_rule
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Mock Redis cache
        mock_redis = Mock()
        mock_redis.invalidate_notification_summary.return_value = 0
        
        with patch('api.admin.get_redis_cache', return_value=mock_redis):
            # Call endpoint
            asyncio.run(save_rule_config(request, admin_user, mock_db))
        
        # Verify description was not changed
        assert existing_rule.description == "Original description"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
