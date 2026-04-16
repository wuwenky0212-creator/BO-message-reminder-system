"""
Demo server for Message Reminder System - No database dependencies required.
This server provides mock data for frontend preview.
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import random

app = FastAPI(
    title="Message Reminder System API (Demo)",
    description="Demo server with mock data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock notification data - 6条异常处理提醒
MOCK_NOTIFICATIONS = [
    {
        "ruleCode": "TRADE_REVIEW_001",
        "title": "未交易复核",
        "count": 23,
        "lastUpdated": "2026-04-16 15:47:36",
        "status": "pending",
        "priority": "high"
    },
    {
        "ruleCode": "CONFIRM_MATCH_002",
        "title": "未证实匹配",
        "count": 15,
        "lastUpdated": "2026-04-16 15:45:20",
        "status": "pending",
        "priority": "high"
    },
    {
        "ruleCode": "CONFIRM_MSG_003",
        "title": "证实报文未发送",
        "count": 8,
        "lastUpdated": "2026-04-16 15:42:15",
        "status": "pending",
        "priority": "critical"
    },
    {
        "ruleCode": "PAYMENT_MSG_004",
        "title": "收付报文未发送",
        "count": 12,
        "lastUpdated": "2026-04-16 15:40:08",
        "status": "pending",
        "priority": "critical"
    },
    {
        "ruleCode": "PAYMENT_APPROVAL_005",
        "title": "收付报文清算审批",
        "count": 6,
        "lastUpdated": "2026-04-16 15:38:52",
        "status": "pending",
        "priority": "high"
    },
    {
        "ruleCode": "BOND_SHORT_006",
        "title": "债券持仓卖空预警",
        "count": 4,
        "lastUpdated": "2026-04-16 15:35:30",
        "status": "warning",
        "priority": "critical"
    }
]

# Mock position data
MOCK_POSITIONS = [
    {
        "securityCode": "600000.SH",
        "securityName": "浦发银行",
        "availableBalance": -5000.0,
        "settlementDate": "T+1",
        "portfolioCode": "PF001",
        "portfolioName": "自营组合1",
        "securityType": "Stock",
        "marketValue": -50000.00,
        "currency": "CNY"
    },
    {
        "securityCode": "000001.SZ",
        "securityName": "平安银行",
        "availableBalance": -3000.0,
        "settlementDate": "T+1",
        "portfolioCode": "PF002",
        "portfolioName": "自营组合2",
        "securityType": "Stock",
        "marketValue": -30000.00,
        "currency": "CNY"
    },
    {
        "securityCode": "601318.SH",
        "securityName": "中国平安",
        "availableBalance": -2000.0,
        "settlementDate": "T+1",
        "portfolioCode": "PF001",
        "portfolioName": "自营组合1",
        "securityType": "Stock",
        "marketValue": -20000.00,
        "currency": "CNY"
    }
]


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Message Reminder System API (Demo Mode)",
        "version": "1.0.0",
        "mode": "demo",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mode": "demo",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/notifications/summary")
async def get_notification_summary(
    tab: Optional[str] = Query("all", description="Tab type: message/exception/all"),
    includeRead: Optional[bool] = Query(False, description="Include read notifications")
):
    """Get notification summary with mock data."""
    
    # Return the 6 exception notifications
    notifications = []
    total_unread = 0
    
    for notif in MOCK_NOTIFICATIONS:
        notifications.append({
            **notif,
            "lastUpdated": notif["lastUpdated"]
        })
        total_unread += notif["count"]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "tabs": {
                "message": [],
                "exception": notifications if tab in ["exception", "all"] else []
            },
            "totalUnread": total_unread,
            "lastRefreshTime": datetime.now().isoformat()
        }
    }


@app.get("/api/v1/positions/projected_shortfall")
async def get_projected_shortfall(
    date: str = Query(..., description="Settlement date (T/T+1)"),
    portfolio: Optional[str] = Query(None, description="Portfolio code filter"),
    securityType: Optional[str] = Query(None, description="Security type filter"),
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(50, ge=1, le=100, description="Page size")
):
    """Query projected settlement positions with shortfalls (mock data)."""
    
    if date not in ['T', 'T+1']:
        return {
            "code": 400,
            "message": "Invalid date parameter. Must be 'T' or 'T+1'",
            "data": None
        }
    
    # Filter positions
    positions = MOCK_POSITIONS.copy()
    
    if portfolio:
        positions = [p for p in positions if p["portfolioCode"] == portfolio]
    
    if securityType:
        positions = [p for p in positions if p["securityType"] == securityType]
    
    # Calculate pagination
    total = len(positions)
    total_pages = (total + pageSize - 1) // pageSize if total > 0 else 0
    start = (page - 1) * pageSize
    end = start + pageSize
    paginated_positions = positions[start:end]
    
    # Calculate summary
    total_shortfall_value = sum(p["marketValue"] for p in positions)
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": paginated_positions,
            "pagination": {
                "page": page,
                "pageSize": pageSize,
                "total": total,
                "totalPages": total_pages
            },
            "summary": {
                "totalShortfallCount": total,
                "totalShortfallValue": total_shortfall_value,
                "queryDate": date
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting demo server...")
    print("Frontend should connect to: http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
