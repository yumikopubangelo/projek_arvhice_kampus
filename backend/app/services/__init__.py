"""
Services Package

Contains business logic services for the Campus Archive application.
"""

from app.services.auth_service import AuthService
from app.services.project_service import ProjectService
from app.services.file_service import save_project_file, save_supplementary_file, delete_project_files

# Export services for easy import
__all__ = [
    "AuthService",
    "ProjectService",
    "save_project_file",
    "save_supplementary_file",
    "delete_project_files"
]