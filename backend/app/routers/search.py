from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, and_, func

from app.database import get_db
from app.models.user import User
from app.models.project import Project, PrivacyLevel
from app.schemas.project import ProjectSummary, ProjectSearch
from app.routers.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])


# =====================================================
# SEARCH PROJECTS
# =====================================================
@router.get("/", response_model=List[ProjectSummary])
async def search_projects(
    q: Optional[str] = Query(None, description="Search query for title, abstract, authors, or tags"),
    year: Optional[int] = Query(None, description="Filter by year"),
    tag: Optional[str] = Query(None, description="Filter by specific tag"),
    privacy_level: Optional[PrivacyLevel] = Query(None, description="Filter by privacy level"),
    status: Optional[str] = Query(None, description="Filter by project status"),
    uploader_id: Optional[int] = Query(None, description="Filter by uploader ID"),
    advisor_id: Optional[int] = Query(None, description="Filter by advisor ID"),
    semester: Optional[str] = Query(None, description="Filter by semester"),
    class_name: Optional[str] = Query(None, description="Filter by class name"),
    course_code: Optional[str] = Query(None, description="Filter by course code"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results to return"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search and filter projects with access control
    """
    query = db.query(Project)

    # Apply text search
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Project.title.ilike(search_term),
                Project.abstract.ilike(search_term),
                func.array_to_string(Project.authors, ' ').ilike(search_term),
                func.array_to_string(Project.tags, ' ').ilike(search_term)
            )
        )

    # Apply filters
    if year:
        query = query.filter(Project.year == year)

    if tag:
        # Case-insensitive partial match in tags
        query = query.filter(
            func.array_to_string(Project.tags, ' ').ilike(f'%{tag}%')
        )

    if privacy_level:
        query = query.filter(Project.privacy_level == privacy_level)

    if status:
        query = query.filter(Project.status == status)

    if uploader_id:
        query = query.filter(Project.uploaded_by == uploader_id)

    if advisor_id:
        query = query.filter(Project.advisor_id == advisor_id)

    if semester:
        query = query.filter(Project.semester == semester)

    if class_name:
        query = query.filter(Project.class_name.ilike(f"%{class_name}%"))

    if course_code:
        query = query.filter(Project.course_code.ilike(f"%{course_code}%"))

    # Get results ordered by relevance (newest first for now)
    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    # Apply access control
    accessible_projects = []
    for project in projects:
        if current_user and project.can_access(current_user.id, current_user.role):
            accessible_projects.append(project)
        elif project.privacy_level == PrivacyLevel.PUBLIC:
            # Public projects are accessible to everyone
            accessible_projects.append(project)

    # Convert to summary format
    results = []
    for project in accessible_projects:
        # Get uploader info
        uploader = db.query(User).filter(User.id == project.uploaded_by).first()
        uploader_name = uploader.full_name if uploader else None

        # Get advisor info
        advisor_name = None
        if project.advisor_id:
            advisor = db.query(User).filter(User.id == project.advisor_id).first()
            advisor_name = advisor.full_name if advisor else None

        results.append(ProjectSummary(
            id=project.id,
            title=project.title,
            abstract_preview=project.abstract_preview,
            authors=project.authors,
            tags=project.tags,
            year=project.year,
            semester=project.semester,
            status=project.status,
            privacy_level=project.privacy_level,
            uploaded_by=project.uploaded_by,
            advisor_id=project.advisor_id,
            view_count=project.view_count,
            created_at=project.created_at,
            uploader_name=uploader_name,
            advisor_name=advisor_name
        ))

    return results


# =====================================================
# GET SEARCH SUGGESTIONS
# =====================================================
@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Partial search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on partial query
    """
    suggestions = {
        "titles": [],
        "authors": [],
        "tags": [],
        "courses": []
    }

    # Get title suggestions
    titles = db.query(Project.title).filter(
        Project.title.ilike(f"{q}%")
    ).distinct().limit(limit).all()
    suggestions["titles"] = [title[0] for title in titles]

    # Get author suggestions
    # This is more complex due to array field
    authors_query = db.query(func.unnest(Project.authors).label('author')).filter(
        func.unnest(Project.authors).ilike(f"{q}%")
    ).distinct().limit(limit)
    authors = authors_query.all()
    suggestions["authors"] = [author[0] for author in authors]

    # Get tag suggestions
    tags_query = db.query(func.unnest(Project.tags).label('tag')).filter(
        func.unnest(Project.tags).ilike(f"{q}%")
    ).distinct().limit(limit)
    tags = tags_query.all()
    suggestions["tags"] = [tag[0] for tag in tags]

    # Get course code suggestions
    courses = db.query(Project.course_code).filter(
        Project.course_code.ilike(f"{q}%")
    ).distinct().limit(limit).all()
    suggestions["courses"] = [course[0] for course in courses if course[0]]

    return suggestions


# =====================================================
# GET SEARCH FILTERS
# =====================================================
@router.get("/filters")
async def get_search_filters(
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available filter options for search
    """
    filters = {}

    # Get available years
    years = db.query(Project.year).distinct().order_by(Project.year.desc()).all()
    filters["years"] = [year[0] for year in years]

    # Get available tags (most common)
    tags_query = db.query(
        func.unnest(Project.tags).label('tag'),
        func.count().label('count')
    ).group_by(func.unnest(Project.tags)).order_by(func.count().desc()).limit(50)
    tags = tags_query.all()
    filters["tags"] = [{"tag": tag[0], "count": tag[1]} for tag in tags]

    # Get available semesters
    semesters = db.query(Project.semester).distinct().filter(
        Project.semester.isnot(None)
    ).order_by(Project.semester).all()
    filters["semesters"] = [sem[0] for sem in semesters if sem[0]]

    # Get available course codes
    courses = db.query(Project.course_code).distinct().filter(
        Project.course_code.isnot(None)
    ).order_by(Project.course_code).all()
    filters["course_codes"] = [course[0] for course in courses if course[0]]

    # Get available class names
    classes = db.query(Project.class_name).distinct().filter(
        Project.class_name.isnot(None)
    ).order_by(Project.class_name).all()
    filters["class_names"] = [cls[0] for cls in classes if cls[0]]

    return filters


# =====================================================
# ADVANCED SEARCH
# =====================================================
@router.post("/advanced", response_model=List[ProjectSummary])
async def advanced_search(
    search_params: ProjectSearch,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Advanced search with complex filtering
    """
    # Use the same logic as basic search but with structured parameters
    return await search_projects(
        q=search_params.query,
        year=search_params.year,
        tag=search_params.tag,
        privacy_level=search_params.privacy_level,
        status=search_params.status,
        uploader_id=search_params.uploader_id,
        advisor_id=search_params.advisor_id,
        skip=search_params.skip,
        limit=search_params.limit,
        current_user=current_user,
        db=db
    )


# =====================================================
# GET POPULAR TAGS
# =====================================================
@router.get("/popular-tags")
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100, description="Number of tags to return"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get most popular tags across all accessible projects
    """
    # Get projects user can access
    query = db.query(Project)

    if current_user:
        # Complex access control query - for simplicity, get public projects and user's projects
        query = query.filter(
            or_(
                Project.privacy_level == PrivacyLevel.PUBLIC,
                Project.uploaded_by == current_user.id,
                Project.advisor_id == current_user.id
            )
        )
    else:
        # Anonymous users only see public projects
        query = query.filter(Project.privacy_level == PrivacyLevel.PUBLIC)

    # Get tag counts
    tags_query = db.query(
        func.unnest(Project.tags).label('tag'),
        func.count().label('count')
    ).filter(
        Project.id.in_(
            query.with_entities(Project.id).subquery()
        )
    ).group_by(func.unnest(Project.tags)).order_by(func.count().desc()).limit(limit)

    tags = tags_query.all()
    return [{"tag": tag[0], "count": tag[1]} for tag in tags]