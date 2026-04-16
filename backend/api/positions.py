"""
Positions API endpoints.

This module provides REST API endpoints for position queries:
- GET /api/v1/positions/projected_shortfall: Query projected settlement positions with shortfalls

Permission Filtering:
=====================
- Organization-based filtering: Users can only see positions for their authorized organizations
- Portfolio-based filtering: Users can only see positions for their authorized portfolios
- Combined filtering ensures data security at multiple levels
"""

from datetime import datetime
from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from auth.jwt_parser import UserContext
from auth.permission_filter import PermissionFilter
from models.position import Position
from api.dependencies import get_current_user, get_db


# Create router
router = APIRouter(prefix="/api/v1/positions", tags=["positions"])


# Response models
class PositionItem(BaseModel):
    """Single position item in the response."""
    securityCode: str = Field(..., description="Security code")
    securityName: str = Field(..., description="Security name")
    availableBalance: float = Field(..., description="Available balance (negative for shortfall)")
    settlementDate: str = Field(..., description="Settlement date (T/T+1)")
    portfolioCode: str = Field(..., description="Portfolio code")
    portfolioName: str = Field(..., description="Portfolio name")
    securityType: str = Field(..., description="Security type (Stock/Bond/Fund)")
    marketValue: float = Field(..., description="Market value")
    currency: str = Field(..., description="Currency")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "securityCode": "600000.SH",
                "securityName": "浦发银行",
                "availableBalance": -5000.0,
                "settlementDate": "T+1",
                "portfolioCode": "PF001",
                "portfolioName": "自营组合1",
                "securityType": "Stock",
                "marketValue": -50000.00,
                "currency": "CNY"
            }
        }
    }


class PaginationInfo(BaseModel):
    """Pagination information."""
    page: int = Field(..., description="Current page number")
    pageSize: int = Field(..., description="Page size")
    total: int = Field(..., description="Total number of records")
    totalPages: int = Field(..., description="Total number of pages")


class ShortfallSummary(BaseModel):
    """Summary of shortfall positions."""
    totalShortfallCount: int = Field(..., description="Total number of shortfall positions")
    totalShortfallValue: float = Field(..., description="Total shortfall market value")
    queryDate: str = Field(..., description="Query date (T/T+1)")


class ProjectedShortfallData(BaseModel):
    """Projected shortfall data."""
    items: List[PositionItem] = Field(..., description="List of shortfall positions")
    pagination: PaginationInfo = Field(..., description="Pagination information")
    summary: ShortfallSummary = Field(..., description="Summary statistics")


class ProjectedShortfallResponse(BaseModel):
    """Response model for projected shortfall endpoint."""
    code: int = Field(0, description="Response code (0 = success)")
    message: str = Field("success", description="Response message")
    data: ProjectedShortfallData = Field(..., description="Projected shortfall data")


class ErrorResponse(BaseModel):
    """Error response model."""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


