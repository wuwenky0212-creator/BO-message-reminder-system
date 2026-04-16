"""
Example usage of Redis cache for notification system.

This script demonstrates:
1. Basic cache operations
2. Cache invalidation
3. Integration with notification API
"""

import os
import sys
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cache.redis_client import RedisCache, get_redis_cache
from cache.invalidation import invalidate_notification_cache, invalidate_all_notification_caches


def example_basic_operations():
    """Example 1: Basic cache operations."""
    print("=" * 60)
    print("Example 1: Basic Cache Operations")
    print("=" * 60)
    
    # Get cache instance
    cache = get_redis_cache()
    
    # Check connection
    if cache.ping():
        print("✓ Redis connection successful")
    else:
        print("✗ Redis connection failed")
        return
    
    # Prepare test data
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
                        "lastUpdated": datetime.now().isoformat(),
                        "status": "success",
                        "priority": "normal"
                    }
                ]
            },
            "totalUnread": 15,
            "lastRefreshTime": datetime.now().isoformat()
        }
    }
    
    # Set cache
    print("\n1. Setting cache for user123...")
    success = cache.set_notification_summary(
        user_id="user123",
        data=test_data,
        tab="all",
        include_read=False
    )
    print(f"   Cache set: {success}")
    
    # Get cache (should hit)
    print("\n2. Getting cache for user123...")
    cached_data = cache.get_notification_summary(
        user_id="user123",
        tab="all",
        include_read=False
    )
    if cached_data:
        print(f"   ✓ Cache hit! Total unread: {cached_data['data']['totalUnread']}")
    else:
        print("   ✗ Cache miss")
    
    # Get cache for different user (should miss)
    print("\n3. Getting cache for user456 (different user)...")
    cached_data = cache.get_notification_summary(
        user_id="user456",
        tab="all",
        include_read=False
    )
    if cached_data:
        print("   ✓ Cache hit")
    else:
        print("   ✗ Cache miss (expected - different user)")
    
    print()


def example_cache_invalidation():
    """Example 2: Cache invalidation."""
    print("=" * 60)
    print("Example 2: Cache Invalidation")
    print("=" * 60)
    
    cache = get_redis_cache()
    
    # Set cache for multiple users
    print("\n1. Setting cache for multiple users...")
    for user_id in ["user123", "user456", "user789"]:
        test_data = {
            "code": 0,
            "data": {"totalUnread": 10}
        }
        cache.set_notification_summary(user_id, test_data)
        print(f"   ✓ Cache set for {user_id}")
    
    # Verify cache exists
    print("\n2. Verifying cache exists...")
    for user_id in ["user123", "user456", "user789"]:
        cached = cache.get_notification_summary(user_id)
        status = "✓ Hit" if cached else "✗ Miss"
        print(f"   {status} for {user_id}")
    
    # Invalidate cache for specific user
    print("\n3. Invalidating cache for user123...")
    deleted = invalidate_notification_cache(user_id="user123")
    print(f"   Deleted {deleted} cache key(s)")
    
    # Verify user123 cache is gone
    print("\n4. Verifying user123 cache is invalidated...")
    cached = cache.get_notification_summary("user123")
    if cached:
        print("   ✗ Cache still exists (unexpected)")
    else:
        print("   ✓ Cache invalidated successfully")
    
    # Verify other users' cache still exists
    print("\n5. Verifying other users' cache still exists...")
    for user_id in ["user456", "user789"]:
        cached = cache.get_notification_summary(user_id)
        status = "✓ Still cached" if cached else "✗ Invalidated (unexpected)"
        print(f"   {status} for {user_id}")
    
    # Invalidate all caches
    print("\n6. Invalidating all caches...")
    deleted = invalidate_all_notification_caches()
    print(f"   Deleted {deleted} cache key(s)")
    
    # Verify all caches are gone
    print("\n7. Verifying all caches are invalidated...")
    for user_id in ["user456", "user789"]:
        cached = cache.get_notification_summary(user_id)
        status = "✓ Invalidated" if not cached else "✗ Still cached (unexpected)"
        print(f"   {status} for {user_id}")
    
    print()


