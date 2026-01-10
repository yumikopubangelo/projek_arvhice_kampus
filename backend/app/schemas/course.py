from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from .user import UserRead


class CourseBase(BaseModel):
    """Base course schema with common fields"""
    course_code: str = Field(..., max_length=20, description="Course code (e.g., CS101, ML202)")
    course_name: str = Field(..., max_length=200, description="Full course name")
    semester: str = Field(..., max_length=20, description="'Ganjil' or 'Genap'")
    year: int = Field(..., ge=2000, le=2100, description="Academic year")


class CourseCreate(CourseBase):
    """Schema for creating new courses"""
    pass

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "course_code": "CS101",
            "course_name": "Introduction to Computer Science",
            "semester": "Ganjil",
            "year": 2024
        }
    })


class CourseRead(CourseBase):
    """Schema for course responses (read operations)"""
    id: int
    lecturer_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    # Related data (optional, populated by service layer)
    lecturer: Optional[UserRead] = None
    creator: Optional[UserRead] = None

    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "course_code": "CS101",
            "course_name": "Introduction to Computer Science",
            "semester": "Ganjil",
            "year": 2024,
            "lecturer_id": 2,
            "created_by": 2,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "lecturer": {
                "id": 2,
                "email": "lecturer@university.edu",
                "full_name": "Dr. Jane Smith",
                "role": "dosen"
            }
        }
    })


class CourseUpdate(BaseModel):
    """Schema for updating existing courses"""
    course_code: Optional[str] = Field(None, max_length=20)
    course_name: Optional[str] = Field(None, max_length=200)
    semester: Optional[str] = Field(None, max_length=20)
    year: Optional[int] = Field(None, ge=2000, le=2100)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "course_name": "Advanced Computer Science",
            "year": 2025
        }
    })


class CourseSummary(BaseModel):
    """Simplified course info for listings"""
    id: int
    course_code: str
    course_name: str
    semester: str
    year: int
    lecturer_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)