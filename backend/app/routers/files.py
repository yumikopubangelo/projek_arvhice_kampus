from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os
from app.config import get_settings
from app.models.user import User
from app.models.project import Project
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.auth import get_current_user

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
    if filename not in (project.supplementary_files or []):
        raise HTTPException(status_code=404, detail="File not found in project")

    file_path = os.path.join(settings.UPLOAD_DIR, str(project_id), filename)

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