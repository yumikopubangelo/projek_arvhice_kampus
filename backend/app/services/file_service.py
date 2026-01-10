import os
import shutil
import aiofiles
from fastapi import UploadFile, HTTPException
from pathlib import Path
from typing import Tuple, Optional
import uuid
from datetime import datetime

from app.config import get_settings

settings = get_settings()


# =====================================================
# FILE SERVICE CONFIGURATION
# =====================================================

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert MB to bytes
MAX_TOTAL_SIZE_MB = 50
MAX_TOTAL_SIZE = MAX_TOTAL_SIZE_MB * 1024 * 1024  # 50MB total per project

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf': ['.pdf'],
    'images': ['.png', '.jpg', '.jpeg', '.gif', '.svg'],
    'data': ['.csv', '.xlsx', '.xls', '.json', '.txt'],
    'code': ['.py', '.ipynb', '.r', '.sql', '.md'],
    'archives': ['.zip', '.tar.gz', '.rar'],
    'presentations': ['.pptx', '.ppt']
}

# PDF specific settings
PDF_EXTENSIONS = ['.pdf']


# =====================================================
# DIRECTORY MANAGEMENT
# =====================================================

def ensure_upload_dirs():
    """Ensure upload directory exists"""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_user_dir(user_uuid: uuid.UUID) -> Path:
    """Get the directory path for a specific user"""
    return UPLOAD_DIR / str(user_uuid)


def ensure_user_dir(user_uuid: uuid.UUID) -> Path:
    """Ensure user directory exists and return its path"""
    user_dir = get_user_dir(user_uuid)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


# =====================================================
# FILE VALIDATION
# =====================================================

def validate_file_size(file_size: int) -> None:
    """Validate file size against maximum allowed"""
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB"
        )


def validate_total_size(total_size: int) -> None:
    """Validate total project files size against maximum allowed"""
    if total_size > MAX_TOTAL_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Total files size too large. Maximum total size is {MAX_TOTAL_SIZE_MB}MB"
        )


def validate_file_extension(filename: str, allowed_extensions: list) -> None:
    """Validate file extension"""
    file_ext = Path(filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )


def is_pdf_file(filename: str) -> bool:
    """Check if file is a PDF"""
    return Path(filename).suffix.lower() == '.pdf'


# =====================================================
# FILE OPERATIONS
# =====================================================

async def save_project_file(upload_file: UploadFile, user_uuid: uuid.UUID) -> Tuple[str, int]:
    """
    Save an uploaded file for a project.

    Args:
        upload_file: FastAPI UploadFile object
        user_uuid: UUID of the user uploading the file

    Returns:
        Tuple[str, int]: (relative_file_path, file_size)

    Raises:
        HTTPException: If file validation fails or save operation fails
    """
    # Validate file size first
    file_size = 0
    content = await upload_file.read()
    file_size = len(content)
    validate_file_size(file_size)

    # Validate file extension for PDFs
    if not is_pdf_file(upload_file.filename):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed for project uploads"
        )

    # Ensure user directory exists
    user_dir = ensure_user_dir(user_uuid)

    # Generate unique filename to prevent conflicts
    original_ext = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{original_ext}"
    file_path = user_dir / unique_filename

    try:
        # Save file asynchronously
        async with aiofiles.open(file_path, 'wb') as buffer:
            await buffer.write(content)

        # Return relative path from upload directory
        relative_path = str(file_path.relative_to(UPLOAD_DIR))

        return relative_path, file_size

    except Exception as e:
        # Clean up partial file if it exists
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )


async def save_supplementary_file(upload_file: UploadFile, user_uuid: uuid.UUID) -> Tuple[str, int]:
    """
    Save a supplementary file for a project.

    Args:
        upload_file: FastAPI UploadFile object
        user_uuid: UUID of the user uploading the file

    Returns:
        Tuple[str, int]: (relative_file_path, file_size)
    """
    # Read file content
    content = await upload_file.read()
    file_size = len(content)
    validate_file_size(file_size)

    # Validate file extension (allow various types for supplementary files)
    all_allowed = []
    for ext_list in ALLOWED_EXTENSIONS.values():
        all_allowed.extend(ext_list)

    validate_file_extension(upload_file.filename, all_allowed)

    # Ensure user directory exists
    user_dir = ensure_user_dir(user_uuid)

    # Generate unique filename
    original_ext = Path(upload_file.filename).suffix
    unique_filename = f"supp_{uuid.uuid4()}{original_ext}"
    file_path = user_dir / unique_filename

    try:
        # Save file
        async with aiofiles.open(file_path, 'wb') as buffer:
            await buffer.write(content)

        relative_path = str(file_path.relative_to(UPLOAD_DIR))
        return relative_path, file_size

    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save supplementary file: {str(e)}"
        )


def delete_project_files(file_paths: list) -> None:
    """
    Delete specific files associated with a project.

    Args:
        file_paths: List of relative file paths to delete
    """
    for file_path in file_paths:
        full_path = UPLOAD_DIR / file_path
        if full_path.exists():
            full_path.unlink()


def delete_file(file_path: str) -> None:
    """
    Delete a specific file.

    Args:
        file_path: Relative path to the file from upload directory
    """
    full_path = UPLOAD_DIR / file_path
    if full_path.exists():
        full_path.unlink()


# =====================================================
# FILE INFORMATION
# =====================================================

def get_file_info(file_path: str) -> Optional[dict]:
    """
    Get information about a file.

    Args:
        file_path: Relative path to the file from upload directory

    Returns:
        dict or None: File information or None if file doesn't exist
    """
    full_path = UPLOAD_DIR / file_path
    if not full_path.exists():
        return None

    stat = full_path.stat()
    return {
        'path': file_path,
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'exists': True
    }




# =====================================================
# INITIALIZATION
# =====================================================

# Ensure upload directories exist on import
ensure_upload_dirs()