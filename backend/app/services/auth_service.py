from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from typing import Optional

from app.config import get_settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.password import hash_password, verify_password, is_password_strong

settings = get_settings()


# =====================================================
# AUTHENTICATION SERVICE
# =====================================================

class AuthService:
    """Service class for authentication-related operations"""

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check password strength
        is_strong, issues = is_password_strong(user_data.password)
        if not is_strong:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password too weak: {'; '.join(issues)}"
            )

        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check if student_id already exists (if provided)
        if user_data.student_id:
            existing_student = db.query(User).filter(User.student_id == user_data.student_id).first()
            if existing_student:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Student ID already registered"
                )

        # Create new user
        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            student_id=user_data.student_id if user_data.role == "student" else None,
            department=user_data.department if user_data.role == "dosen" else None,
            title=user_data.title if user_data.role == "dosen" else None,
            phone=user_data.phone,
            is_active=True,
            is_verified=False
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    @staticmethod
    def authenticate_user(db: Session, credentials: UserLogin) -> User:
        """Authenticate user with email and password"""
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def create_access_token(user_id: int, role: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expire
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def get_current_user_from_token(db: Session, token: str) -> User:
        """Get current user from JWT token"""
        payload = AuthService.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    @staticmethod
    def update_user_profile(db: Session, user: User, update_data: dict) -> User:
        """Update user profile information"""
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(db: Session, user: User, old_password: str, new_password: str) -> None:
        """Change user password"""
        # Verify old password
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Check new password strength
        is_strong, issues = is_password_strong(new_password)
        if not is_strong:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"New password too weak: {'; '.join(issues)}"
            )

        # Update password
        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def deactivate_user(db: Session, user: User) -> None:
        """Deactivate user account"""
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def activate_user(db: Session, user: User) -> None:
        """Activate user account"""
        user.is_active = True
        user.updated_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def verify_user_email(db: Session, user: User) -> None:
        """Mark user email as verified"""
        user.is_verified = True
        user.updated_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def check_email_available(db: Session, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """Check if email is available for registration"""
        query = db.query(User).filter(User.email == email)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is None

    @staticmethod
    def check_student_id_available(db: Session, student_id: str, exclude_user_id: Optional[int] = None) -> bool:
        """Check if student ID is available"""
        if not student_id:
            return True
        query = db.query(User).filter(User.student_id == student_id)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is None