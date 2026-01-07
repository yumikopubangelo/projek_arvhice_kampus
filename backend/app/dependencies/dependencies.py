from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from jose import JWTError, jwt

from app.database import get_db
from app.config import get_settings
from app.models.user import User

settings = get_settings()


# =====================================================
# AUTHENTICATION DEPENDENCIES
# =====================================================

def get_current_user_optional(
    token: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    Doesn't raise exception for unauthenticated users.
    """
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        user = db.query(User).filter(User.id == int(user_id)).first()
        return user

    except JWTError:
        return None


def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """
    Get current authenticated and active user.
    Raises exception if not authenticated or not active.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    return current_user


def require_role(required_role: str):
    """
    Dependency factory to require specific user role.

    Args:
        required_role: Required role ('student' or 'dosen')

    Returns:
        Dependency function
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires {required_role} role"
            )
        return current_user

    return role_checker


# =====================================================
# PERMISSION DEPENDENCIES
# =====================================================

def require_project_owner(project_id: int):
    """
    Dependency factory to ensure user owns the project.

    Args:
        project_id: Project ID parameter

    Returns:
        Dependency function
    """
    def owner_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Import here to avoid circular imports
        from app.models.project import Project

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        if project.uploaded_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't own this project"
            )

        return current_user

    return owner_checker


def require_project_access(project_id: int):
    """
    Dependency factory to ensure user has access to the project.

    Args:
        project_id: Project ID parameter

    Returns:
        Dependency function
    """
    def access_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Import here to avoid circular imports
        from app.models.project import Project

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        if not project.can_access(current_user.id, current_user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project"
            )

        return current_user

    return access_checker


# =====================================================
# UTILITY DEPENDENCIES
# =====================================================

def get_db_session() -> Session:
    """
    Alias for get_db to provide clearer naming.
    """
    return Depends(get_db)


# =====================================================
# COMMON DEPENDENCY COMBINATIONS
# =====================================================

# Require authenticated student
require_student = require_role("student")

# Require authenticated dosen
require_dosen = require_role("dosen")

# Require authenticated active user (alias for clarity)
require_auth = get_current_active_user