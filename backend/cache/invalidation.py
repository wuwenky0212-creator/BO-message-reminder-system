"""
Cache invalidation utilities for notification system.

This module provides functions to invalidate cache when notifications are updated.
Should be called from business logic when:
- Notification counts change (e.g., after approval, matching, sending)
- New notifications are created
- Notifications are deleted or marked as read
"""

from typing import Optional
from backend.cache.redis_client import get_redis_cache


def invalidate_notification_cache(user_id: Optional[str] = None) -> int:
    """
    Invalidate notification summary cache.
    
    This function should be called whenever notification data changes:
    - After a user completes a business operation (approval, matching, etc.)
    - After a scheduled scan creates/updates notifications
    - After notifications are marked as read
    
    Args:
        user_id: User ID to invalidate cache for (None = invalidate all users)
    
    Returns:
        int: Number of cache keys deleted
    
    Example:
        # Invalidate cache for specific user after they approve a trade
        invalidate_notification_cache(user_id="user123")
        
        # Invalidate cache for all users after scheduled scan
        invalidate_notification_cache()
    """
    redis_cache = get_redis_cache()
    return redis_cache.invalidate_notification_summary(user_id=user_id)


def invalidate_all_notification_caches() -> int:
    """
    Invalidate notification cache for all users.
    
    This is a convenience function that invalidates cache for all users.
    Should be called after scheduled scans that update notification counts.
    
    Returns:
        int: Number of cache keys deleted
    
    Example:
        # After CHK_TRD_004 scan completes
        invalidate_all_notification_caches()
    """
    return invalidate_notification_cache(user_id=None)
