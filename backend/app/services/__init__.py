"""
Services Package

Contains business logic services for the Campus Archive application.
"""

from app.services.auth_service import AuthService
from app.services.project_service import ProjectService
from app.services.file_service import FileService
from app.services.course_service import CourseService

# Export services for easy import
__all__ = [
    "AuthService",
    "ProjectService",
    "FileService",
    "CourseService",
]