"""
Custom exceptions for authentication and authorization.
"""


class AuthenticationError(Exception):
    """Base exception for authentication errors."""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when JWT Token has expired."""
    pass


class TokenInvalidError(AuthenticationError):
    """Raised when JWT Token is invalid or malformed."""
    pass


class TokenMissingError(AuthenticationError):
    """Raised when JWT Token is missing from request."""
    pass


class PermissionDeniedError(Exception):
    """Raised when user lacks required permissions."""
    pass
