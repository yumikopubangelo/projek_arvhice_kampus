from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# =====================================================
# USER SCHEMAS
# =====================================================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    full_name: Optional[str] = None
    role: str = Field(..., description="Role: 'student' or 'dosen'")
    student_id: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@university.edu",
                "password": "securepassword123",
                "full_name": "John Doe",
                "role": "student",
                "student_id": "12345678",
                "phone": "+628123456789"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@university.edu",
                "password": "securepassword123"
            }
        }


class UserRead(UserBase):
    """Schema for user responses (read operations)"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "student@university.edu",
                "full_name": "John Doe",
                "role": "student",
                "student_id": "12345678",
                "department": None,
                "title": None,
                "phone": "+628123456789",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "last_login": "2024-01-01T12:00:00Z"
            }
        }


class UserUpdate(BaseModel):
    """Schema for user profile updates"""
    full_name: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Updated Doe",
                "phone": "+628123456789"
            }
        }


# =====================================================
# AUTH SCHEMAS
# =====================================================

class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    user: dict  # Simplified user info for token response

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "student@university.edu",
                    "full_name": "John Doe",
                    "role": "student"
                }
            }
        }


class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[int] = None
    role: Optional[str] = None