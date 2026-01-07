from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.project import Project, PrivacyLevel, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.routers.auth import get_current_user
from app.services.file_service import save_project_file
from app.utils.encryption import decrypt_sensitive_fields

router = APIRouter(prefix="/projects", tags=["Projects"])


# =====================================================
# CREATE PROJECT
# =====================================================
@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    # Form data
    title: str = Form(...),
    abstract: str = Form(...),
    authors: str = Form(...),  # Comma-separated
    tags: str = Form(...),     # Comma-separated
    year: int = Form(...),
    semester: Optional[str] = Form(None),
    class_name: Optional[str] = Form(None),
    course_code: Optional[str] = Form(None),
    assignment_type: Optional[str] = Form(None),
    privacy_level: str = Form(default="private"),
    code_repo_url: Optional[str] = Form(None),
    dataset_url: Optional[str] = Form(None),
    advisor_id: Optional[int] = Form(None),
    # File upload
    pdf_file: Optional[UploadFile] = File(None),
    # Auth & DB
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new project (students only)
    """
    # Only students can create projects
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can upload projects"
        )
    
    # Parse authors and tags
    authors_list = [a.strip() for a in authors.split(",")]
    tags_list = [t.strip() for t in tags.split(",")]
    
    # Create abstract preview (first 300 chars)
    abstract_preview = abstract[:300] + "..." if len(abstract) > 300 else abstract
    
    # Create project in DB first (to get ID for file storage)
    new_project = Project(
        title=title,
        abstract=abstract,
        abstract_preview=abstract_preview,
        authors=authors_list,
        tags=tags_list,
        year=year,
        semester=semester,
        class_name=class_name,
        course_code=course_code,
        assignment_type=assignment_type,
        status=ProjectStatus.ONGOING,
        privacy_level=PrivacyLevel(privacy_level),
        code_repo_url=code_repo_url,
        dataset_url=dataset_url,
        uploaded_by=current_user.id,
        advisor_id=advisor_id
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Save PDF file if provided
    if pdf_file:
        file_path, file_size = await save_project_file(pdf_file, new_project.id)
        new_project.pdf_file_path = file_path
        new_project.pdf_file_size = file_size
        db.commit()

    # Load the project with relationships for proper serialization
    project = db.query(Project).options(
        joinedload(Project.uploader)
    ).filter(Project.id == new_project.id).first()

    # Format project for response
    project_dict = project.__dict__.copy()
    project_dict.pop('_sa_instance_state', None)

    # Ensure supplementary_files is a list
    if project_dict.get('supplementary_files') is None:
        project_dict['supplementary_files'] = []

    # Format uploader as dict
    if project.uploader:
        project_dict['uploader'] = {
            'id': project.uploader.id,
            'full_name': project.uploader.full_name,
            'email': project.uploader.email
        }
    else:
        project_dict['uploader'] = None

    return project_dict


# =====================================================
# GET ALL PROJECTS (WITH FILTERS)
# =====================================================
@router.get("", response_model=List[ProjectRead])
async def get_projects(
    year: Optional[int] = None,
    tag: Optional[str] = None,
    privacy_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects (filtered by access permissions)
    """
    query = db.query(Project).options(
        # Eager load uploader relationship
        joinedload(Project.uploader)
    ).join(Project.uploader)

    # Apply filters
    if year:
        query = query.filter(Project.year == year)

    if tag:
        # Case-insensitive partial match in tags
        from sqlalchemy import func
        query = query.filter(
            func.array_to_string(Project.tags, ' ').ilike(f'%{tag}%')
        )

    if privacy_level:
        query = query.filter(Project.privacy_level == privacy_level)

    # Filter by access permissions
    # TODO: Implement proper access control based on privacy levels

    projects = query.offset(skip).limit(limit).all()

    # Format projects for response
    formatted_projects = []
    for project in projects:
        # Check if user can access this project
        if not project.can_access(current_user.id, current_user.role):
            continue

        # Check if user can access full content
        can_access_full = project.can_access_full_content(current_user.id, current_user.role)

        project_dict = project.__dict__.copy()
        # Remove SQLAlchemy internal fields
        project_dict.pop('_sa_instance_state', None)

        # Ensure supplementary_files is a list
        if project_dict.get('supplementary_files') is None:
            project_dict['supplementary_files'] = []

        # Hide private content if user cannot access full content
        if not can_access_full:
            project_dict['pdf_file_path'] = None
            project_dict['pdf_file_size'] = None
            project_dict['supplementary_files'] = []
            project_dict['code_repo_url'] = None
            project_dict['dataset_url'] = None

        # Format uploader as dict
        if project.uploader:
            project_dict['uploader'] = {
                'id': project.uploader.id,
                'full_name': project.uploader.full_name,
                'email': project.uploader.email
            }
        else:
            project_dict['uploader'] = None

        formatted_projects.append(project_dict)

    return formatted_projects


