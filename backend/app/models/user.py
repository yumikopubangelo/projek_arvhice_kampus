from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class User(Base):
    """
    User model - supports both students and lecturers (dosen)
    """
    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile Information
    full_name = Column(String(255), nullable=True)
    role = Column(
        String(50), 
        nullable=False,
        index=True,
        comment="Role: 'student' or 'dosen'"
    )
    
    # Student-specific field (NIM)
    student_id = Column(String(50), nullable=True, unique=True, index=True)
    
    # Lecturer-specific fields
    department = Column(String(100), nullable=True)
    title = Column(String(50), nullable=True, comment="Academic title: Dr., Prof., etc.")
    
    # Contact
    phone = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    uploaded_projects = relationship(
        "Project", 
        back_populates="uploader",
        foreign_keys="[Project.uploaded_by]",
        cascade="all, delete-orphan"
    )
    
    advised_projects = relationship(
        "Project",
        back_populates="advisor",
        foreign_keys="[Project.advisor_id]"
    )
    
    access_requests = relationship(
        "AccessRequest",
        back_populates="requester",
        cascade="all, delete-orphan"
    )

    # Course relationships
    created_courses = relationship(
        "Course",
        back_populates="lecturer",
        foreign_keys="[Course.lecturer_id]",
        cascade="all, delete-orphan"
    )

    managed_courses = relationship(
        "Course",
        back_populates="creator",
        foreign_keys="[Course.created_by]",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def is_student(self) -> bool:
        """Check if user is a student"""
        return self.role == "student"
    
    @property
    def is_dosen(self) -> bool:
        """Check if user is a lecturer"""
        return self.role == "dosen"