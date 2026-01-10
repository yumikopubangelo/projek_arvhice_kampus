from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.access_request import AccessRequest, AccessRequestStatus
from app.schemas.access_request import (
    AccessRequestCreate, AccessRequestRead, AccessRequestUpdate,
    AccessRequestRespond, AccessRequestSummary
)
from app.dependencies.dependencies import get_current_active_user

router = APIRouter(prefix="/access", tags=["Access Requests"])


# =====================================================
# CREATE ACCESS REQUEST
# =====================================================
@router.post("/", response_model=AccessRequestRead, status_code=status.HTTP_201_CREATED)
async def create_access_request(
    request_data: AccessRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new access request for a private project
    """
    # Only dosen can request access
    if current_user.role != "dosen":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can request access to projects"
        )

    # Check if project exists
    project = db.query(Project).filter(Project.id == request_data.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check if project is private
    if project.privacy_level.value == "public":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access requests are only for private projects"
        )

    # Check if user already has access
    if project.can_access(current_user.id, current_user.role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have access to this project"
        )

    # Check if request already exists
    existing_request = db.query(AccessRequest).filter(
        AccessRequest.project_id == request_data.project_id,
        AccessRequest.requester_id == current_user.id
    ).first()

    if existing_request:
        if existing_request.status == AccessRequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a pending request for this project"
            )
        elif existing_request.status == AccessRequestStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your request for this project has already been approved"
            )

    # Create new request
    access_request = AccessRequest(
        project_id=request_data.project_id,
        requester_id=current_user.id,
        message=request_data.message
    )

    db.add(access_request)
    db.commit()
    db.refresh(access_request)

    return access_request


# =====================================================
# GET MY ACCESS REQUESTS
# =====================================================
@router.get("/my-requests", response_model=List[AccessRequestSummary])
async def get_my_access_requests(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get access requests made by current user
    """
    query = db.query(AccessRequest).filter(AccessRequest.requester_id == current_user.id)

    if status_filter:
        try:
            status_enum = AccessRequestStatus(status_filter)
            query = query.filter(AccessRequest.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter"
            )

    requests = query.order_by(AccessRequest.requested_at.desc()).all()
    return requests


# =====================================================
# GET REQUESTS FOR MY PROJECTS
# =====================================================
@router.get("/for-my-projects", response_model=List[AccessRequestSummary])
async def get_requests_for_my_projects(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get access requests for projects owned by current user
    """
    # Get user's projects
    user_projects = db.query(Project).filter(Project.uploaded_by == current_user.id).subquery()

    query = db.query(AccessRequest).filter(
        AccessRequest.project_id.in_(
            db.query(user_projects.c.id)
        )
    )

    if status_filter:
        try:
            status_enum = AccessRequestStatus(status_filter)
            query = query.filter(AccessRequest.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter"
            )

    requests = query.order_by(AccessRequest.requested_at.desc()).all()
    return requests


# =====================================================
# GET SINGLE ACCESS REQUEST
# =====================================================
@router.get("/{request_id}", response_model=AccessRequestRead)
async def get_access_request(
    request_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific access request
    """
    request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found"
        )

    # Check if user is involved (requester or project owner)
    is_requester = request.requester_id == current_user.id
    is_owner = db.query(Project).filter(
        Project.id == request.project_id,
        Project.uploaded_by == current_user.id
    ).first() is not None

    if not (is_requester or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this request"
        )

    return request


# =====================================================
# RESPOND TO ACCESS REQUEST
# =====================================================
@router.post("/{request_id}/respond", response_model=AccessRequestRead)
async def respond_to_access_request(
    request_id: int,
    response_data: AccessRequestRespond,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Approve or deny an access request (project owners only)
    """
    request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found"
        )

    # Check if current user owns the project
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if project.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owners can respond to access requests"
        )

    # Check if request is still pending
    if request.status != AccessRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This request has already been responded to"
        )

    # Process response
    if response_data.action == "approve":
        request.approve(response_data.response_message)
        if response_data.expires_at:
            request.expires_at = response_data.expires_at
    elif response_data.action == "deny":
        request.deny(response_data.response_message)
    elif response_data.action == "revoke":
        if request.status == AccessRequestStatus.APPROVED:
            request.revoke()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot revoke a request that is not approved"
            )

    db.commit()
    db.refresh(request)

    return request


# =====================================================
# CANCEL ACCESS REQUEST
# =====================================================
@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_access_request(
    request_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a pending access request (requester only)
    """
    request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found"
        )

    # Only requester can cancel
    if request.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own requests"
        )

    # Only pending requests can be cancelled
    if request.status != AccessRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending requests can be cancelled"
        )

    db.delete(request)
    db.commit()

    return None


# =====================================================
# CHECK ACCESS STATUS
# =====================================================
@router.get("/check/{project_id}")
async def check_access_status(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check current user's access status for a project
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check direct access
    has_access = project.can_access(current_user.id, current_user.role)

    # Check if there's an active access request
    access_request = db.query(AccessRequest).filter(
        AccessRequest.project_id == project_id,
        AccessRequest.requester_id == current_user.id
    ).first()

    request_status = None
    if access_request:
        request_status = access_request.status.value
        # If approved and not expired, grant access
        if access_request.is_active:
            has_access = True

    return {
        "project_id": project_id,
        "has_access": has_access,
        "request_status": request_status,
        "privacy_level": project.privacy_level.value
    }