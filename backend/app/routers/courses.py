from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate, CourseSummary
from app.services.course_service import CourseService
from app.dependencies.dependencies import get_current_active_user, require_dosen

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(require_dosen),
    db: Session = Depends(get_db)
):
    """
    Create a new course (lecturers only)
    """
    try:
        course = CourseService.create_course(db, course_data, current_user.id)
        return CourseService.get_course_with_details(db, course.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[CourseSummary])
async def get_my_courses(
    current_user: User = Depends(require_dosen),
    db: Session = Depends(get_db)
):
    """
    Get all courses for the current lecturer
    """
    return CourseService.get_course_summaries(db, current_user.id)


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(
    course_id: int,
    current_user: User = Depends(require_dosen),
    db: Session = Depends(get_db)
):
    """
    Get a specific course by ID (only if lecturer owns it)
    """
    course = CourseService.get_course_with_details(db, course_id)

    if not course or course.lecturer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    return course


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(require_dosen),
    db: Session = Depends(get_db)
):
    """
    Update a course (only by the lecturer who created it)
    """
    try:
        course = CourseService.update_course(db, course_id, course_data, current_user.id)

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        return CourseService.get_course_with_details(db, course.id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    current_user: User = Depends(require_dosen),
    db: Session = Depends(get_db)
):
    """
    Delete a course (only by the lecturer who created it)
    """
    success = CourseService.delete_course(db, course_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )


@router.get("/search/", response_model=List[CourseSummary])
async def search_courses(
    query: Optional[str] = Query(None, description="Search in course code or name"),
    year: Optional[int] = Query(None, description="Filter by year"),
    current_user: User = Depends(require_dosen),
    db: Session = Depends(get_db)
):
    """
    Search courses by lecturer with optional filters
    """
    courses = CourseService.search_courses(db, current_user.id, query, year)

    # Convert to summaries
    summaries = []
    for course in courses:
        summary = CourseSummary(
            id=course.id,
            course_code=course.course_code,
            course_name=course.course_name,
            semester=course.semester,
            year=course.year,
            lecturer_name=current_user.full_name
        )
        summaries.append(summary)

    return summaries