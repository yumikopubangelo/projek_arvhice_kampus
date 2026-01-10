from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
from typing import List
from app.config import get_settings
from app.models.user import User
from app.models.project import Project
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.auth import get_current_user
from app.services.file_service import save_supplementary_file, delete_file, validate_file_extension, validate_file_size, ALLOWED_EXTENSIONS

router = APIRouter(prefix="/files", tags=["Files"])
settings = get_settings()

@router.get("/{project_id}/pdf")
async def download_pdf(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download PDF file for a project
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check access permissions
    if not project.can_access_full_content(current_user.id, current_user.role):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to download this file"
        )

    # Check if file exists
    if not project.pdf_file_path:
        raise HTTPException(status_code=404, detail="PDF file not found")

    file_path = os.path.join(settings.UPLOAD_DIR, project.pdf_file_path)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    # Increment download count
    project.download_count += 1
    db.commit()

    return FileResponse(
        path=file_path,
        filename=f"{project.title}.pdf",
        media_type='application/pdf'
    )

@router.get("/{project_id}/supplementary/{filename}")
async def download_supplementary(
    project_id: int,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download supplementary file for a project
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check access permissions
    if not project.can_access_full_content(current_user.id, current_user.role):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to download this file"
        )

    # Check if file is in supplementary files list
    # Find the stored path for this filename
    stored_path = None
    for path in (project.supplementary_files or []):
        if path.endswith(f"/{filename}") or path == filename:
            stored_path = path
            break

    if not stored_path:
        raise HTTPException(status_code=404, detail="File not found in project")

    file_path = os.path.join(settings.UPLOAD_DIR, stored_path)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    # Increment download count
    project.download_count += 1
    db.commit()

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@router.post("/{project_id}/supplementary")
async def upload_supplementary_file(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a supplementary file to a project
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check ownership
    if project.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only modify your own projects"
        )

    # Validate file extension
    all_allowed = []
    for ext_list in ALLOWED_EXTENSIONS.values():
        all_allowed.extend(ext_list)
    validate_file_extension(file.filename, all_allowed)

    # Save file using user_id (files are stored in user folders)
    file_path, file_size = await save_supplementary_file(file, current_user.uuid)

    # Add to project's supplementary files list
    if project.supplementary_files is None:
        project.supplementary_files = []
    project.supplementary_files.append(file_path)  # Store relative file path

    db.commit()

    return {
        "filename": file.filename,
        "path": file_path,
        "size": file_size,
        "message": "File uploaded successfully"
    }


@router.delete("/{project_id}/supplementary/{filename}")
async def delete_supplementary_file(
    project_id: int,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a supplementary file from a project
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check ownership
    if project.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only modify your own projects"
        )

    # Find the stored path for this filename
    path_to_remove = None
    for path in (project.supplementary_files or []):
        if path.endswith(f"/{filename}") or path == filename:
            path_to_remove = path
            break

    if not path_to_remove:
        raise HTTPException(status_code=404, detail="File not found in project")

    # Remove from list
    project.supplementary_files.remove(path_to_remove)

    # Delete file from disk using the stored path
    delete_file(path_to_remove)

    db.commit()

    return {"message": "File deleted successfully"}