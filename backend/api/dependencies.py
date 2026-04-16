"""
FastAPI dependencies for authentication and database access.

This module provides dependency injection functions for:
- JWT token parsing and user authentication
- Database session management
"""

from typing import Annotated
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from auth.jwt_parser import JWTParser, UserContext
from auth.exceptions import TokenExpiredError, TokenInvalidError, TokenMissingError


# JWT Parser instance (should be configured with secret key from environment)
# For now, using a placeholder secret key
jwt_parser = JWTParser(
    secret_key="your-secret-key-here",  # TODO: Load from environment variable
    algorithm="HS256",
    verify_signature=True,
    verify_expiration=True
)


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None
) -> UserContext:
    """
    Dependency to extract and validate user from JWT token.
    
    Args:
        authorization: Authorization header containing Bearer token
    
    Returns:
        UserContext: Parsed user context with permissions
    
    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_context = jwt_parser.parse_bearer_token(authorization)
        return user_context
    
    except TokenMissingError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except TokenInvalidError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_db() -> Session:
    """
    Dependency to get database session.
    
    Creates a database session for each request and ensures proper cleanup.
    Uses SQLite for development/testing, PostgreSQL for production.
    
    Yields:
        Session: SQLAlchemy database session
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from models.message import Base
    import os
    
    # Get database URL from environment or use SQLite for development
    database_url = os.getenv("DATABASE_URL", "sqlite:///./message_reminder.db")
    
    # Create engine
    engine = create_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
    )
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create and yield session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
