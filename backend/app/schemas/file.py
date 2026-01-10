from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.models.file import FileType


class ProjectFileBase(BaseModel):
    original_filename: str
    file_type: FileType
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


class ProjectFileCreate(ProjectFileBase):
    saved_path: str
    project_id: int


class ProjectFile(ProjectFileBase):
    id: int
    saved_path: str
    created_at: datetime

    class Config:
        from_attributes = True
