# Redis Cache Implementation

## Overview

This module implements Redis caching for the notification summary API with a 30-second TTL as specified in the design document.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Request Flow                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Check Cache  │
                    └───────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
            Cache Hit              Cache Miss
                │                       │
                ▼                       ▼
        ┌──────────────┐      ┌──────────────────┐
        │ Return Cache │      │  Query Database  │
        └──────────────┘      └──────────────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │   Cache Result   │
                              │   (TTL=30s)      │
                              └──────────────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │  Return Response │
                              └──────────────────┘
```

## Components

### 1. RedisCache Class (`redis_client.py`)

Main cache client with the following features:

- **Connection Management**: Connection pooling with configurable max connections
- **Cache Key Generation**: User-specific cache keys with parameters
- **TTL Management**: 30-second default TTL for notification summaries
- **Error Handling**: Graceful degradation on Redis errors
- **Cache Invalidation**: Support for user-specific and global invalidation

#### Cache Key Format

```
notification:summary:{user_id}:{tab}:{include_read}
```

Examples:
- `notification:summary:user123:all:0`
- `notification:summary:user456:exception:1`

### 2. Cache Invalidation (`invalidation.py`)

Utility functions for invalidating cache when notifications change:

```python
from backend.cache.invalidation import invalidate_notification_cache

# Invalidate cache for specific user
invalidate_notification_cache(user_id="user123")

# Invalidate cache for all users (after scheduled scan)
invalidate_notification_cache()
```

### 3. API Integration (`api/notifications.py`)

The notification summary API automatically uses Redis caching:

1. **Check cache first**: Try to get cached data
2. **Query database on miss**: If cache miss, query database
3. **Cache the result**: Store result with 30-second TTL
4. **Return response**: Return cached or fresh data

## Configuration

Redis connection is configured via environment variables:

```bash
REDIS_HOST=localhost      # Default: localhost
REDIS_PORT=6379          # Default: 6379
REDIS_DB=0               # Default: 0
REDIS_PASSWORD=secret    # Optional
```

## Usage Examples

### Basic Usage

```python
from backend.cache.redis_client import get_redis_cache

# Get Redis cache instance
cache = get_redis_cache()

# Check connection
if cache.ping():
    print("Redis connected!")

# Get cached notification summary
cached_data = cache.get_notification_summary(
    user_id="user123",
    tab="all",
    include_read=False
)

if cached_data:
    print("Cache hit!")
else:
    print("Cache miss - query database")
    
    # ... query database ...
    
    # Cache the result
    cache.set_notification_summary(
        user_id="user123",
        data=response_data,
        tab="all",
        include_read=False
    )
```

### Cache Invalidation

```python
from backend.cache.invalidation import (
    invalidate_notification_cache,
    invalidate_all_notification_caches
)

# After user completes an approval
def on_trade_approved(user_id: str, trade_id: str):
    # ... update database ...
    
    # Invalidate user's cache
    invalidate_notification_cache(user_id=user_id)

# After scheduled scan updates notification counts
def on_scan_completed(rule_code: str):
    # ... update message table ...
    
    # Invalidate all users' cache
    invalidate_all_notification_caches()
```

## Performance Benefits

### Without Cache
- Every API request queries the database
- Response time: ~200-500ms (depending on data volume)
- Database load: High

### With Cache (30-second TTL)
- First request: Cache miss, queries database (~200-500ms)
- Subsequent requests (within 30s): Cache hit (~5-10ms)
- Database load: Reduced by ~95% (assuming 30-second refresh interval)

### Example Metrics

For a user refreshing the notification panel every 5 seconds:

**Without Cache:**
- 6 requests/30 seconds
- 6 database queries
- Total time: ~1200-3000ms

**With Cache:**
- 6 requests/30 seconds
- 1 database query (first request)
- 5 cache hits
- Total time: ~250-550ms (78-82% improvement)

## Cache Invalidation Strategy

### When to Invalidate

1. **User-Specific Invalidation**:
   - After user completes a business operation (approval, matching, etc.)
   - When notification count changes for specific user

2. **Global Invalidation**:
   - After scheduled scans update notification counts
   - After bulk operations affecting multiple users
   - After system configuration changes

### Invalidation Patterns

```python
# Pattern 1: Invalidate after user action
@app.post("/api/v1/trades/{trade_id}/approve")
async def approve_trade(trade_id: str, user: UserContext):
    # Approve trade
    trade_service.approve(trade_id, user.user_id)
    
    # Invalidate cache
    invalidate_notification_cache(user_id=user.user_id)
    
    return {"status": "approved"}

