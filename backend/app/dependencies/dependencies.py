from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from app.database import get_db
from app.config import get_settings
from app.models import User, Project

settings = get_settings()

# Define the OAuth2 scheme
# The tokenUrl should point to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_user_optional(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get the current user from a JWT token if provided.
    Returns None if the token is invalid, expired, or not provided,
    instead of raising an exception.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.id == int(user_id)).first()
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user_optional)
) -> User:
    """
    Dependency to get the current authenticated and active user.
    This depends on the optional user and raises an exception if not present
    or not active.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    return current_user

def require_role(required_role: str):
    """
    Dependency factory to require a specific user role ('student' or 'dosen').
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires '{required_role}' role"
            )
        return current_user
    return role_checker

# Pre-made dependencies for convenience
require_student = require_role("student")
require_dosen = require_role("dosen")