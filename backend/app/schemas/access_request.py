from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# =====================================================
# ENUMS (MIRRORING MODEL ENUMS)
# =====================================================

class AccessRequestStatus(str, Enum):
    """Status of access requests"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    REVOKED = "revoked"


# =====================================================
# ACCESS REQUEST SCHEMAS
# =====================================================

class AccessRequestBase(BaseModel):
    """Base access request schema with common fields"""
    message: Optional[str] = Field(None, max_length=1000, description="Optional message explaining why access is needed")


class AccessRequestCreate(AccessRequestBase):
    """Schema for creating new access requests"""
    project_id: int = Field(..., description="ID of the project to request access to")

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "message": "I am reviewing projects for the Computer Science department and need access to evaluate this work."
            }
        }


class AccessRequestRead(AccessRequestBase):
    """Schema for access request responses (read operations)"""
    id: int
    project_id: int
    requester_id: int
    status: AccessRequestStatus
    response_message: Optional[str] = None
    requested_at: datetime
    responded_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    # Related data (optional, populated by service layer)
    project: Optional[dict] = None  # Simplified project info
    requester: Optional[dict] = None  # Simplified user info

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "project_id": 1,
                "requester_id": 2,
                "status": "pending",
                "message": "I am reviewing projects for the Computer Science department and need access to evaluate this work.",
                "response_message": None,
                "requested_at": "2024-01-01T10:00:00Z",
                "responded_at": None,
                "expires_at": None,
                "project": {
                    "id": 1,
                    "title": "Machine Learning Analysis of Student Performance",
                    "year": 2024
                },
                "requester": {
                    "id": 2,
                    "full_name": "Dr. Jane Smith",
                    "email": "jane@university.edu",
                    "role": "dosen",
                    "department": "Computer Science"
                }
            }
        }


class AccessRequestUpdate(BaseModel):
    """Schema for updating access requests (approve/deny)"""
    status: AccessRequestStatus = Field(..., description="New status for the request")
    response_message: Optional[str] = Field(None, max_length=1000, description="Optional response message")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date for approved access")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "approved",
                "response_message": "Access granted for evaluation purposes. Please use this access responsibly.",
                "expires_at": "2024-12-31T23:59:59Z"
            }
        }


class AccessRequestRespond(BaseModel):
    """Schema for responding to access requests"""
    action: str = Field(..., pattern="^(approve|deny|revoke)$", description="Action to take: approve, deny, or revoke")
    response_message: Optional[str] = Field(None, max_length=1000, description="Optional response message")
    expires_at: Optional[datetime] = Field(None, description="Expiration date (only for approve action)")

    class Config:
        json_schema_extra = {
            "example": {
                "action": "approve",
                "response_message": "Access granted for evaluation purposes.",
                "expires_at": "2024-12-31T23:59:59Z"
            }
        }


class AccessRequestSummary(BaseModel):
    """Simplified access request info for listings"""
    id: int
    project_id: int
    requester_id: int
    status: AccessRequestStatus
    requested_at: datetime
    responded_at: Optional[datetime] = None

    # Related data
    project_title: Optional[str] = None
    requester_name: Optional[str] = None
    requester_role: Optional[str] = None

    class Config:
        from_attributes = True