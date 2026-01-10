from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Course(Base):
    """
    Course model - represents academic courses managed by lecturers
    """
    __tablename__ = "courses"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Course Information
    course_code = Column(String(20), nullable=False, index=True, comment="Course code (e.g., CS101, ML202)")
    course_name = Column(String(200), nullable=False, comment="Full course name")

    # Academic Context
    semester = Column(String(20), nullable=False, comment="'Ganjil' or 'Genap'")
    year = Column(Integer, nullable=False, index=True)

    # Relationships
    lecturer_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Main lecturer/creator of this course"
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who created this course record"
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # SQLAlchemy Relationships
    lecturer = relationship(
        "User",
        back_populates="created_courses",
        foreign_keys=[lecturer_id]
    )

    creator = relationship(
        "User",
        back_populates="managed_courses",
        foreign_keys=[created_by]
    )

    # Projects relationship (will be added when we update projects model)
    # projects = relationship("Project", back_populates="course")

    def __repr__(self):
        return f"<Course(id={self.id}, code='{self.course_code}', name='{self.course_name[:30]}...', semester={self.semester} {self.year})>"