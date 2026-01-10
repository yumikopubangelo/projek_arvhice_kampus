from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base
# Import the new ProjectFile model to establish the relationship
from .file import ProjectFile


class PrivacyLevel(str, enum.Enum):
    """Privacy levels for projects"""
    PRIVATE = "private"          # Only uploader can see
    ADVISOR = "advisor"          # Uploader + advisor can see
    CLASS = "class"              # All students in the same class
    PUBLIC = "public"            # Everyone can see


class ProjectStatus(str, enum.Enum):
    """Project completion status"""
    ONGOING = "ongoing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    """
    Project model - stores student research projects/assignments
    """
    __tablename__ = "projects"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # =====================================================
    # PUBLIC METADATA (Always visible in search results)
    # =====================================================
    title = Column(String(500), nullable=False, index=True)
    abstract = Column(Text, nullable=True)
    abstract_preview = Column(
        String(300), 
        nullable=True,
        comment="Truncated abstract for search results"
    )
    
    # Authors (stored as array)
    authors = Column(
        ARRAY(String), 
        nullable=True,
        comment="List of author names"
    )
    
    # Tags/Keywords (stored as array for easy filtering)
    tags = Column(
        ARRAY(String),
        nullable=True,
        index=True,
        comment="Topics: ML, NLP, Computer Vision, etc."
    )
    
    # Academic Context
    year = Column(Integer, nullable=False, index=True)
    semester = Column(
        String(20),
        nullable=True,
        comment="'Ganjil' or 'Genap'"
    )
    class_name = Column(String(100), nullable=True)
    course_code = Column(String(50), nullable=True)
    assignment_type = Column(
        String(50),
        nullable=True,
        comment="Type of assignment: 'skripsi', 'tugas_matkul', 'laporan_kp', 'lainnya'"
    )
    lecturer_name = Column(String(200), nullable=True, comment="Nama Dosen")
    
    # Status
    status = Column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.ONGOING,
        nullable=False,
        index=True
    )
    
    # =====================================================
    # PRIVACY CONTROL
    # =====================================================
    privacy_level = Column(
        SQLEnum(PrivacyLevel),
        default=PrivacyLevel.PRIVATE,
        nullable=False,
        index=True
    )
    
    # =====================================================
    # PRIVATE CONTENT (Controlled by privacy_level)
    # =====================================================
    # DEPRECATED: pdf_file_path, pdf_file_size, supplementary_files
    # These are now handled by the ProjectFile model
    
    code_repo_url = Column(
        String(500),
        nullable=True,
        comment="GitHub/GitLab repository URL"
    )
    
    dataset_url = Column(
        String(500),
        nullable=True,
        comment="Link to dataset (if publicly available)"
    )

    video_url = Column(
        String(500),
        nullable=True,
        comment="YouTube link to demo video"
    )

    # =====================================================
    # RELATIONSHIPS (Foreign Keys)
    # =====================================================
    uploaded_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    advisor_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # =====================================================
    # STATISTICS
    # =====================================================
    view_count = Column(Integer, default=0, nullable=False)
    download_count = Column(Integer, default=0, nullable=False)
    
    # =====================================================
    # TIMESTAMPS
    # =====================================================
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # =====================================================
    # SQLAlchemy Relationships
    # =====================================================
    uploader = relationship(
        "User",
        back_populates="uploaded_projects",
        foreign_keys=[uploaded_by]
    )
    
    advisor = relationship(
        "User",
        back_populates="advised_projects",
        foreign_keys=[advisor_id]
    )
    
    access_requests = relationship(
        "AccessRequest",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # New relationship to ProjectFile
    files = relationship(
        "ProjectFile",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="joined"  # Use 'joined' to load files with the project
    )

    def __repr__(self):
        return f"<Project(id={self.id}, title='{self.title[:50]}...', year={self.year})>"
    
    @property
    def is_public(self) -> bool:
        """Check if project is publicly accessible"""
        return self.privacy_level == PrivacyLevel.PUBLIC
    
    @property
    def has_file(self) -> bool:
        """Check if project has any associated files"""
        return self.files and len(self.files) > 0
    
    def can_access(self, user_id: int, user_role: str) -> bool:
        """
        Check if a user can access this project's content

        Args:
            user_id: ID of user requesting access
            user_role: Role of user ('student' or 'dosen')

        Returns:
            bool: True if user can access, False otherwise
        """
        # Owner can always access
        if user_id == self.uploaded_by:
            return True

        # Public projects are accessible to everyone
        if self.privacy_level == PrivacyLevel.PUBLIC:
            return True

        # Advisor can access if privacy is ADVISOR or higher
        if self.advisor_id == user_id and self.privacy_level in [
            PrivacyLevel.ADVISOR,
            PrivacyLevel.CLASS,
            PrivacyLevel.PUBLIC
        ]:
            return True

        # Dosen can access private projects for metadata viewing
        if user_role == 'dosen':
            return True

        # For CLASS level, need to check if user is in same class
        # (This would require additional logic based on your class system)
        if self.privacy_level == PrivacyLevel.CLASS:
            # TODO: Implement class membership check
            pass

        # Otherwise, check if access request is approved
        # (This would be checked in the access_requests relationship)
        return False

    def can_access_full_content(self, user_id: int, user_role: str) -> bool:
        """
        Check if a user can access the full content (PDF, etc.) of this project

        Args:
            user_id: ID of user requesting access
            user_role: Role of user ('student' or 'dosen')

        Returns:
            bool: True if user can access full content, False otherwise
        """
        # Owner can always access
        if user_id == self.uploaded_by:
            return True

        # Public projects are fully accessible to everyone
        if self.privacy_level == PrivacyLevel.PUBLIC:
            return True

        # Advisor can access if privacy is ADVISOR or higher
        if self.advisor_id == user_id and self.privacy_level in [
            PrivacyLevel.ADVISOR,
            PrivacyLevel.CLASS,
            PrivacyLevel.PUBLIC
        ]:
            return True

        # Dosen can only see metadata for private projects, not full content
        if user_role == 'dosen' and self.privacy_level == PrivacyLevel.PRIVATE:
            return False

        # For CLASS level, need to check if user is in same class
        # (This would require additional logic based on your class system)
        if self.privacy_level == PrivacyLevel.CLASS:
            # TODO: Implement class membership check
            pass

        # Otherwise, check if access request is approved
        # (This would be checked in the access_requests relationship)
        return False