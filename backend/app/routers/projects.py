import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.project import Project, PrivacyLevel, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.routers.auth import get_current_user
from app.services.file_service import save_project_file, save_supplementary_file, validate_file_extension, validate_total_size, ALLOWED_EXTENSIONS, delete_project_files, delete_file
from app.utils.encryption import decrypt_sensitive_fields
from app.config import get_settings

settings = get_settings()

def get_file_info(file_paths):
    """
    Get file information including sizes for a list of file paths
    """
    file_info = []
    for path in file_paths:
        if path:
            full_path = os.path.join(settings.UPLOAD_DIR, path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                filename = os.path.basename(path)
                file_info.append({
                    'path': path,
                    'name': filename,
                    'size': size
                })
            else:
                # File doesn't exist, still include with size 0
                filename = os.path.basename(path)
                file_info.append({
                    'path': path,
                    'name': filename,
                    'size': 0
                })
    return file_info

def format_project_response(project, include_private=True):
    """
    Format project for API response with file information
    """
    project_dict = project.__dict__.copy()
    project_dict.pop('_sa_instance_state', None)

    # Ensure supplementary_files is a list
    if project_dict.get('supplementary_files') is None:
        project_dict['supplementary_files'] = []

    # Add file information with sizes
    if include_private and project_dict['supplementary_files']:
        project_dict['supplementary_files_info'] = get_file_info(project_dict['supplementary_files'])
    else:
        project_dict['supplementary_files_info'] = []

    # Format uploader as dict
    if hasattr(project, 'uploader') and project.uploader:
        project_dict['uploader'] = {
            'id': project.uploader.id,
            'uuid': project.uploader.uuid,
            'full_name': project.uploader.full_name,
            'email': project.uploader.email
        }
    else:
        project_dict['uploader'] = None

    return project_dict

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
    video_url: Optional[str] = Form(None),
    advisor_id: Optional[int] = Form(None),
    # File uploads
    pdf_file: UploadFile = File(...),
    supplementary_files: List[UploadFile] = File([]),
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
        video_url=video_url,
        uploaded_by=current_user.id,
        advisor_id=advisor_id
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Save files first, then validate total size
    saved_files = []

    try:
        # Save PDF file (mandatory)
        pdf_path, pdf_size = await save_project_file(pdf_file, current_user.uuid)
        new_project.pdf_file_path = pdf_path
        new_project.pdf_file_size = pdf_size
        saved_files.append(pdf_path)

        # Save supplementary files
        supp_paths = []
        total_supp_size = 0

        if supplementary_files:
            for upload_file in supplementary_files:
                # Validate file extension
                all_allowed = []
                for ext_list in ALLOWED_EXTENSIONS.values():
                    all_allowed.extend(ext_list)
                validate_file_extension(upload_file.filename, all_allowed)

                path, size = await save_supplementary_file(upload_file, current_user.uuid)
                supp_paths.append(path)
                saved_files.append(path)
                total_supp_size += size

        # Validate total size
        total_size = pdf_size + total_supp_size
        validate_total_size(total_size)

        new_project.supplementary_files = supp_paths
        db.commit()

    except Exception as e:
        # If validation fails or any error occurs, delete saved files
        for file_path in saved_files:
            delete_file(file_path)
        raise e

    # Load the project with relationships for proper serialization
    project = db.query(Project).options(
        joinedload(Project.uploader)
    ).filter(Project.id == new_project.id).first()

    # Format project for response
    return format_project_response(project, include_private=True)


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

        # Format project with file info
        project_dict = format_project_response(project, include_private=can_access_full)

        # Hide private content if user cannot access full content
        if not can_access_full:
            project_dict['pdf_file_path'] = None
            project_dict['pdf_file_size'] = None
            project_dict['supplementary_files'] = []
            project_dict['supplementary_files_info'] = []
            project_dict['code_repo_url'] = None
            project_dict['dataset_url'] = None

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

    # Format project with file info
    project_dict = format_project_response(project, include_private=can_access_full)

    # Hide private content if user cannot access full content
    if not can_access_full:
        project_dict['pdf_file_path'] = None
        project_dict['pdf_file_size'] = None
        project_dict['supplementary_files'] = []
        project_dict['supplementary_files_info'] = []
        project_dict['code_repo_url'] = None
        project_dict['dataset_url'] = None

    return project_dict


# =====================================================
# UPDATE PROJECT
# =====================================================
@router.put("/{project_id}", response_model=ProjectRead)
@router.patch("/{project_id}", response_model=ProjectRead)  # Also support PATCH
async def update_project(
    project_id: int,
    # Form data for file uploads
    title: Optional[str] = Form(None),
    abstract: Optional[str] = Form(None),
    authors: Optional[str] = Form(None),  # Comma-separated
    tags: Optional[str] = Form(None),     # Comma-separated
    year: Optional[int] = Form(None),
    semester: Optional[str] = Form(None),
    class_name: Optional[str] = Form(None),
    course_code: Optional[str] = Form(None),
    assignment_type: Optional[str] = Form(None),
    privacy_level: Optional[str] = Form(None),
    code_repo_url: Optional[str] = Form(None),
    dataset_url: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
    advisor_id: Optional[int] = Form(None),
    # File uploads
    pdf_file: Optional[UploadFile] = File(None),
    supplementary_files: Optional[List[UploadFile]] = File([]),
    # Auth & DB
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update project (owner only) - supports both JSON and multipart form data
    """
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

    # Prepare update data
    update_data = {}

    # Handle form fields
    if title is not None:
        update_data['title'] = title
    if abstract is not None:
        update_data['abstract'] = abstract
    if authors is not None:
        update_data['authors'] = [a.strip() for a in authors.split(",")]
    if tags is not None:
        update_data['tags'] = [t.strip() for t in tags.split(",")]
    if year is not None:
        update_data['year'] = year
    if semester is not None:
        update_data['semester'] = semester
    if class_name is not None:
        update_data['class_name'] = class_name
    if course_code is not None:
        update_data['course_code'] = course_code
    if assignment_type is not None:
        update_data['assignment_type'] = assignment_type
    if privacy_level is not None:
        update_data['privacy_level'] = PrivacyLevel(privacy_level)
    if code_repo_url is not None:
        update_data['code_repo_url'] = code_repo_url if code_repo_url else None
    if dataset_url is not None:
        update_data['dataset_url'] = dataset_url if dataset_url else None
    if video_url is not None:
        update_data['video_url'] = video_url if video_url else None
    if advisor_id is not None:
        update_data['advisor_id'] = advisor_id

    # Handle file uploads
    saved_files = []

    try:
        # Handle PDF file upload
        if pdf_file is not None:
            # Delete old PDF file if exists
            if project.pdf_file_path:
                delete_file(project.pdf_file_path)

            pdf_path, pdf_size = await save_project_file(pdf_file, current_user.uuid)
            update_data['pdf_file_path'] = pdf_path
            update_data['pdf_file_size'] = pdf_size
            saved_files.append(pdf_path)

        # Handle supplementary files upload
        if supplementary_files:
            # Validate extensions
            all_allowed = []
            for ext_list in ALLOWED_EXTENSIONS.values():
                all_allowed.extend(ext_list)

            new_supp_paths = []
            for upload_file in supplementary_files:
                validate_file_extension(upload_file.filename, all_allowed)
                path, _ = await save_supplementary_file(upload_file, current_user.uuid)
                new_supp_paths.append(path)
                saved_files.append(path)

            # Merge with existing supplementary files
            existing_supp = project.supplementary_files or []
            update_data['supplementary_files'] = existing_supp + new_supp_paths

        # Validate total size if files were uploaded
        if saved_files:
            total_size = 0
            if 'pdf_file_size' in update_data:
                total_size += update_data['pdf_file_size']

            # Calculate size of all supplementary files
            all_supp_files = update_data.get('supplementary_files', project.supplementary_files or [])
            for file_path in all_supp_files:
                file_info = get_file_info(file_path)
                if file_info:
                    total_size += file_info['size']

            validate_total_size(total_size)

        # Apply updates
        for key, value in update_data.items():
            setattr(project, key, value)

        # Update abstract preview if abstract changed
        if 'abstract' in update_data:
            project.abstract_preview = update_data['abstract'][:300] + "..." if len(update_data['abstract']) > 300 else update_data['abstract']

        db.commit()
        db.refresh(project)

    except Exception as e:
        # If any error occurs, delete newly saved files
        for file_path in saved_files:
            delete_file(file_path)
        raise e

    # Load the project with relationships for proper serialization
    updated_project = db.query(Project).options(
        joinedload(Project.uploader)
    ).filter(Project.id == project.id).first()

    # Format project for response
    return format_project_response(updated_project, include_private=True)


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

    # Collect file paths to delete
    file_paths = []
    if project.pdf_file_path:
        file_paths.append(project.pdf_file_path)
    if project.supplementary_files:
        file_paths.extend(project.supplementary_files)

    # Delete project from DB
    db.delete(project)
    db.commit()

    # Delete associated files
    if file_paths:
        delete_project_files(file_paths)

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
        # Format project with file info (owner can see all)
        project_dict = format_project_response(project, include_private=True)

        # Override uploader with current user info
        project_dict['uploader'] = {
            'id': current_user.id,
            'full_name': current_user.full_name,
            'email': current_user.email
        }

        formatted_projects.append(project_dict)

    return formatted_projects
