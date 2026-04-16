"""
Unit tests for JWT Token parser.

Tests cover:
- Token validation and parsing
- Expiration handling
- Permission extraction (organizations, portfolios)
- Error handling for various scenarios
- Multiple token payload formats
"""

import pytest
import jwt
from datetime import datetime, timedelta
from backend.auth import (
    JWTParser,
    UserContext,
    TokenExpiredError,
    TokenInvalidError,
    TokenMissingError
)


# Test secret key
TEST_SECRET_KEY = "test-secret-key-for-jwt-parsing"


class TestJWTParserBasic:
    """Test basic JWT parsing functionality."""
    
    def test_parse_valid_token(self):
        """Test parsing a valid JWT token."""
        # Create token
        payload = {
            'user_id': 'USER001',
            'username': 'test_user',
            'org_ids': ['ORG001', 'ORG002'],
            'portfolio_ids': ['PF001', 'PF002'],
            'roles': ['BO_Operator'],
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        # Parse token
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        # Verify
        assert user_context.user_id == 'USER001'
        assert user_context.username == 'test_user'
        assert user_context.org_ids == ['ORG001', 'ORG002']
        assert user_context.portfolio_ids == ['PF001', 'PF002']
        assert user_context.roles == ['BO_Operator']
        assert user_context.token_issued_at is not None
        assert user_context.token_expires_at is not None
    
    def test_parse_token_with_sub_field(self):
        """Test parsing token using 'sub' field for user_id."""
        payload = {
            'sub': 'USER002',
            'name': 'john_doe',
            'org_ids': ['ORG003'],
            'portfolio_ids': [],
            'roles': ['BO_Supervisor'],
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.user_id == 'USER002'
        assert user_context.username == 'john_doe'
    
    def test_parse_bearer_token(self):
        """Test parsing token from Authorization header."""
        payload = {
            'user_id': 'USER003',
            'username': 'jane_doe',
            'org_ids': ['ORG001'],
            'portfolio_ids': ['PF001'],
            'roles': ['System_Admin'],
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        auth_header = f"Bearer {token}"
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_bearer_token(auth_header)
        
        assert user_context.user_id == 'USER003'
        assert user_context.username == 'jane_doe'


class TestJWTParserExpiration:
    """Test token expiration handling."""
    
    def test_expired_token(self):
        """Test that expired token raises TokenExpiredError."""
        payload = {
            'user_id': 'USER004',
            'username': 'expired_user',
            'org_ids': [],
            'portfolio_ids': [],
            'roles': [],
            'exp': datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY, verify_expiration=True)
        
        with pytest.raises(TokenExpiredError) as exc_info:
            parser.parse_token(token)
        
        assert "expired" in str(exc_info.value).lower()
    
    def test_token_without_expiration(self):
        """Test parsing token without expiration field."""
        payload = {
            'user_id': 'USER005',
            'username': 'no_exp_user',
            'org_ids': ['ORG001'],
            'portfolio_ids': [],
            'roles': ['BO_Operator']
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY, verify_expiration=False)
        user_context = parser.parse_token(token)
        
        assert user_context.user_id == 'USER005'
        assert user_context.token_expires_at is None
    
    def test_validate_token_expiration(self):
        """Test token expiration validation method."""
        parser = JWTParser(TEST_SECRET_KEY)
        
        # Valid token
        valid_context = UserContext(
            user_id='USER006',
            username='valid_user',
            org_ids=[],
            portfolio_ids=[],
            roles=[],
            metadata={},
            token_expires_at=datetime.now() + timedelta(hours=1)
        )
        assert parser.validate_token_expiration(valid_context) is True
        
        # Expired token
        expired_context = UserContext(
            user_id='USER007',
            username='expired_user',
            org_ids=[],
            portfolio_ids=[],
            roles=[],
            metadata={},
            token_expires_at=datetime.now() - timedelta(hours=1)
        )
        assert parser.validate_token_expiration(expired_context) is False
        
        # No expiration
        no_exp_context = UserContext(
            user_id='USER008',
            username='no_exp_user',
            org_ids=[],
            portfolio_ids=[],
            roles=[],
            metadata={},
            token_expires_at=None
        )
        assert parser.validate_token_expiration(no_exp_context) is True


class TestJWTParserErrors:
    """Test error handling."""
    
    def test_missing_token(self):
        """Test that missing token raises TokenMissingError."""
        parser = JWTParser(TEST_SECRET_KEY)
        
        with pytest.raises(TokenMissingError):
            parser.parse_token("")
        
        with pytest.raises(TokenMissingError):
            parser.parse_token(None)
    
    def test_invalid_token_format(self):
        """Test that invalid token format raises TokenInvalidError."""
        parser = JWTParser(TEST_SECRET_KEY)
        
        with pytest.raises(TokenInvalidError):
            parser.parse_token("not-a-valid-jwt-token")
    
    def test_invalid_signature(self):
        """Test that token with invalid signature raises TokenInvalidError."""
        payload = {
            'user_id': 'USER009',
            'username': 'test_user',
            'org_ids': [],
            'portfolio_ids': [],
            'roles': []
        }
        # Sign with different key
        token = jwt.encode(payload, "wrong-secret-key", algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY, verify_signature=True)
        
        with pytest.raises(TokenInvalidError) as exc_info:
            parser.parse_token(token)
        
        assert "signature" in str(exc_info.value).lower()
    
    def test_missing_required_fields(self):
        """Test that token missing required fields raises TokenInvalidError."""
        # Missing user_id
        payload = {
            'username': 'test_user',
            'org_ids': [],
            'portfolio_ids': [],
            'roles': []
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        
        with pytest.raises(TokenInvalidError) as exc_info:
            parser.parse_token(token)
        
        assert "user_id" in str(exc_info.value).lower()
    
    def test_missing_authorization_header(self):
        """Test that missing Authorization header raises TokenMissingError."""
        parser = JWTParser(TEST_SECRET_KEY)
        
        with pytest.raises(TokenMissingError):
            parser.parse_bearer_token("")
        
        with pytest.raises(TokenMissingError):
            parser.parse_bearer_token(None)
    
    def test_malformed_authorization_header(self):
        """Test that malformed Authorization header raises TokenInvalidError."""
        parser = JWTParser(TEST_SECRET_KEY)
        
        # Missing "Bearer" prefix
        with pytest.raises(TokenInvalidError) as exc_info:
            parser.parse_bearer_token("some-token")
        assert "Bearer" in str(exc_info.value)
        
        # Wrong prefix
        with pytest.raises(TokenInvalidError):
            parser.parse_bearer_token("Basic some-token")


class TestPermissionExtraction:
    """Test permission extraction from various payload formats."""
    
    def test_extract_org_ids_direct(self):
        """Test extracting org_ids from direct field."""
        payload = {
            'user_id': 'USER010',
            'username': 'test_user',
            'org_ids': ['ORG001', 'ORG002', 'ORG003'],
            'portfolio_ids': [],
            'roles': []
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.org_ids == ['ORG001', 'ORG002', 'ORG003']
    
    def test_extract_org_ids_from_organizations_array(self):
        """Test extracting org_ids from organizations array."""
        payload = {
            'user_id': 'USER011',
            'username': 'test_user',
            'organizations': [
                {'id': 'ORG001', 'name': 'Org 1'},
                {'id': 'ORG002', 'name': 'Org 2'}
            ],
            'portfolio_ids': [],
            'roles': []
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.org_ids == ['ORG001', 'ORG002']
    
    def test_extract_org_ids_from_org_tree(self):
        """Test extracting org_ids from org_tree structure."""
        payload = {
            'user_id': 'USER012',
            'username': 'test_user',
            'org_tree': {
                'nodes': ['ORG001', 'ORG002', 'ORG003']
            },
            'portfolio_ids': [],
            'roles': []
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.org_ids == ['ORG001', 'ORG002', 'ORG003']
    
    def test_extract_org_ids_from_permissions(self):
        """Test extracting org_ids from permissions structure."""
        payload = {
            'user_id': 'USER013',
            'username': 'test_user',
            'permissions': {
                'org_ids': ['ORG001', 'ORG002']
            },
            'portfolio_ids': [],
            'roles': []
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.org_ids == ['ORG001', 'ORG002']
    
    def test_extract_portfolio_ids_direct(self):
        """Test extracting portfolio_ids from direct field."""
        payload = {
            'user_id': 'USER014',
            'username': 'test_user',
            'org_ids': [],
            'portfolio_ids': ['PF001', 'PF002', 'PF003'],
            'roles': []
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.portfolio_ids == ['PF001', 'PF002', 'PF003']
    
    def test_extract_portfolio_ids_from_portfolios_array(self):
        """Test extracting portfolio_ids from portfolios array."""
        payload = {
            'user_id': 'USER015',
            'username': 'test_user',
            'org_ids': [],
            'portfolios': [
                {'id': 'PF001', 'name': 'Portfolio 1'},
                {'id': 'PF002', 'name': 'Portfolio 2'}
            ],
            'roles': []
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.portfolio_ids == ['PF001', 'PF002']
    
    def test_extract_roles_array(self):
        """Test extracting roles from array."""
        payload = {
            'user_id': 'USER016',
            'username': 'test_user',
            'org_ids': [],
            'portfolio_ids': [],
            'roles': ['BO_Operator', 'BO_Supervisor', 'System_Admin']
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.roles == ['BO_Operator', 'BO_Supervisor', 'System_Admin']
    
    def test_extract_single_role(self):
        """Test extracting single role from 'role' field."""
        payload = {
            'user_id': 'USER017',
            'username': 'test_user',
            'org_ids': [],
            'portfolio_ids': [],
            'role': 'BO_Operator'
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.roles == ['BO_Operator']
    
    def test_extract_metadata(self):
        """Test extracting additional metadata."""
        payload = {
            'user_id': 'USER018',
            'username': 'test_user',
            'org_ids': [],
            'portfolio_ids': [],
            'roles': [],
            'email': 'test@example.com',
            'department': 'Back Office',
            'custom_field': 'custom_value'
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.metadata['email'] == 'test@example.com'
        assert user_context.metadata['department'] == 'Back Office'
        assert user_context.metadata['custom_field'] == 'custom_value'


class TestPermissionChecks:
    """Test permission checking methods."""
    
    def test_has_role(self):
        """Test role checking."""
        user_context = UserContext(
            user_id='USER019',
            username='test_user',
            org_ids=[],
            portfolio_ids=[],
            roles=['BO_Operator', 'BO_Supervisor'],
            metadata={}
        )
        
        parser = JWTParser(TEST_SECRET_KEY)
        
        assert parser.has_role(user_context, 'BO_Operator') is True
        assert parser.has_role(user_context, 'BO_Supervisor') is True
        assert parser.has_role(user_context, 'System_Admin') is False
    
    def test_has_any_role(self):
        """Test checking for any of multiple roles."""
        user_context = UserContext(
            user_id='USER020',
            username='test_user',
            org_ids=[],
            portfolio_ids=[],
            roles=['BO_Operator'],
            metadata={}
        )
        
        parser = JWTParser(TEST_SECRET_KEY)
        
        assert parser.has_any_role(user_context, ['BO_Operator', 'BO_Supervisor']) is True
        assert parser.has_any_role(user_context, ['BO_Supervisor', 'System_Admin']) is False
    
    def test_has_org_access(self):
        """Test organization access checking."""
        user_context = UserContext(
            user_id='USER021',
            username='test_user',
            org_ids=['ORG001', 'ORG002'],
            portfolio_ids=[],
            roles=[],
            metadata={}
        )
        
        parser = JWTParser(TEST_SECRET_KEY)
        
        assert parser.has_org_access(user_context, 'ORG001') is True
        assert parser.has_org_access(user_context, 'ORG002') is True
        assert parser.has_org_access(user_context, 'ORG003') is False
    
    def test_has_portfolio_access(self):
        """Test portfolio access checking."""
        user_context = UserContext(
            user_id='USER022',
            username='test_user',
            org_ids=[],
            portfolio_ids=['PF001', 'PF002'],
            roles=[],
            metadata={}
        )
        
        parser = JWTParser(TEST_SECRET_KEY)
        
        assert parser.has_portfolio_access(user_context, 'PF001') is True
        assert parser.has_portfolio_access(user_context, 'PF002') is True
        assert parser.has_portfolio_access(user_context, 'PF003') is False


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_permissions(self):
        """Test token with empty permission lists."""
        payload = {
            'user_id': 'USER023',
            'username': 'test_user',
            'org_ids': [],
            'portfolio_ids': [],
            'roles': []
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.org_ids == []
        assert user_context.portfolio_ids == []
        assert user_context.roles == []
    
    def test_numeric_ids(self):
        """Test handling of numeric IDs (should be converted to strings)."""
        payload = {
            'user_id': 12345,
            'username': 'test_user',
            'org_ids': [1, 2, 3],
            'portfolio_ids': [100, 200],
            'roles': []
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.user_id == '12345'
        assert user_context.org_ids == ['1', '2', '3']
        assert user_context.portfolio_ids == ['100', '200']
    
    def test_disable_signature_verification(self):
        """Test parsing with signature verification disabled."""
        payload = {
            'user_id': 'USER024',
            'username': 'test_user',
            'org_ids': [],
            'portfolio_ids': [],
            'roles': []
        }
        # Sign with different key
        token = jwt.encode(payload, "different-key", algorithm='HS256')
        
        # Should succeed with verification disabled
        parser = JWTParser(TEST_SECRET_KEY, verify_signature=False)
        user_context = parser.parse_token(token)
        
        assert user_context.user_id == 'USER024'
    
    def test_complex_nested_permissions(self):
        """Test complex nested permission structures."""
        payload = {
            'user_id': 'USER025',
            'username': 'test_user',
            'permissions': {
                'org_ids': ['ORG001', 'ORG002'],
                'portfolio_ids': ['PF001'],
                'roles': ['BO_Operator']
            }
        }
        token = jwt.encode(payload, TEST_SECRET_KEY, algorithm='HS256')
        
        parser = JWTParser(TEST_SECRET_KEY)
        user_context = parser.parse_token(token)
        
        assert user_context.org_ids == ['ORG001', 'ORG002']
        assert user_context.portfolio_ids == ['PF001']
        assert user_context.roles == ['BO_Operator']
