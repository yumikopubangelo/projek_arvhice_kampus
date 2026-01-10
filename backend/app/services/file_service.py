import os
import shutil
import aiofiles
from fastapi import UploadFile, HTTPException
from pathlib import Path
from typing import Tuple, Optional, TYPE_CHECKING
import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from app.config import get_settings
from app.models import ProjectFile, FileType  # Import DB models

if TYPE_CHECKING:
    from app.models import Project

settings = get_settings()


# =====================================================
# FILE SERVICE CONFIGURATION
# =====================================================

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert MB to bytes
ALLOWED_EXTENSIONS = {
    '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.csv', '.xlsx', 
    '.xls', '.json', '.txt', '.py', '.ipynb', '.r', '.sql', '.md', 
    '.zip', '.tar.gz', '.rar', '.pptx', '.ppt', '.docx'
}


class FileService:
    """Service class for file-related business logic."""

    @staticmethod
    def _ensure_upload_dirs():
        """Ensure upload directory exists"""
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _get_user_dir(user_uuid: uuid.UUID) -> Path:
        """Get the directory path for a specific user"""
        return UPLOAD_DIR / str(user_uuid)

    @staticmethod
    def _ensure_user_dir(user_uuid: uuid.UUID) -> Path:
        """Ensure user directory exists and return its path"""
        user_dir = FileService._get_user_dir(user_uuid)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    @staticmethod
    def _validate_file(file_size: int, filename: str):
        """Internal helper to run all validations."""
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File '{filename}' is too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB."
            )
        
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{file_ext}' is not allowed."
            )

    @staticmethod
    async def create_project_file_record(
        db: Session,
        project_id: int,
        user_uuid: uuid.UUID,
        upload_file: UploadFile,
        file_type: FileType,
    ) -> ProjectFile:
        """
        Saves an uploaded file and creates a corresponding ProjectFile record in the database.
        """
        content = await upload_file.read()
        file_size = len(content)

        FileService._validate_file(file_size, upload_file.filename)

        user_dir = FileService._ensure_user_dir(user_uuid)

        original_ext = Path(upload_file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{original_ext}"
        file_path = user_dir / unique_filename

        try:
            async with aiofiles.open(file_path, 'wb') as buffer:
                await buffer.write(content)

            relative_path = str(file_path.relative_to(UPLOAD_DIR))

            db_file = ProjectFile(
                project_id=project_id,
                original_filename=upload_file.filename,
                saved_path=relative_path,
                file_type=file_type,
                mime_type=upload_file.content_type,
                file_size=file_size,
            )

            db.add(db_file)
            return db_file

        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file '{upload_file.filename}': {str(e)}"
            )

    @staticmethod
    def delete_file_record(db: Session, file_path: str) -> None:
        """
        Deletes a file from the filesystem and its corresponding record from the database.
        """
        full_path = UPLOAD_DIR / file_path
        if full_path.exists():
            full_path.unlink()

        db_file = db.query(ProjectFile).filter(ProjectFile.saved_path == file_path).first()
        if db_file:
            db.delete(db_file)

    @staticmethod
    async def replace_main_report(
        db: Session,
        project: "Project",
        user_uuid: uuid.UUID,
        new_file: UploadFile
    ):
        """
        Replaces the main report file for a project.
        Deletes the old file and creates a new one.
        """
        # Find the old main report
        old_report = db.query(ProjectFile).filter(
            ProjectFile.project_id == project.id,
            ProjectFile.file_type == FileType.MAIN_REPORT
        ).first()

        # Delete the old report from disk and DB if it exists
        if old_report:
            FileService.delete_file_record(db, old_report.saved_path)

        # Create the new file record
        await FileService.create_project_file_record(
            db=db,
            project_id=project.id,
            user_uuid=user_uuid,
            upload_file=new_file,
            file_type=FileType.MAIN_REPORT
        )

# Ensure upload directories exist on import
FileService._ensure_upload_dirs()