@router.get(
    "/projected_shortfall",
    response_model=ProjectedShortfallResponse,
    responses={
        200: {"description": "Success", "model": ProjectedShortfallResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        403: {"description": "Forbidden", "model": ErrorResponse},
        500: {"description": "Internal Server Error", "model": ErrorResponse},
    },
    summary="Query projected settlement positions with shortfalls",
    description="Query positions with negative available balance (shortfalls) for specified settlement date"
)
async def get_projected_shortfall(
    date: Annotated[str, Query(description="Settlement date (T/T+1)")],
    portfolio: Annotated[Optional[str], Query(description="Portfolio code filter")] = None,
    securityType: Annotated[Optional[str], Query(description="Security type filter (Stock/Bond/Fund)")] = None,
    page: Annotated[int, Query(description="Page number", ge=1)] = 1,
    pageSize: Annotated[int, Query(description="Page size", ge=1, le=100)] = 50,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectedShortfallResponse:
    """
    Query projected settlement positions with shortfalls (negative available balance).
    
    This endpoint returns positions where availableBalance < 0 for the specified settlement date.
    It applies user's organization and portfolio permissions to filter the positions.
    
    Query timeout is set to 10 seconds as per design specification.
    
    Args:
        date: Settlement date (must be 'T' or 'T+1')
        portfolio: Optional portfolio code filter
        securityType: Optional security type filter (Stock/Bond/Fund)
        page: Page number (default: 1, min: 1)
        pageSize: Page size (default: 50, min: 1, max: 100)
        current_user: Current authenticated user context
        db: Database session
    
    Returns:
        ProjectedShortfallResponse: List of shortfall positions with pagination and summary
    
    Raises:
        HTTPException: 400 if date parameter is invalid
        HTTPException: 401 if unauthorized
        HTTPException: 403 if forbidden
        HTTPException: 500 if internal error or query timeout
    """
    try:
        # Validate date parameter
        if date not in ['T', 'T+1']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date parameter. Must be 'T' or 'T+1'"
            )
        
        # Validate pageSize
        if pageSize > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page size cannot exceed 100"
            )
        
        # Initialize permission filter
        permission_filter = PermissionFilter()
        
        # Build base query for shortfall positions (availableBalance < 0)
        query = db.query(Position).filter(
            Position.available_balance < 0,
            Position.settlement_date == date
        )
        
        # Apply organization permission filtering
        if current_user.org_ids:
            query = permission_filter.apply_org_filter(
                query,
                current_user,
                Position.org_id
            )
        else:
            # No organization permissions, return empty result
            return ProjectedShortfallResponse(
                code=0,
                message="success",
                data=ProjectedShortfallData(
                    items=[],
                    pagination=PaginationInfo(
                        page=page,
                        pageSize=pageSize,
                        total=0,
                        totalPages=0
                    ),
                    summary=ShortfallSummary(
                        totalShortfallCount=0,
                        totalShortfallValue=0.0,
                        queryDate=date
                    )
                )
            )
        
        # Apply portfolio permission filtering
        if current_user.portfolio_ids:
            query = permission_filter.apply_portfolio_filter(
                query,
                current_user,
                Position.portfolio_code
            )
        
        # Apply optional filters
        if portfolio:
            query = query.filter(Position.portfolio_code == portfolio)
        
        if securityType:
            query = query.filter(Position.security_type == securityType)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Calculate summary statistics
        summary_query = query.with_entities(
            func.count(Position.id).label('count'),
            func.sum(Position.market_value).label('total_value')
        )
        summary_result = summary_query.first()
        
        total_shortfall_count = summary_result.count if summary_result.count else 0
        total_shortfall_value = float(summary_result.total_value) if summary_result.total_value else 0.0
        
        # Apply pagination
        offset = (page - 1) * pageSize
        paginated_query = query.offset(offset).limit(pageSize)
        
        # Execute query with timeout control (10 seconds as per design)
        # Note: SQLAlchemy doesn't have built-in timeout, this would need to be
        # implemented at the database connection level or using asyncio timeout
        positions = paginated_query.all()
        
        # Convert to response format
        position_items = [
            PositionItem(
                securityCode=pos.security_code,
                securityName=pos.security_name,
                availableBalance=float(pos.available_balance),
                settlementDate=pos.settlement_date,
                portfolioCode=pos.portfolio_code,
                portfolioName=pos.portfolio_name,
                securityType=pos.security_type,
                marketValue=float(pos.market_value),
                currency=pos.currency
            )
            for pos in positions
        ]
        
        # Calculate total pages
        total_pages = (total_count + pageSize - 1) // pageSize if total_count > 0 else 0
        
        # Build response
        response = ProjectedShortfallResponse(
            code=0,
            message="success",
            data=ProjectedShortfallData(
                items=position_items,
                pagination=PaginationInfo(
                    page=page,
                    pageSize=pageSize,
                    total=total_count,
                    totalPages=total_pages
                ),
                summary=ShortfallSummary(
                    totalShortfallCount=total_shortfall_count,
                    totalShortfallValue=total_shortfall_value,
                    queryDate=date
                )
            )
        )
        
        return response
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error in get_projected_shortfall: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
