"""
Unit tests for Positions API endpoints.

Tests the GET /api/v1/positions/projected_shortfall endpoint with various scenarios:
- Valid queries with different parameters
- Permission filtering (organization and portfolio)
- Pagination
- Error handling
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.positions import router
from api.dependencies import get_db, get_current_user
from models.position import Position, Base
from auth.jwt_parser import UserContext


# Create test app
app = FastAPI()
app.include_router(router)


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
def sample_positions(test_db):
    """Create sample position data."""
    positions = [
        # Shortfall positions (negative available_balance)
        Position(
            id=1,
            security_code='600000.SH',
            security_name='浦发银行',
            security_type='Stock',
            available_balance=-5000,
            market_value=-50000.00,
            currency='CNY',
            settlement_date='T+1',
            portfolio_code='PF001',
            portfolio_name='自营组合1',
            org_id='ORG001'
        ),
        Position(
            id=2,
            security_code='600001.SH',
            security_name='中国银行',
            security_type='Stock',
            available_balance=-3000,
            market_value=-30000.00,
            currency='CNY',
            settlement_date='T+1',
            portfolio_code='PF002',
            portfolio_name='自营组合2',
            org_id='ORG001'
        ),
        Position(
            id=3,
            security_code='110001.SH',
            security_name='国债01',
            security_type='Bond',
            available_balance=-2000,
            market_value=-20000.00,
            currency='CNY',
            settlement_date='T',
            portfolio_code='PF001',
            portfolio_name='自营组合1',
            org_id='ORG002'
        ),
        # Normal positions (positive available_balance) - should not be returned
        Position(
            id=4,
            security_code='600002.SH',
            security_name='工商银行',
            security_type='Stock',
            available_balance=10000,
            market_value=100000.00,
            currency='CNY',
            settlement_date='T+1',
            portfolio_code='PF001',
            portfolio_name='自营组合1',
            org_id='ORG001'
        ),
    ]
    test_db.add_all(positions)
    test_db.commit()
    return positions


@pytest.fixture
def mock_user_context():
    """Create mock user context with permissions."""
    return UserContext(
        user_id='user123',
        username='testuser',
        roles=['BO_Operator', 'BO_Supervisor'],
        org_ids=['ORG001'],
        portfolio_ids=['PF001', 'PF002'],
        metadata={}
    )


@pytest.fixture
def mock_user_context_limited():
    """Create mock user context with limited permissions."""
    return UserContext(
        user_id='user456',
        username='limiteduser',
        roles=['BO_Operator'],
        org_ids=['ORG002'],
        portfolio_ids=['PF001'],
        metadata={}
    )


@pytest.fixture
def mock_user_context_no_permissions():
    """Create mock user context with no permissions."""
    return UserContext(
        user_id='user789',
        username='nopermuser',
        roles=['BO_Operator'],
        org_ids=[],
        portfolio_ids=[],
        metadata={}
    )


def make_request_with_auth(test_db, user_context, path, params=None):
    """Helper function to make authenticated requests."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    def override_get_current_user():
        return user_context
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    client = TestClient(app)
    
    try:
        return client.get(path, params=params)
    finally:
        app.dependency_overrides.clear()


