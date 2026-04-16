"""
JWT Token parser for extracting user permissions.

This module provides functionality to parse JWT tokens and extract:
- User organization tree permissions
- Portfolio permissions
- User roles and metadata

Includes token validation, expiration handling, and comprehensive error handling.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError,
    DecodeError,
    InvalidSignatureError
)

from .exceptions import (
    TokenExpiredError,
    TokenInvalidError,
    TokenMissingError
)


@dataclass
class UserContext:
    """
    User context extracted from JWT Token.
    
    Attributes:
        user_id: Unique user identifier
        username: Username
        org_ids: List of organization IDs the user has access to
        portfolio_ids: List of portfolio IDs the user has access to
        roles: List of user roles (e.g., BO_Operator, BO_Supervisor, System_Admin)
        metadata: Additional user metadata from token
        token_issued_at: Token issue timestamp
        token_expires_at: Token expiration timestamp
    """
    user_id: str
    username: str
    org_ids: List[str]
    portfolio_ids: List[str]
    roles: List[str]
    metadata: Dict[str, Any]
    token_issued_at: Optional[datetime] = None
    token_expires_at: Optional[datetime] = None


class JWTParser:
    """
    JWT Token parser for authentication and authorization.
    
    This class handles:
    - Token validation and signature verification
    - Token expiration checking
    - User permission extraction (organization tree, portfolios)
    - Error handling for various token issues
    """
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        verify_signature: bool = True,
        verify_expiration: bool = True
    ):
        """
        Initialize JWT parser.
        
        Args:
            secret_key: Secret key for token verification
            algorithm: JWT algorithm (default: HS256)
            verify_signature: Whether to verify token signature
            verify_expiration: Whether to verify token expiration
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.verify_signature = verify_signature
        self.verify_expiration = verify_expiration
    
    def parse_token(self, token: str) -> UserContext:
        """
        Parse JWT token and extract user context.
        
        Args:
            token: JWT token string (without "Bearer " prefix)
        
        Returns:
            UserContext: Parsed user context with permissions
        
        Raises:
            TokenMissingError: If token is None or empty
            TokenExpiredError: If token has expired
            TokenInvalidError: If token is invalid or malformed
        """
        if not token:
            raise TokenMissingError("JWT token is missing or empty")
        
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    'verify_signature': self.verify_signature,
                    'verify_exp': self.verify_expiration
                }
            )
            
            # Extract user context from payload
            return self._extract_user_context(payload)
            
        except ExpiredSignatureError as e:
            raise TokenExpiredError(f"JWT token has expired: {str(e)}")
        
        except (InvalidSignatureError, DecodeError) as e:
            raise TokenInvalidError(f"JWT token signature is invalid: {str(e)}")
        
        except InvalidTokenError as e:
            raise TokenInvalidError(f"JWT token is invalid: {str(e)}")
        
        except Exception as e:
            raise TokenInvalidError(f"Failed to parse JWT token: {str(e)}")
    
    def parse_bearer_token(self, authorization_header: str) -> UserContext:
        """
        Parse JWT token from Authorization header.
        
        Args:
            authorization_header: Authorization header value (e.g., "Bearer <token>")
        
        Returns:
            UserContext: Parsed user context with permissions
        
        Raises:
            TokenMissingError: If header is missing or malformed
            TokenExpiredError: If token has expired
            TokenInvalidError: If token is invalid
        """
        if not authorization_header:
            raise TokenMissingError("Authorization header is missing")
        
        parts = authorization_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise TokenInvalidError(
                "Authorization header must be in format: Bearer <token>"
            )
        
        token = parts[1]
        return self.parse_token(token)
    
    def _extract_user_context(self, payload: Dict[str, Any]) -> UserContext:
        """
        Extract user context from JWT payload.
        
        Args:
            payload: Decoded JWT payload
        
        Returns:
            UserContext: User context object
        
        Raises:
            TokenInvalidError: If required fields are missing
        """
        try:
            # Extract required fields
            user_id = payload.get('user_id') or payload.get('sub')
            username = payload.get('username') or payload.get('name')
            
            if not user_id:
                raise TokenInvalidError("Token missing required field: user_id or sub")
            
            if not username:
                raise TokenInvalidError("Token missing required field: username or name")
            
            # Extract organization permissions
            org_ids = self._extract_org_ids(payload)
            
            # Extract portfolio permissions
            portfolio_ids = self._extract_portfolio_ids(payload)
            
            # Extract roles
            roles = self._extract_roles(payload)
            
            # Extract timestamps
            token_issued_at = self._extract_timestamp(payload, 'iat')
            token_expires_at = self._extract_timestamp(payload, 'exp')
            
            # Extract additional metadata
            metadata = self._extract_metadata(payload)
            
            return UserContext(
                user_id=str(user_id),
                username=str(username),
                org_ids=org_ids,
                portfolio_ids=portfolio_ids,
                roles=roles,
                metadata=metadata,
                token_issued_at=token_issued_at,
                token_expires_at=token_expires_at
            )
            
        except TokenInvalidError:
            raise
        except Exception as e:
            raise TokenInvalidError(f"Failed to extract user context: {str(e)}")
    
    def _extract_org_ids(self, payload: Dict[str, Any]) -> List[str]:
        """
        Extract organization IDs from token payload.
        
        Supports multiple payload formats:
        - org_ids: ["ORG001", "ORG002"]
        - organizations: [{"id": "ORG001"}, {"id": "ORG002"}]
        - org_tree: {"nodes": ["ORG001", "ORG002"]}
        
        Args:
            payload: JWT payload
        
        Returns:
            List of organization IDs
        """
        # Try direct org_ids field
        if 'org_ids' in payload:
            org_ids = payload['org_ids']
            if isinstance(org_ids, list):
                return [str(org_id) for org_id in org_ids]
        
        # Try organizations array
        if 'organizations' in payload:
            orgs = payload['organizations']
            if isinstance(orgs, list):
                return [str(org.get('id')) for org in orgs if isinstance(org, dict) and 'id' in org]
        
        # Try org_tree structure
        if 'org_tree' in payload:
            org_tree = payload['org_tree']
            if isinstance(org_tree, dict) and 'nodes' in org_tree:
                nodes = org_tree['nodes']
                if isinstance(nodes, list):
                    return [str(node) for node in nodes]
        
        # Try permissions structure
        if 'permissions' in payload:
            perms = payload['permissions']
            if isinstance(perms, dict) and 'org_ids' in perms:
                org_ids = perms['org_ids']
                if isinstance(org_ids, list):
                    return [str(org_id) for org_id in org_ids]
        
        return []
    
    def _extract_portfolio_ids(self, payload: Dict[str, Any]) -> List[str]:
        """
        Extract portfolio IDs from token payload.
        
        Supports multiple payload formats:
        - portfolio_ids: ["PF001", "PF002"]
        - portfolios: [{"id": "PF001"}, {"id": "PF002"}]
        - permissions: {"portfolio_ids": ["PF001", "PF002"]}
        
        Args:
            payload: JWT payload
        
        Returns:
            List of portfolio IDs
        """
        # Try direct portfolio_ids field
        if 'portfolio_ids' in payload:
            portfolio_ids = payload['portfolio_ids']
            if isinstance(portfolio_ids, list):
                return [str(pid) for pid in portfolio_ids]
        
        # Try portfolios array
        if 'portfolios' in payload:
            portfolios = payload['portfolios']
            if isinstance(portfolios, list):
                return [str(p.get('id')) for p in portfolios if isinstance(p, dict) and 'id' in p]
        
        # Try permissions structure
        if 'permissions' in payload:
            perms = payload['permissions']
            if isinstance(perms, dict) and 'portfolio_ids' in perms:
                portfolio_ids = perms['portfolio_ids']
                if isinstance(portfolio_ids, list):
                    return [str(pid) for pid in portfolio_ids]
        
        return []
    
    def _extract_roles(self, payload: Dict[str, Any]) -> List[str]:
        """
        Extract user roles from token payload.
        
        Supports multiple payload formats:
        - roles: ["BO_Operator", "BO_Supervisor"]
        - role: "BO_Operator"
        - permissions: {"roles": ["BO_Operator"]}
        
        Args:
            payload: JWT payload
        
        Returns:
            List of role names
        """
        # Try roles array
        if 'roles' in payload:
            roles = payload['roles']
            if isinstance(roles, list):
                return [str(role) for role in roles]
            elif isinstance(roles, str):
                return [roles]
        
        # Try single role field
        if 'role' in payload:
            role = payload['role']
            if isinstance(role, str):
                return [role]
            elif isinstance(role, list):
                return [str(r) for r in role]
        
        # Try permissions structure
        if 'permissions' in payload:
            perms = payload['permissions']
            if isinstance(perms, dict) and 'roles' in perms:
                roles = perms['roles']
                if isinstance(roles, list):
                    return [str(role) for role in roles]
        
        return []
    
    def _extract_timestamp(self, payload: Dict[str, Any], field: str) -> Optional[datetime]:
        """
        Extract timestamp from payload and convert to datetime.
        
        Args:
            payload: JWT payload
            field: Field name ('iat' or 'exp')
        
        Returns:
            datetime object or None if field not present
        """
        if field in payload:
            timestamp = payload[field]
            if isinstance(timestamp, (int, float)):
                return datetime.fromtimestamp(timestamp)
        return None
    
    def _extract_metadata(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract additional metadata from payload.
        
        Excludes standard JWT fields and permission fields.
        
        Args:
            payload: JWT payload
        
        Returns:
            Dictionary of additional metadata
        """
        # Standard JWT fields to exclude
        excluded_fields = {
            'user_id', 'sub', 'username', 'name',
            'org_ids', 'organizations', 'org_tree',
            'portfolio_ids', 'portfolios',
            'roles', 'role', 'permissions',
            'iat', 'exp', 'nbf', 'iss', 'aud', 'jti'
        }
        
        metadata = {}
        for key, value in payload.items():
            if key not in excluded_fields:
                metadata[key] = value
        
        return metadata
    
    def validate_token_expiration(self, user_context: UserContext) -> bool:
        """
        Check if token is expired.
        
        Args:
            user_context: User context with token expiration info
        
        Returns:
            True if token is valid (not expired), False otherwise
        """
        if user_context.token_expires_at is None:
            # No expiration set, consider valid
            return True
        
        return datetime.now() < user_context.token_expires_at
    
    def has_role(self, user_context: UserContext, role: str) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            user_context: User context
            role: Role name to check
        
        Returns:
            True if user has the role, False otherwise
        """
        return role in user_context.roles
    
    def has_any_role(self, user_context: UserContext, roles: List[str]) -> bool:
        """
        Check if user has any of the specified roles.
        
        Args:
            user_context: User context
            roles: List of role names to check
        
        Returns:
            True if user has at least one role, False otherwise
        """
        return any(role in user_context.roles for role in roles)
    
    def has_org_access(self, user_context: UserContext, org_id: str) -> bool:
        """
        Check if user has access to a specific organization.
        
        Args:
            user_context: User context
            org_id: Organization ID to check
        
        Returns:
            True if user has access, False otherwise
        """
        return org_id in user_context.org_ids
    
    def has_portfolio_access(self, user_context: UserContext, portfolio_id: str) -> bool:
        """
        Check if user has access to a specific portfolio.
        
        Args:
            user_context: User context
            portfolio_id: Portfolio ID to check
        
        Returns:
            True if user has access, False otherwise
        """
        return portfolio_id in user_context.portfolio_ids
