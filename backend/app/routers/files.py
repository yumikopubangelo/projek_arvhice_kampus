from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.dependencies.dependencies import get_current_active_user
from app.models import User, Project, ProjectFile
from app.services import ProjectService, FileService
from app.config import get_settings
from app.schemas import ProjectFile as ProjectFileSchema

router = APIRouter(prefix="/files", tags=["Files"])
settings = get_settings()

@router.get("/{file_id}/download")
def download_project_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Downloads a specific project file, checking for access permissions first.
    """
    # Query for the file and eagerly load the associated project and its uploader
    db_file = db.query(ProjectFile).options(
        joinedload(ProjectFile.project).joinedload(Project.uploader)
    ).filter(ProjectFile.id == file_id).first()

    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    project = db_file.project
    if not project:
        # This case should not happen if data is consistent, but as a safeguard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated project not found")

    # Check if the user has permission to access the full content
    if not project.can_access_full_content(user_id=current_user.id, user_role=current_user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to download this file")

    # Construct the full path to the file on disk
    file_path = settings.UPLOAD_DIR / db_file.saved_path
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk. It may have been moved or deleted.")

    # Increment download count if the user is not the owner
    if project.uploaded_by != current_user.id:
        ProjectService.increment_download_count(db, project=project)

    # Return the file as a response, using its original filename
    return FileResponse(
        path=str(file_path),
        filename=db_file.original_filename,
        media_type='application/octet-stream'  # Generic media type for downloads
    )

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a specific project file. Only the project owner can do this.
    """
    # Query for the file and eagerly load the associated project
    db_file = db.query(ProjectFile).options(
        joinedload(ProjectFile.project)
    ).filter(ProjectFile.id == file_id).first()

    if not db_file:
        # If the file is already gone, we can consider the operation a success.
        return None

    project = db_file.project
    if not project:
        # This indicates an orphaned file, which is an inconsistent state.
        # It's safe to disallow deletion if the parent project is gone.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated project not found")

    # Check if the current user owns the project
    if project.uploaded_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete files from this project")

    # The FileService handles deleting the file from disk and the DB record
    FileService.delete_file_record(db, file_path=db_file.saved_path)
    
    db.commit()

    return None

@router.get("/project/{project_id}", response_model=List[ProjectFileSchema])
def get_project_files(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a list of all files associated with a specific project.
    """
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check if the user can view the project's metadata at all
    if not project.can_access(user_id=current_user.id, user_role=current_user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this project's files")

    return project.files
