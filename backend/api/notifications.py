"""
Notifications API endpoints.

This module provides REST API endpoints for the notification system:
- GET /api/v1/notifications/summary: Get aggregated notification summary

Permission Filtering Architecture:
===================================

This module implements a two-level permission filtering system:

1. Role-Based Filtering (target_roles):
   - Each notification message has a target_roles field specifying which roles can see it
   - Users must have at least one matching role to see a notification
   - Examples: BO_Operator, BO_Supervisor, System_Admin

2. Organization-Based Filtering (org_ids):
   - Users must have organization permissions (org_ids) to see any notifications
   - If a user has no org_ids, they see no notifications regardless of roles
   - This ensures users can only see data for organizations they have access to

Current Implementation:
-----------------------
- The Message table stores aggregated notification counts across all organizations
- Permission filtering is applied at the API level based on:
  * User's roles (from JWT token)
  * User's organization IDs (from JWT token)
  
- Role filtering: Checks if user has any role in message.target_roles
- Org filtering: Checks if user has any organization permissions (org_ids not empty)

Future Enhancement:
-------------------
When the Message table is extended to include org_id field, or when we query
business tables directly, we will apply more granular organization filtering:
- Filter notifications by specific organization IDs
- Show org-specific counts instead of aggregated counts
- Use PermissionFilter.apply_org_filter() for SQL-level filtering

For now, the combination of role-based and org-existence filtering provides
adequate security while maintaining performance with pre-aggregated counts.
"""

from datetime import datetime
from typing import Annotated, Optional, Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from auth.jwt_parser import UserContext
from auth.permission_filter import PermissionFilter
from models.message import Message
from api.dependencies import get_current_user, get_db
from cache.redis_client import get_redis_cache


# Create router
router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


# Response models
class NotificationItem(BaseModel):
    """Single notification item in the response."""
    ruleCode: str = Field(..., description="Rule code (e.g., CHK_TRD_004)")
    title: str = Field(..., description="Notification title")
    count: int = Field(..., description="Number of pending items")
    lastUpdated: str = Field(..., description="Last update timestamp (ISO 8601)")
    status: str = Field(..., description="Scan status: success/timeout/error")
    priority: str = Field(..., description="Priority: normal/high/critical")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "ruleCode": "CHK_TRD_004",
                "title": "当日交易未复核",
                "count": 15,
                "lastUpdated": "2024-01-15T14:30:00Z",
                "status": "success",
                "priority": "normal"
            }
        }
    }


class NotificationTabs(BaseModel):
    """Notification tabs grouping."""
    message: List[NotificationItem] = Field(default_factory=list, description="Message tab notifications")
    exception: List[NotificationItem] = Field(default_factory=list, description="Exception tab notifications")


class NotificationSummaryData(BaseModel):
    """Notification summary data."""
    tabs: NotificationTabs = Field(..., description="Notifications grouped by tabs")
    totalUnread: int = Field(..., description="Total unread notification count")
    lastRefreshTime: str = Field(..., description="Last refresh timestamp (ISO 8601)")


class NotificationSummaryResponse(BaseModel):
    """Response model for notification summary endpoint."""
    code: int = Field(0, description="Response code (0 = success)")
    message: str = Field("success", description="Response message")
    data: NotificationSummaryData = Field(..., description="Notification summary data")


class ErrorResponse(BaseModel):
    """Error response model."""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