def example_ttl_behavior():
    """Example 3: TTL behavior."""
    print("=" * 60)
    print("Example 3: TTL Behavior (30-second expiration)")
    print("=" * 60)
    
    cache = get_redis_cache()
    
    # Set cache with default TTL (30 seconds)
    print("\n1. Setting cache with 30-second TTL...")
    test_data = {"code": 0, "data": {"totalUnread": 5}}
    cache.set_notification_summary("user123", test_data)
    print("   ✓ Cache set")
    
    # Verify cache exists
    print("\n2. Verifying cache exists immediately...")
    cached = cache.get_notification_summary("user123")
    if cached:
        print("   ✓ Cache hit")
    else:
        print("   ✗ Cache miss (unexpected)")
    
    # Wait and check again
    print("\n3. Waiting 5 seconds and checking again...")
    time.sleep(5)
    cached = cache.get_notification_summary("user123")
    if cached:
        print("   ✓ Cache still exists (within TTL)")
    else:
        print("   ✗ Cache expired (unexpected)")
    
    print("\n   Note: Cache will expire after 30 seconds total")
    print("   To test expiration, wait 25 more seconds and check again")
    
    print()


def example_cache_key_variations():
    """Example 4: Cache key variations."""
    print("=" * 60)
    print("Example 4: Cache Key Variations")
    print("=" * 60)
    
    cache = get_redis_cache()
    
    # Set cache with different parameters
    print("\n1. Setting cache with different parameters...")
    
    test_data = {"code": 0, "data": {"totalUnread": 10}}
    
    # Same user, different tab
    cache.set_notification_summary("user123", test_data, tab="all")
    cache.set_notification_summary("user123", test_data, tab="exception")
    cache.set_notification_summary("user123", test_data, tab="message")
    print("   ✓ Set cache for user123 with different tabs")
    
    # Same user, different include_read
    cache.set_notification_summary("user123", test_data, include_read=False)
    cache.set_notification_summary("user123", test_data, include_read=True)
    print("   ✓ Set cache for user123 with different include_read")
    
    # Verify different cache keys
    print("\n2. Verifying different cache keys...")
    
    # Check tab variations
    for tab in ["all", "exception", "message"]:
        cached = cache.get_notification_summary("user123", tab=tab)
        status = "✓ Hit" if cached else "✗ Miss"
        print(f"   {status} for tab={tab}")
    
    # Check include_read variations
    for include_read in [False, True]:
        cached = cache.get_notification_summary("user123", include_read=include_read)
        status = "✓ Hit" if cached else "✗ Miss"
        print(f"   {status} for include_read={include_read}")
    
    print()


def example_error_handling():
    """Example 5: Error handling."""
    print("=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)
    
    # Try to connect to non-existent Redis
    print("\n1. Testing connection to non-existent Redis...")
    cache = RedisCache(host="nonexistent.redis.server", port=9999)
    
    if cache.ping():
        print("   ✗ Connection succeeded (unexpected)")
    else:
        print("   ✓ Connection failed (expected)")
    
    # Try to get cache (should return None gracefully)
    print("\n2. Testing cache get with failed connection...")
    cached = cache.get_notification_summary("user123")
    if cached is None:
        print("   ✓ Returned None gracefully (no exception)")
    else:
        print("   ✗ Returned data (unexpected)")
    
    # Try to set cache (should return False gracefully)
    print("\n3. Testing cache set with failed connection...")
    success = cache.set_notification_summary("user123", {"code": 0})
    if not success:
        print("   ✓ Returned False gracefully (no exception)")
    else:
        print("   ✗ Returned True (unexpected)")
    
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Redis Cache Examples for Notification System")
    print("=" * 60)
    print("\nPrerequisites:")
    print("- Redis server running on localhost:6379")
    print("- Or set REDIS_HOST and REDIS_PORT environment variables")
    print()
    
    try:
        # Run examples
        example_basic_operations()
        example_cache_invalidation()
        example_ttl_behavior()
        example_cache_key_variations()
        example_error_handling()
        
        print("=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure Redis is running:")
        print("  docker run -d -p 6379:6379 redis:7.0")


if __name__ == "__main__":
    main()
