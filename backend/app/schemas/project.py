from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum


# =====================================================
# ENUMS (MIRRORING MODEL ENUMS)
# =====================================================

class PrivacyLevel(str, Enum):
    """Privacy levels for projects"""
    PRIVATE = "private"
    ADVISOR = "advisor"
    CLASS = "class"
    PUBLIC = "public"


class ProjectStatus(str, Enum):
    """Project completion status"""
    ONGOING = "ongoing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# =====================================================
# PROJECT SCHEMAS
# =====================================================

class ProjectBase(BaseModel):
    """Base project schema with common fields"""
    title: str = Field(..., max_length=500)
    abstract: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    year: int
    semester: Optional[str] = None
    class_name: Optional[str] = None
    course_code: Optional[str] = None
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE
    code_repo_url: Optional[HttpUrl] = None
    dataset_url: Optional[HttpUrl] = None


class ProjectCreate(ProjectBase):
    """Schema for creating new projects"""
    pass  # Inherits all fields from ProjectBase

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "Machine Learning Analysis of Student Performance",
            "abstract": "This project analyzes student performance data using various ML algorithms...",
            "authors": ["John Doe", "Jane Smith"],
            "tags": ["Machine Learning", "Data Analysis", "Python"],
            "year": 2024,
            "semester": "Ganjil",
            "class_name": "Computer Science 101",
            "course_code": "CS101",
            "privacy_level": "private",
            "code_repo_url": "https://github.com/johndoe/ml-student-analysis",
            "dataset_url": "https://example.com/dataset.csv"
        }
    })


class ProjectRead(ProjectBase):
    """Schema for project responses (read operations)"""
    id: int
    abstract_preview: Optional[str] = None
    status: ProjectStatus
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    supplementary_files: List[str] = Field(default_factory=list)
    uploaded_by: int
    advisor_id: Optional[int] = None
    view_count: int
    download_count: int
    created_at: datetime
    updated_at: datetime

    # Related data (optional, populated by service layer)
    uploader: Optional[dict] = None  # Simplified user info
    advisor: Optional[dict] = None   # Simplified user info

    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "title": "Machine Learning Analysis of Student Performance",
            "abstract": "This project analyzes student performance data using various ML algorithms...",
            "abstract_preview": "This project analyzes student performance data using various ML algorithms...",
            "authors": ["John Doe", "Jane Smith"],
            "tags": ["Machine Learning", "Data Analysis", "Python"],
            "year": 2024,
            "semester": "Ganjil",
            "class_name": "Computer Science 101",
            "course_code": "CS101",
            "status": "ongoing",
            "privacy_level": "private",
            "pdf_file_path": "/uploads/projects/1/project.pdf",
            "pdf_file_size": 2048576,
            "code_repo_url": "https://github.com/johndoe/ml-student-analysis",
            "dataset_url": "https://example.com/dataset.csv",
            "supplementary_files": ["/uploads/projects/1/data.csv", "/uploads/projects/1/results.png"],
            "uploaded_by": 1,
            "advisor_id": 2,
            "view_count": 15,
            "download_count": 3,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "uploader": {
                "id": 1,
                "full_name": "John Doe",
                "email": "john@university.edu"
            },
            "advisor": {
                "id": 2,
                "full_name": "Dr. Jane Smith",
                "email": "jane@university.edu"
            }
        }
    })


class ProjectUpdate(BaseModel):
    """Schema for updating existing projects"""
    title: Optional[str] = Field(None, max_length=500)
    abstract: Optional[str] = None
    authors: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    semester: Optional[str] = None
    class_name: Optional[str] = None
    course_code: Optional[str] = None
    status: Optional[ProjectStatus] = None
    privacy_level: Optional[PrivacyLevel] = None
    code_repo_url: Optional[HttpUrl] = None
    dataset_url: Optional[HttpUrl] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "Updated: Machine Learning Analysis of Student Performance",
            "status": "completed",
            "privacy_level": "advisor"
        }
    })


class ProjectSearch(BaseModel):
    """Schema for project search parameters"""
    query: Optional[str] = None
    year: Optional[int] = None
    tag: Optional[str] = None
    privacy_level: Optional[PrivacyLevel] = None
    status: Optional[ProjectStatus] = None
    uploader_id: Optional[int] = None
    advisor_id: Optional[int] = None
    skip: int = 0
    limit: int = 20

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "query": "machine learning",
            "year": 2024,
            "tag": "Python",
            "privacy_level": "public",
            "skip": 0,
            "limit": 10
        }
    })


class ProjectSummary(BaseModel):
    """Simplified project info for listings/search results"""
    id: int
    title: str
    abstract_preview: Optional[str] = None
    authors: List[str]
    tags: List[str]
    year: int
    semester: Optional[str] = None
    status: ProjectStatus
    privacy_level: PrivacyLevel
    uploaded_by: int
    advisor_id: Optional[int] = None
    view_count: int
    created_at: datetime

    # Related data
    uploader_name: Optional[str] = None
    advisor_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)