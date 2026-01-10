from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional

from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate, CourseRead, CourseSummary


class CourseService:
    """Service class for course-related operations"""

    @staticmethod
    def create_course(db: Session, course_data: CourseCreate, lecturer_id: int) -> Course:
        """Create a new course"""
        # Check if course code already exists for this lecturer in the same semester/year
        existing_course = db.query(Course).filter(
            and_(
                Course.course_code == course_data.course_code,
                Course.lecturer_id == lecturer_id,
                Course.semester == course_data.semester,
                Course.year == course_data.year
            )
        ).first()

        if existing_course:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=f"Course code '{course_data.course_code}' already exists for {course_data.semester} {course_data.year}"
            )

        # Create new course
        new_course = Course(
            course_code=course_data.course_code,
            course_name=course_data.course_name,
            semester=course_data.semester,
            year=course_data.year,
            lecturer_id=lecturer_id,
            created_by=lecturer_id
        )

        db.add(new_course)
        db.commit()
        db.refresh(new_course)

        return new_course

    @staticmethod
    def get_course_by_id(db: Session, course_id: int) -> Optional[Course]:
        """Get course by ID"""
        return db.query(Course).filter(Course.id == course_id).first()

    @staticmethod
    def get_lecturer_courses(db: Session, lecturer_id: int) -> List[Course]:
        """Get all courses for a specific lecturer"""
        return db.query(Course).filter(Course.lecturer_id == lecturer_id).order_by(
            Course.year.desc(), Course.semester.desc(), Course.course_code
        ).all()

    @staticmethod
    def get_course_with_details(db: Session, course_id: int) -> Optional[CourseRead]:
        """Get course with lecturer and creator details"""
        course = db.query(Course).filter(Course.id == course_id).first()
        if course:
            # Populate related data
            course.lecturer = db.query(User).filter(User.id == course.lecturer_id).first()
            course.creator = db.query(User).filter(User.id == course.created_by).first()
        return course

    @staticmethod
    def update_course(db: Session, course_id: int, course_data: CourseUpdate, lecturer_id: int) -> Optional[Course]:
        """Update course information"""
        course = db.query(Course).filter(
            and_(Course.id == course_id, Course.lecturer_id == lecturer_id)
        ).first()

        if not course:
            return None

        # Check for duplicate course code if course_code is being updated
        if course_data.course_code and course_data.course_code != course.course_code:
            existing_course = db.query(Course).filter(
                and_(
                    Course.course_code == course_data.course_code,
                    Course.lecturer_id == lecturer_id,
                    Course.semester == (course_data.semester or course.semester),
                    Course.year == (course_data.year or course.year),
                    Course.id != course_id
                )
            ).first()

            if existing_course:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=400,
                    detail=f"Course code '{course_data.course_code}' already exists for this semester/year"
                )

        # Update fields
        update_data = course_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(course, key, value)

        db.commit()
        db.refresh(course)

        return course

    @staticmethod
    def delete_course(db: Session, course_id: int, lecturer_id: int) -> bool:
        """Delete course (only by the lecturer who created it)"""
        course = db.query(Course).filter(
            and_(Course.id == course_id, Course.lecturer_id == lecturer_id)
        ).first()

        if not course:
            return False

        # TODO: Check if course has associated projects before deletion
        # For now, allow deletion

        db.delete(course)
        db.commit()

        return True

    @staticmethod
    def get_course_summaries(db: Session, lecturer_id: int) -> List[CourseSummary]:
        """Get course summaries for a lecturer"""
        courses = db.query(Course).filter(Course.lecturer_id == lecturer_id).order_by(
            Course.year.desc(), Course.semester.desc(), Course.course_code
        ).all()

        summaries = []
        for course in courses:
            lecturer = db.query(User).filter(User.id == course.lecturer_id).first()
            summary = CourseSummary(
                id=course.id,
                course_code=course.course_code,
                course_name=course.course_name,
                semester=course.semester,
                year=course.year,
                lecturer_name=lecturer.full_name if lecturer else None
            )
            summaries.append(summary)

        return summaries

    @staticmethod
    def search_courses(db: Session, lecturer_id: int, query: Optional[str] = None, year: Optional[int] = None) -> List[Course]:
        """Search courses by lecturer"""
        q = db.query(Course).filter(Course.lecturer_id == lecturer_id)

        if query:
            # Search in course code or name
            search_filter = f"%{query}%"
            q = q.filter(
                or_(
                    Course.course_code.ilike(search_filter),
                    Course.course_name.ilike(search_filter)
                )
            )

        if year:
            q = q.filter(Course.year == year)

        return q.order_by(Course.year.desc(), Course.semester.desc(), Course.course_code).all()