class TestProjectedShortfallEndpoint:
    """Test cases for GET /api/v1/positions/projected_shortfall endpoint."""
    
    def test_get_shortfall_positions_success(self, test_db, sample_positions, mock_user_context):
        """Test successful query of shortfall positions."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['code'] == 0
        assert data['message'] == 'success'
        assert 'data' in data
        
        # Check items
        items = data['data']['items']
        assert len(items) == 2  # Only ORG001 positions with T+1
        assert all(item['availableBalance'] < 0 for item in items)
        assert all(item['settlementDate'] == 'T+1' for item in items)
        
        # Check pagination
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['pageSize'] == 50
        assert pagination['total'] == 2
        assert pagination['totalPages'] == 1
        
        # Check summary
        summary = data['data']['summary']
        assert summary['totalShortfallCount'] == 2
        assert summary['totalShortfallValue'] == -80000.00
        assert summary['queryDate'] == 'T+1'
    
    def test_get_shortfall_positions_with_portfolio_filter(self, test_db, sample_positions, mock_user_context):
        """Test query with portfolio filter."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'portfolio': 'PF001'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 1
        assert items[0]['portfolioCode'] == 'PF001'
        assert items[0]['securityCode'] == '600000.SH'
    
    def test_get_shortfall_positions_with_security_type_filter(self, test_db, sample_positions, mock_user_context):
        """Test query with security type filter."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'securityType': 'Stock'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 2
        assert all(item['securityType'] == 'Stock' for item in items)
    
    def test_get_shortfall_positions_with_pagination(self, test_db, sample_positions, mock_user_context):
        """Test query with pagination."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'page': 1, 'pageSize': 1}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 1
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['pageSize'] == 1
        assert pagination['total'] == 2
        assert pagination['totalPages'] == 2
    
    def test_get_shortfall_positions_limited_permissions(self, test_db, sample_positions, mock_user_context_limited):
        """Test query with limited organization permissions."""
        response = make_request_with_auth(
            test_db,
            mock_user_context_limited,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 1  # Only ORG002 position with T
        assert items[0]['securityCode'] == '110001.SH'
        assert items[0]['securityType'] == 'Bond'
    
    def test_get_shortfall_positions_no_permissions(self, test_db, sample_positions, mock_user_context_no_permissions):
        """Test query with no organization permissions."""
        response = make_request_with_auth(
            test_db,
            mock_user_context_no_permissions,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty result
        items = data['data']['items']
        assert len(items) == 0
        
        summary = data['data']['summary']
        assert summary['totalShortfallCount'] == 0
        assert summary['totalShortfallValue'] == 0.0
    
    def test_get_shortfall_positions_invalid_date(self, test_db, mock_user_context):
        """Test query with invalid date parameter."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+2'}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'Invalid date parameter' in data['detail']
    
    def test_get_shortfall_positions_missing_date(self, test_db, mock_user_context):
        """Test query without date parameter."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_shortfall_positions_invalid_page_size(self, test_db, mock_user_context):
        """Test query with invalid page size (exceeds max)."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'pageSize': 150}
        )
        
        # FastAPI validation returns 422 for constraint violations
        # Our custom validation returns 400
        # Since pageSize has le=100 constraint, FastAPI catches it first
        assert response.status_code in [400, 422]
    
    def test_get_shortfall_positions_no_results(self, test_db, mock_user_context):
        """Test query with no matching results."""
        # Clear all positions
        test_db.query(Position).delete()
        test_db.commit()
        
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 0
        
        summary = data['data']['summary']
        assert summary['totalShortfallCount'] == 0
        assert summary['totalShortfallValue'] == 0.0
    
    def test_get_shortfall_positions_unauthorized(self, test_db):
        """Test query without authentication."""
        client = TestClient(app)
        
        def override_get_db():
            try:
                yield test_db
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        
        try:
            response = client.get(
                '/api/v1/positions/projected_shortfall',
                params={'date': 'T+1'}
            )
            # Should fail due to missing authentication
            assert response.status_code in [401, 422]
        finally:
            app.dependency_overrides.clear()


class TestPaginationLogic:
    """Test cases specifically for pagination logic and edge cases."""
    
    @pytest.fixture
    def large_dataset(self, test_db):
        """Create a large dataset for pagination testing."""
        positions = []
        for i in range(1, 126):  # Create 125 positions
            positions.append(
                Position(
                    id=i,
                    security_code=f'60{i:04d}.SH',
                    security_name=f'股票{i}',
                    security_type='Stock',
                    available_balance=-1000 * i,
                    market_value=-10000 * i,
                    currency='CNY',
                    settlement_date='T+1',
                    portfolio_code='PF001',
                    portfolio_name='自营组合1',
                    org_id='ORG001'
                )
            )
        test_db.add_all(positions)
        test_db.commit()
        return positions
    
    def test_pagination_first_page(self, test_db, large_dataset, mock_user_context):
        """Test pagination on first page."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'page': 1, 'pageSize': 50}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 50
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['pageSize'] == 50
        assert pagination['total'] == 125
        assert pagination['totalPages'] == 3  # ceil(125/50) = 3
    
    def test_pagination_middle_page(self, test_db, large_dataset, mock_user_context):
        """Test pagination on middle page."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'page': 2, 'pageSize': 50}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 50
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 2
        assert pagination['pageSize'] == 50
        assert pagination['total'] == 125
        assert pagination['totalPages'] == 3
    
    def test_pagination_last_page_partial(self, test_db, large_dataset, mock_user_context):
        """Test pagination on last page with partial results."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'page': 3, 'pageSize': 50}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 25  # 125 - (2 * 50) = 25 remaining
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 3
        assert pagination['pageSize'] == 50
        assert pagination['total'] == 125
        assert pagination['totalPages'] == 3
    
    def test_pagination_beyond_last_page(self, test_db, large_dataset, mock_user_context):
        """Test pagination beyond last page returns empty results."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'page': 10, 'pageSize': 50}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 0  # No items on page 10
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 10
        assert pagination['pageSize'] == 50
        assert pagination['total'] == 125
        assert pagination['totalPages'] == 3
    
    def test_pagination_with_max_page_size(self, test_db, large_dataset, mock_user_context):
        """Test pagination with maximum allowed page size (100)."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'page': 1, 'pageSize': 100}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 100
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['pageSize'] == 100
        assert pagination['total'] == 125
        assert pagination['totalPages'] == 2  # ceil(125/100) = 2
    
    def test_pagination_with_min_page_size(self, test_db, large_dataset, mock_user_context):
        """Test pagination with minimum page size (1)."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'page': 1, 'pageSize': 1}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 1
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['pageSize'] == 1
        assert pagination['total'] == 125
        assert pagination['totalPages'] == 125
    
    def test_pagination_empty_results(self, test_db, mock_user_context):
        """Test pagination with empty results."""
        # Clear all positions
        test_db.query(Position).delete()
        test_db.commit()
        
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'page': 1, 'pageSize': 50}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 0
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['pageSize'] == 50
        assert pagination['total'] == 0
        assert pagination['totalPages'] == 0
    
    def test_pagination_exact_page_boundary(self, test_db, mock_user_context):
        """Test pagination when total records exactly match page size."""
        # Create exactly 50 positions
        positions = []
        for i in range(1, 51):
            positions.append(
                Position(
                    id=i,
                    security_code=f'60{i:04d}.SH',
                    security_name=f'股票{i}',
                    security_type='Stock',
                    available_balance=-1000,
                    market_value=-10000,
                    currency='CNY',
                    settlement_date='T+1',
                    portfolio_code='PF001',
                    portfolio_name='自营组合1',
                    org_id='ORG001'
                )
            )
        test_db.add_all(positions)
        test_db.commit()
        
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'page': 1, 'pageSize': 50}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 50
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['pageSize'] == 50
        assert pagination['total'] == 50
        assert pagination['totalPages'] == 1  # Exactly one page
    
    def test_pagination_invalid_page_number(self, test_db, large_dataset, mock_user_context):
        """Test pagination with invalid page number (0 or negative)."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'page': 0, 'pageSize': 50}
        )
        
        # FastAPI validation should catch this (ge=1 constraint)
        assert response.status_code == 422
    
    def test_pagination_default_values(self, test_db, large_dataset, mock_user_context):
        """Test pagination with default values (page=1, pageSize=50)."""
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1'}  # No page or pageSize specified
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 50  # Default pageSize
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 1  # Default page
        assert pagination['pageSize'] == 50  # Default pageSize
        assert pagination['total'] == 125
        assert pagination['totalPages'] == 3
    
    def test_pagination_with_filters(self, test_db, large_dataset, mock_user_context):
        """Test pagination works correctly with filters applied."""
        # Add some Bond positions
        bond_positions = []
        for i in range(1, 11):
            bond_positions.append(
                Position(
                    id=200 + i,
                    security_code=f'11{i:04d}.SH',
                    security_name=f'债券{i}',
                    security_type='Bond',
                    available_balance=-1000,
                    market_value=-10000,
                    currency='CNY',
                    settlement_date='T+1',
                    portfolio_code='PF001',
                    portfolio_name='自营组合1',
                    org_id='ORG001'
                )
            )
        test_db.add_all(bond_positions)
        test_db.commit()
        
        # Query with security type filter
        response = make_request_with_auth(
            test_db,
            mock_user_context,
            path='/api/v1/positions/projected_shortfall',
            params={'date': 'T+1', 'securityType': 'Bond', 'page': 1, 'pageSize': 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        items = data['data']['items']
        assert len(items) == 5
        assert all(item['securityType'] == 'Bond' for item in items)
        
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['pageSize'] == 5
        assert pagination['total'] == 10  # Only Bond positions
        assert pagination['totalPages'] == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