@router.get(
    "/summary",
    response_model=NotificationSummaryResponse,
    responses={
        200: {"description": "Success", "model": NotificationSummaryResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        403: {"description": "Forbidden", "model": ErrorResponse},
        500: {"description": "Internal Server Error", "model": ErrorResponse},
    },
    summary="Get notification summary",
    description="Get aggregated notification summary with permission filtering"
)
async def get_notification_summary(
    tab: Annotated[Optional[str], Query(description="Tab type: message/exception/all")] = "all",
    includeRead: Annotated[Optional[bool], Query(description="Include read notifications")] = False,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> NotificationSummaryResponse:
    """
    Get notification summary with user permission filtering.
    
    This endpoint returns aggregated notification data grouped by tabs (message/exception).
    It applies user's organization and role permissions to filter the notifications.
    
    Implements Redis caching with 30-second TTL:
    - Cache key includes user_id, tab, and includeRead parameters
    - Cache is checked first before querying database
    - Cache is automatically invalidated when notifications are updated
    
    Args:
        tab: Tab type filter (message/exception/all), default: all
        includeRead: Whether to include read notifications, default: False
        current_user: Current authenticated user context
        db: Database session
    
    Returns:
        NotificationSummaryResponse: Aggregated notification summary
    
    Raises:
        HTTPException: 401 if unauthorized, 403 if forbidden, 500 if internal error
    """
    try:
        # Get Redis cache instance
        redis_cache = get_redis_cache()
        
        # Try to get cached data
        cached_data = redis_cache.get_notification_summary(
            user_id=current_user.user_id,
            tab=tab,
            include_read=includeRead
        )
        
        if cached_data:
            # Return cached response
            return NotificationSummaryResponse(**cached_data)
        
        # Cache miss - query database
        # Initialize permission filter
        permission_filter = PermissionFilter()
        
        # Query all messages from database
        query = db.query(Message)
        
        # Apply permission filtering based on target_roles
        # Filter messages where user has at least one matching role
        if current_user.roles:
            # Get all messages where target_roles intersects with user roles
            messages = query.all()
            filtered_messages = []
            
            for msg in messages:
                # Check if user has any of the target roles
                if msg.target_roles and isinstance(msg.target_roles, list):
                    if any(role in current_user.roles for role in msg.target_roles):
                        filtered_messages.append(msg)
                else:
                    # If no target_roles specified, include for all users
                    filtered_messages.append(msg)
        else:
            # No roles, return empty result
            filtered_messages = []
        
        # Apply organization permission filtering
        # Filter out notifications for organizations the user doesn't have access to
        # Note: This is a placeholder for future enhancement when Message table
        # includes org_id field or when we query business tables directly
        # For now, we rely on target_roles filtering which is sufficient for the current design
        if current_user.org_ids:
            # User has organization permissions
            # In future: filter by org_id when available in Message table
            # For now: all role-filtered messages are accessible
            pass
        else:
            # User has no organization permissions, return empty result
            filtered_messages = []
        
        # Group notifications by tab type
        message_tab_notifications = []
        exception_tab_notifications = []
        total_unread = 0
        
        for msg in filtered_messages:
            # Create notification item
            notification_item = NotificationItem(
                ruleCode=msg.rule_code,
                title=msg.title,
                count=msg.count,
                lastUpdated=msg.last_updated.isoformat() if msg.last_updated else datetime.now().isoformat(),
                status=msg.status,
                priority=msg.priority
            )
            
            # Determine tab based on rule code or metadata
            # For now, all notifications go to exception tab
            # TODO: Implement proper tab classification logic
            exception_tab_notifications.append(notification_item)
            
            # Count unread notifications (count > 0)
            if msg.count > 0:
                total_unread += msg.count
        
        # Filter by tab parameter
        tabs_data = NotificationTabs(
            message=message_tab_notifications if tab in ["message", "all"] else [],
            exception=exception_tab_notifications if tab in ["exception", "all"] else []
        )
        
        # Build response
        response_data = NotificationSummaryData(
            tabs=tabs_data,
            totalUnread=total_unread,
            lastRefreshTime=datetime.now().isoformat()
        )
        
        response = NotificationSummaryResponse(
            code=0,
            message="success",
            data=response_data
        )
        
        # Cache the response for 30 seconds
        redis_cache.set_notification_summary(
            user_id=current_user.user_id,
            data=response.model_dump(),
            tab=tab,
            include_read=includeRead
        )
        
        return response
    
    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error in get_notification_summary: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
