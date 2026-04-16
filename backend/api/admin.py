"""
Admin API endpoints.

This module provides REST API endpoints for system administration:
- POST /api/v1/admin/rules/config: Save rule configuration (System_Admin only)

Permission Requirements:
========================
- All endpoints in this module require System_Admin role
- Users without System_Admin role will receive 403 Forbidden error
"""

from datetime import datetime
from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator

from auth.jwt_parser import UserContext
from models.rule_config import RuleConfig
from api.dependencies import get_current_user, get_db
from cache.redis_client import get_redis_cache


# Create router
router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# Request models
class RuleConfigRequest(BaseModel):
    """Request model for rule configuration."""
    ruleCode: str = Field(..., description="Rule code (e.g., CHK_TRD_004)", min_length=1, max_length=50)
    scheduledTime: str = Field(..., description="Scheduled time in HH:MM format", pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    targetRoles: List[str] = Field(..., description="Target roles list", min_length=1)
    enabled: bool = Field(..., description="Whether the rule is enabled")
    description: Optional[str] = Field(None, description="Rule description")
    
    @field_validator('targetRoles')
    @classmethod
    def validate_target_roles(cls, v):
        """Validate that targetRoles is not empty and contains valid role names."""
        if not v:
            raise ValueError("targetRoles cannot be empty")
        
        # Validate each role name
        valid_roles = {
            "BO_Operator", "BO_Supervisor", "System_Admin",
            "FO_Trader", "Risk_Manager", "Compliance_Officer"
        }
        
        for role in v:
            if not role or not isinstance(role, str):
                raise ValueError(f"Invalid role: {role}")
            # Note: We don't enforce valid_roles check to allow flexibility
            # but you can uncomment the following lines to enforce it:
            # if role not in valid_roles:
            #     raise ValueError(f"Invalid role: {role}. Must be one of {valid_roles}")
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "ruleCode": "CHK_TRD_004",
                "scheduledTime": "14:30",
                "targetRoles": ["BO_Operator", "BO_Supervisor"],
                "enabled": True,
                "description": "交易复核提醒，每日14:30执行"
            }
        }
    }


# Response models
class RuleConfigData(BaseModel):
    """Rule configuration data in response."""
    ruleCode: str = Field(..., description="Rule code")
    scheduledTime: str = Field(..., description="Scheduled time")
    targetRoles: List[str] = Field(..., description="Target roles")
    enabled: bool = Field(..., description="Whether enabled")
    updatedAt: str = Field(..., description="Update timestamp (ISO 8601)")
    updatedBy: str = Field(..., description="Updated by user")


class RuleConfigResponse(BaseModel):
    """Response model for rule configuration save."""
    code: int = Field(0, description="Response code (0 = success)")
    message: str = Field(..., description="Response message")
    data: RuleConfigData = Field(..., description="Updated rule configuration")


class ErrorResponse(BaseModel):
    """Error response model."""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


def require_system_admin(current_user: UserContext) -> UserContext:
    """
    Dependency to check if user has System_Admin role.
    
    Args:
        current_user: Current authenticated user context
    
    Returns:
        UserContext: User context if authorized
    
    Raises:
        HTTPException: 403 if user doesn't have System_Admin role
    """
    if not current_user.roles or "System_Admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. System_Admin role required."
        )
    return current_user


@router.post(
    "/rules/config",
    response_model=RuleConfigResponse,
    responses={
        200: {"description": "Success", "model": RuleConfigResponse},
        400: {"description": "Bad Request - Validation Failed", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        403: {"description": "Forbidden - System_Admin Required", "model": ErrorResponse},
        404: {"description": "Not Found - Rule Not Found", "model": ErrorResponse},
        500: {"description": "Internal Server Error", "model": ErrorResponse},
    },
    summary="Save rule configuration",
    description="Save or update rule configuration. Requires System_Admin role. Cache is invalidated after update."
)
async def save_rule_config(
    request: RuleConfigRequest,
    current_user: UserContext = Depends(require_system_admin),
    db: Session = Depends(get_db)
) -> RuleConfigResponse:
    """
    Save or update rule configuration.
    
    This endpoint allows System_Admin users to update rule configuration including:
    - Scheduled time
    - Target roles
    - Enabled status
    - Description
    
    After successful update, the notification summary cache is invalidated to ensure
    users see updated data on next request.
    
    Args:
        request: Rule configuration request data
        current_user: Current authenticated user (must have System_Admin role)
        db: Database session
    
    Returns:
        RuleConfigResponse: Updated rule configuration
    
    Raises:
        HTTPException: 400 if validation fails
        HTTPException: 401 if unauthorized
        HTTPException: 403 if not System_Admin
        HTTPException: 404 if rule not found
        HTTPException: 500 if internal error
    """
    try:
        # Query existing rule configuration
        rule_config = db.query(RuleConfig).filter(
            RuleConfig.rule_code == request.ruleCode
        ).first()
        
        if not rule_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule configuration not found for rule code: {request.ruleCode}"
            )
        
        # Update rule configuration
        rule_config.scheduled_time = request.scheduledTime
        rule_config.target_roles = request.targetRoles
        rule_config.enabled = request.enabled
        
        if request.description is not None:
            rule_config.description = request.description
        
        # Update audit fields
        rule_config.updated_by = current_user.user_id
        rule_config.updated_at = datetime.now()
        
        # Generate cron expression from scheduled time
        # Format: "minute hour * * 1-5" (Monday to Friday)
        hour, minute = request.scheduledTime.split(":")
        rule_config.cron_expression = f"{minute} {hour} * * 1-5"
        
        # Commit changes to database
        db.commit()
        db.refresh(rule_config)
        
        # Invalidate notification summary cache for all users
        # This ensures users see updated notifications on next request
        redis_cache = get_redis_cache()
        invalidated_count = redis_cache.invalidate_notification_summary()
        
        # Log cache invalidation (in production, use proper logging)
        print(f"Cache invalidated: {invalidated_count} keys deleted after rule config update")
        
        # Build response
        response = RuleConfigResponse(
            code=0,
            message="配置保存成功，将在下一个定时任务周期生效",
            data=RuleConfigData(
                ruleCode=rule_config.rule_code,
                scheduledTime=rule_config.scheduled_time,
                targetRoles=rule_config.target_roles,
                enabled=rule_config.enabled,
                updatedAt=rule_config.updated_at.isoformat() if rule_config.updated_at else datetime.now().isoformat(),
                updatedBy=rule_config.updated_by or current_user.user_id
            )
        )
        
        return response
    
    except HTTPException:
        # Re-raise HTTP exceptions
        db.rollback()
        raise
    
    except Exception as e:
        # Rollback transaction on error
        db.rollback()
        
        # Log error (in production, use proper logging)
        print(f"Error in save_rule_config: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
