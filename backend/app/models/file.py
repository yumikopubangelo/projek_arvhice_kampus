from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class FileType(str, enum.Enum):
    """Enum for the type of project file."""
    MAIN_REPORT = "main_report"  # e.g., PDF of the thesis
    SUPPLEMENTARY = "supplementary"  # e.g., ZIP file with code, dataset, slides
    THUMBNAIL = "thumbnail" # e.g., a preview image for the project


class ProjectFile(Base):
    """
    Model to store metadata for each file associated with a project.
    """
    __tablename__ = "project_files"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to the Project
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File metadata
    original_filename = Column(String(500), nullable=False, comment="The original name of the file as uploaded by the user.")
    saved_path = Column(String(500), nullable=False, unique=True, comment="The path to the file on the server's storage, usually with a randomized name.")
    file_type = Column(SQLEnum(FileType), nullable=False, default=FileType.SUPPLEMENTARY, comment="The role of the file in the project.")
    mime_type = Column(String(100), nullable=True, comment="The MIME type of the file, e.g., 'application/pdf'.")
    file_size = Column(Integer, nullable=True, comment="File size in bytes.")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # SQLAlchemy relationship
    project = relationship("Project", back_populates="files")

    def __repr__(self):
        return f"<ProjectFile(id={self.id}, original_filename='{self.original_filename}', project_id={self.project_id})>"
