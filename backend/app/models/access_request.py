from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class AccessRequestStatus(str, enum.Enum):
    """Status of access requests"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    REVOKED = "revoked"  # Access was approved but later revoked


class AccessRequest(Base):
    """
    Access Request model - tracks lecturer requests to view private projects
    """
    __tablename__ = "access_requests"
    
    # Composite unique constraint to prevent duplicate requests
    __table_args__ = (
        UniqueConstraint('project_id', 'requester_id', name='uq_project_requester'),
    )

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # =====================================================
    # FOREIGN KEYS
    # =====================================================
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    requester_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User requesting access (usually a dosen)"
    )
    
    # =====================================================
    # REQUEST DETAILS
    # =====================================================
    status = Column(
        SQLEnum(AccessRequestStatus),
        default=AccessRequestStatus.PENDING,
        nullable=False,
        index=True
    )
    
    message = Column(
        Text,
        nullable=True,
        comment="Optional message from requester explaining why they need access"
    )
    
    response_message = Column(
        Text,
        nullable=True,
        comment="Optional message from project owner when approving/denying"
    )
    
    # =====================================================
    # TIMESTAMPS
    # =====================================================
    requested_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    responded_at = Column(
        DateTime,
        nullable=True,
        comment="When the request was approved/denied"
    )
    
    expires_at = Column(
        DateTime,
        nullable=True,
        comment="When access expires (optional)"
    )
    
    # =====================================================
    # SQLAlchemy Relationships
    # =====================================================
    project = relationship(
        "Project",
        back_populates="access_requests"
    )
    
    requester = relationship(
        "User",
        back_populates="access_requests"
    )

    def __repr__(self):
        return f"<AccessRequest(id={self.id}, project_id={self.project_id}, status='{self.status}')>"
    
    @property
    def is_pending(self) -> bool:
        """Check if request is still pending"""
        return self.status == AccessRequestStatus.PENDING
    
    @property
    def is_approved(self) -> bool:
        """Check if request is approved"""
        return self.status == AccessRequestStatus.APPROVED
    
    @property
    def is_active(self) -> bool:
        """Check if access is currently active (approved and not expired)"""
        if self.status != AccessRequestStatus.APPROVED:
            return False
        
        if self.expires_at is None:
            return True
        
        return datetime.utcnow() < self.expires_at
    
    def approve(self, response_message: str = None):
        """Approve the access request"""
        self.status = AccessRequestStatus.APPROVED
        self.responded_at = datetime.utcnow()
        self.response_message = response_message
    
    def deny(self, response_message: str = None):
        """Deny the access request"""
        self.status = AccessRequestStatus.DENIED
        self.responded_at = datetime.utcnow()
        self.response_message = response_message
    
    def revoke(self):
        """Revoke previously granted access"""
        if self.status == AccessRequestStatus.APPROVED:
            self.status = AccessRequestStatus.REVOKED
            self.responded_at = datetime.utcnow()