# Pattern 2: Invalidate after scheduled scan
def scan_trade_approval():
    # Scan and update message table
    count = scan_pending_trades()
    update_message_table("CHK_TRD_004", count)
    
    # Invalidate all caches
    invalidate_all_notification_caches()
```

## Error Handling

The cache implementation includes comprehensive error handling:

1. **Redis Connection Errors**: Gracefully degrade to database queries
2. **Serialization Errors**: Log error and skip caching
3. **Timeout Errors**: Return None and query database

Example:

```python
try:
    cached_data = cache.get_notification_summary(user_id)
    if cached_data:
        return cached_data
except RedisError as e:
    # Log error but don't fail the request
    logger.error(f"Redis error: {e}")
    
# Fallback to database query
return query_database()
```

## Testing

### Unit Tests

Run Redis cache unit tests:

```bash
pytest backend/tests/test_redis_cache.py -v
```

Tests cover:
- Cache key generation
- Get/set operations
- TTL behavior
- Cache invalidation
- Error handling
- Connection management

### Manual Testing

1. **Start Redis**:
   ```bash
   docker run -d -p 6379:6379 redis:7.0
   ```

2. **Test cache hit/miss**:
   ```bash
   # First request (cache miss)
   curl -H "Authorization: Bearer <token>" \
        http://localhost:8000/api/v1/notifications/summary
   
   # Second request within 30s (cache hit)
   curl -H "Authorization: Bearer <token>" \
        http://localhost:8000/api/v1/notifications/summary
   ```

3. **Monitor Redis**:
   ```bash
   redis-cli monitor
   ```

## Monitoring

### Redis Metrics to Monitor

1. **Hit Rate**: `cache_hits / (cache_hits + cache_misses)`
2. **Memory Usage**: Monitor Redis memory consumption
3. **Connection Pool**: Monitor active/idle connections
4. **Eviction Rate**: Monitor key evictions

### Health Check

```python
from backend.cache.redis_client import get_redis_cache

cache = get_redis_cache()
if not cache.ping():
    # Alert: Redis connection failed
    logger.error("Redis health check failed")
```

## Future Enhancements

1. **Cache Warming**: Pre-populate cache before scheduled scans
2. **Distributed Caching**: Support Redis Cluster for high availability
3. **Cache Compression**: Compress large notification data
4. **Metrics Collection**: Integrate with Prometheus/Grafana
5. **Cache Versioning**: Support cache schema versioning

## Troubleshooting

### Cache Not Working

1. Check Redis connection:
   ```python
   cache = get_redis_cache()
   print(cache.ping())  # Should return True
   ```

2. Check environment variables:
   ```bash
   echo $REDIS_HOST
   echo $REDIS_PORT
   ```

3. Check Redis logs:
   ```bash
   docker logs <redis-container-id>
   ```

### High Cache Miss Rate

1. Check TTL configuration (should be 30 seconds)
2. Verify cache invalidation isn't too aggressive
3. Monitor user request patterns

### Memory Issues

1. Monitor Redis memory usage:
   ```bash
   redis-cli info memory
   ```

2. Configure max memory policy:
   ```bash
   redis-cli config set maxmemory-policy allkeys-lru
   ```

## References

- Design Document: `.kiro/specs/message-reminder/design.md` (Section 8.2)
- Redis Documentation: https://redis.io/docs/
- Python Redis Client: https://redis-py.readthedocs.io/