# =====================================================
# GET SINGLE PROJECT
# =====================================================
@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get project by ID
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Load uploader
    uploader = db.query(User).filter(User.id == project.uploaded_by).first()
    project.uploader = uploader

    # Check access permissions
    if not project.can_access(current_user.id, current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this project"
        )

    # Check if user can access full content
    can_access_full = project.can_access_full_content(current_user.id, current_user.role)

    # Increment view count
    project.view_count += 1
    db.commit()
    db.refresh(project)  # Refresh to get updated values

    # Format project for response
    project_dict = project.__dict__.copy()
    project_dict.pop('_sa_instance_state', None)

    # Ensure supplementary_files is a list
    if project_dict.get('supplementary_files') is None:
        project_dict['supplementary_files'] = []

    # Hide private content if user cannot access full content
    if not can_access_full:
        project_dict['pdf_file_path'] = None
        project_dict['pdf_file_size'] = None
        project_dict['supplementary_files'] = []
        project_dict['code_repo_url'] = None
        project_dict['dataset_url'] = None

    # Format uploader as dict
    if project.uploader:
        project_dict['uploader'] = {
            'id': project.uploader.id,
            'full_name': project.uploader.full_name,
            'email': project.uploader.email
        }
    else:
        project_dict['uploader'] = None

    return project_dict


# =====================================================
# UPDATE PROJECT
# =====================================================
@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_data: dict,  # Receive as dict to decrypt
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update project (owner only)
    """
    # Decrypt sensitive fields
    decrypted_data = decrypt_sensitive_fields(project_data)

    # Convert empty strings to None for URL fields
    if decrypted_data.get('code_repo_url') == '':
        decrypted_data['code_repo_url'] = None
    if decrypted_data.get('dataset_url') == '':
        decrypted_data['dataset_url'] = None

    # Validate with Pydantic
    try:
        project_update = ProjectUpdate(**decrypted_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )

    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only owner can update
    if project.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own projects"
        )
    
    # Update fields
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    # Load the project with relationships for proper serialization
    updated_project = db.query(Project).options(
        joinedload(Project.uploader)
    ).filter(Project.id == project.id).first()

    # Format project for response
    project_dict = updated_project.__dict__.copy()
    project_dict.pop('_sa_instance_state', None)

    # Ensure supplementary_files is a list
    if project_dict.get('supplementary_files') is None:
        project_dict['supplementary_files'] = []

    # Format uploader as dict
    if updated_project.uploader:
        project_dict['uploader'] = {
            'id': updated_project.uploader.id,
            'full_name': updated_project.uploader.full_name,
            'email': updated_project.uploader.email
        }
    else:
        project_dict['uploader'] = None

    return project_dict


# =====================================================
# DELETE PROJECT
# =====================================================
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete project (owner only)
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only owner can delete
    if project.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own projects"
        )
    
    db.delete(project)
    db.commit()
    
    return None


# =====================================================
# GET MY PROJECTS (CURRENT USER)
# =====================================================
@router.get("/me/projects", response_model=List[ProjectRead])
async def get_my_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects uploaded by current user
    """
    projects = db.query(Project).filter(
        Project.uploaded_by == current_user.id
    ).all()

    # Format projects for response
    formatted_projects = []
    for project in projects:
        project_dict = project.__dict__.copy()
        project_dict.pop('_sa_instance_state', None)

        # Ensure supplementary_files is a list
        if project_dict.get('supplementary_files') is None:
            project_dict['supplementary_files'] = []

        # Format uploader as dict
        project_dict['uploader'] = {
            'id': current_user.id,
            'full_name': current_user.full_name,
            'email': current_user.email
        }

        formatted_projects.append(project_dict)

    return formatted_projects
