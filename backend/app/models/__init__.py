"""
Database Models Package

Import all models here to ensure they're registered with SQLAlchemy
before Alembic runs migrations.
"""

from app.models.user import User
from app.models.project import Project, PrivacyLevel, ProjectStatus
from app.models.access_request import AccessRequest, AccessRequestStatus
from app.models.file import ProjectFile, FileType

# Export all models for easy import
__all__ = [
    "User",
    "Project",
    "AccessRequest",
    "PrivacyLevel",
    "ProjectStatus",
    "AccessRequestStatus",
    "ProjectFile",
    "FileType",
]