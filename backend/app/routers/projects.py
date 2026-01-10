from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, Project, FileType
from app.schemas import ProjectCreate, ProjectRead, ProjectUpdate, ProjectFile as ProjectFileSchema, ProjectStatus, PrivacyLevel
from app.dependencies.dependencies import get_current_active_user
from app.services import ProjectService, FileService

router = APIRouter(prefix="/projects", tags=["Projects"])

# Dependency to parse form data into a Pydantic model
def get_project_create_form(
    title: str = Form(...),
    abstract: Optional[str] = Form(None),
    authors: str = Form(...),  # Comma-separated
    tags: str = Form(...),     # Comma-separated
    year: int = Form(...),
    semester: Optional[str] = Form(None),
    class_name: Optional[str] = Form(None),
    course_code: Optional[str] = Form(None),
    assignment_type: Optional[str] = Form(None),
    lecturer_name: Optional[str] = Form(None),
    privacy_level: str = Form(default="private"),
    code_repo_url: Optional[str] = Form(None),
    dataset_url: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
) -> ProjectCreate:
    authors_list = [a.strip() for a in authors.split(",") if a.strip()]
    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    return ProjectCreate(
        title=title,
        abstract=abstract,
        authors=authors_list,
        tags=tags_list,
        year=year,
        semester=semester,
        class_name=class_name,
        course_code=course_code,
        assignment_type=assignment_type,
        lecturer_name=lecturer_name,
        privacy_level=privacy_level,
        code_repo_url=code_repo_url,
        dataset_url=dataset_url,
        video_url=video_url
    )

def get_project_update_form(
    title: Optional[str] = Form(None),
    abstract: Optional[str] = Form(None),
    authors: Optional[str] = Form(None),  # Comma-separated
    tags: Optional[str] = Form(None),     # Comma-separated
    year: Optional[int] = Form(None),
    semester: Optional[str] = Form(None),
    class_name: Optional[str] = Form(None),
    course_code: Optional[str] = Form(None),
    assignment_type: Optional[str] = Form(None),
    status: Optional[ProjectStatus] = Form(None),
    privacy_level: Optional[PrivacyLevel] = Form(None),
    code_repo_url: Optional[str] = Form(None),
    dataset_url: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
    lecturer_name: Optional[str] = Form(None),
) -> ProjectUpdate:
    update_data = {
        "title": title,
        "abstract": abstract,
        "year": year,
        "semester": semester,
        "class_name": class_name,
        "course_code": course_code,
        "assignment_type": assignment_type,
        "status": status,
        "privacy_level": privacy_level,
        "code_repo_url": code_repo_url,
        "dataset_url": dataset_url,
        "video_url": video_url,
        "lecturer_name": lecturer_name,
    }

    if authors is not None:
        update_data["authors"] = [a.strip() for a in authors.split(",") if a.strip()]
    
    if tags is not None:
        update_data["tags"] = [t.strip() for t in tags.split(",") if t.strip()]

    # Filter out None values so they don't overwrite existing fields with null
    return ProjectUpdate(**{k: v for k, v in update_data.items() if v is not None})

@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate = Depends(get_project_create_form),
    main_file: UploadFile = File(...),
    supplementary_files: List[UploadFile] = File([]),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project with a main file and optional supplementary files.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can upload projects")

    # Create the project entry first
    project = ProjectService.create_project(db, project_data=project_data, uploader_id=current_user.id)
    
    try:
        # Handle the main file (renamed from pdf_file for clarity)
        await FileService.create_project_file_record(
            db=db,
            project_id=project.id,
            user_uuid=current_user.uuid,
            upload_file=main_file,
            file_type=FileType.MAIN_REPORT
        )

        # Handle supplementary files
        for sup_file in supplementary_files:
            if sup_file.filename: # Ensure file is not empty
                await FileService.create_project_file_record(
                    db=db,
                    project_id=project.id,
                    user_uuid=current_user.uuid,
                    upload_file=sup_file,
                    file_type=FileType.SUPPLEMENTARY
                )
        
        db.commit()
        db.refresh(project)

    except Exception as e:
        db.rollback()
        # Note: File cleanup on disk might be needed if something goes wrong
        # For simplicity, we are not implementing that here, but in production, it would be important.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during file upload: {str(e)}"
        )
        
    return project

@router.post("/{project_id}/files", response_model=List[ProjectFileSchema])
async def upload_project_files(
    project_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload one or more supplementary files to an existing project.
    """
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Only the project owner can upload more files
    if project.uploaded_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to add files to this project")

    created_files = []
    try:
        for file in files:
            if file.filename:
                new_file_record = await FileService.create_project_file_record(
                    db=db,
                    project_id=project.id,
                    user_uuid=current_user.uuid,
                    upload_file=file,
                    file_type=FileType.SUPPLEMENTARY
                )
                created_files.append(new_file_record)
        
        db.commit()
        for f in created_files:
            db.refresh(f)

    except Exception as e:
        db.rollback()
        # Basic cleanup of files that might have been saved before the error
        # A more robust implementation would track and delete them.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during file upload: {str(e)}"
        )
        
    return created_files

@router.get("/me/projects", response_model=List[ProjectRead])
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all projects uploaded by the current user."""
    return ProjectService.get_user_projects(db, user_id=current_user.id)

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a single project by its ID."""
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check access rights
    if not project.can_access(user_id=current_user.id, user_role=current_user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this project")

    # Increment view count if the user is not the owner
    if project.uploaded_by != current_user.id:
        ProjectService.increment_view_count(db, project=project)

    return project

@router.post("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate = Depends(get_project_update_form),
    pdf_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a project's metadata and optionally replace its main file.
    """
    project = ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Update metadata
    updated_project = ProjectService.update_project(db, project=project, update_data=project_update, user_id=current_user.id)

    try:
        # Handle new PDF file if provided
        if pdf_file and pdf_file.filename:
            await FileService.replace_main_report(
                db=db,
                project=project,
                user_uuid=current_user.uuid,
                new_file=pdf_file
            )
        
        db.commit()
        db.refresh(updated_project)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during file update: {str(e)}"
        )

    return updated_project