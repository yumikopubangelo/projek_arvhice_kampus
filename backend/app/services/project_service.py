from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status

from app.models.user import User
from app.models.project import Project, PrivacyLevel, ProjectStatus
from app.models.access_request import AccessRequest, AccessRequestStatus
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead, ProjectSearch


# =====================================================
# PROJECT SERVICE
# =====================================================

class ProjectService:
    """Service class for project-related business logic"""

    @staticmethod
    def create_project(db: Session, project_data: ProjectCreate, uploader_id: int) -> Project:
        """Create a new project"""
        project_dict = project_data.model_dump()

        # Manually convert Pydantic HttpUrl objects to strings for DB compatibility
        for field in ['code_repo_url', 'dataset_url', 'video_url']:
            if project_dict.get(field):
                project_dict[field] = str(project_dict[field])

        # Create project instance
        project = Project(
            **project_dict,
            uploaded_by=uploader_id,
            status=ProjectStatus.ONGOING
        )

        # Generate abstract preview
        if project.abstract:
            project.abstract_preview = project.abstract[:300] + "..." if len(project.abstract) > 300 else project.abstract

        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_project_by_id(db: Session, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        from sqlalchemy.orm import joinedload
        return db.query(Project).options(joinedload(Project.files)).filter(Project.id == project_id).first()

    @staticmethod
    def get_projects(
        db: Session,
        search_params: ProjectSearch,
        current_user: Optional[User] = None
    ) -> List[Project]:
        """Get projects with filtering and access control"""
        query = db.query(Project)

        # Apply search filters
        if search_params.query:
            # Search in title, abstract, authors, tags
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    Project.title.ilike(search_term),
                    Project.abstract.ilike(search_term),
                    func.array_to_string(Project.authors, ' ').ilike(search_term),
                    func.array_to_string(Project.tags, ' ').ilike(search_term)
                )
            )

        if search_params.year:
            query = query.filter(Project.year == search_params.year)

        if search_params.tag:
            query = query.filter(Project.tags.contains([search_params.tag]))

        if search_params.status:
            query = query.filter(Project.status == search_params.status)

        if search_params.privacy_level:
            query = query.filter(Project.privacy_level == search_params.privacy_level)

        if search_params.uploader_id:
            query = query.filter(Project.uploaded_by == search_params.uploader_id)

        if search_params.advisor_id:
            query = query.filter(Project.advisor_id == search_params.advisor_id)

        # Get projects
        projects = query.offset(search_params.skip).limit(search_params.limit).all()

        # Filter by access permissions if user is provided
        if current_user:
            accessible_projects = []
            for project in projects:
                if project.can_access(current_user.id, current_user.role):
                    accessible_projects.append(project)
            projects = accessible_projects

        return projects

    @staticmethod
    def update_project(
        db: Session,
        project: Project,
        update_data: ProjectUpdate,
        user_id: int
    ) -> Project:
        """Update an existing project"""
        # Check ownership
        if project.uploaded_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own projects"
            )

        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Manually convert Pydantic HttpUrl objects to strings for DB compatibility
        for field in ['code_repo_url', 'dataset_url', 'video_url']:
            if field in update_dict and update_dict.get(field):
                update_dict[field] = str(update_dict[field])

        for key, value in update_dict.items():
            setattr(project, key, value)

        # Update abstract preview if abstract changed
        if 'abstract' in update_dict and project.abstract:
            project.abstract_preview = project.abstract[:300] + "..." if len(project.abstract) > 300 else project.abstract

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, project: Project, user_id: int) -> None:
        """Delete a project"""
        # Check ownership
        if project.uploaded_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own projects"
            )

        db.delete(project)
        db.commit()

    @staticmethod
    def increment_view_count(db: Session, project: Project) -> None:
        """Increment project view count"""
        project.view_count += 1
        db.commit()

    @staticmethod
    def increment_download_count(db: Session, project: Project) -> None:
        """Increment project download count"""
        project.download_count += 1
        db.commit()

    @staticmethod
    def check_access(project: Project, user_id: int, user_role: str) -> bool:
        """Check if user can access a project"""
        return project.can_access(user_id, user_role)

    @staticmethod
    def get_user_projects(db: Session, user_id: int) -> List[Project]:
        """Get all projects uploaded by a user"""
        from sqlalchemy.orm import joinedload
        return db.query(Project).options(joinedload(Project.files)).filter(Project.uploaded_by == user_id).all()

    @staticmethod
    def get_advisor_projects(db: Session, advisor_id: int) -> List[Project]:
        """Get all projects advised by a user"""
        return db.query(Project).filter(Project.advisor_id == advisor_id).all()

    @staticmethod
    def search_projects(
        db: Session,
        query: str,
        filters: Dict[str, Any] = None,
        current_user: Optional[User] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Project]:
        """Advanced project search"""
        search_query = db.query(Project)

        # Text search
        if query:
            search_term = f"%{query}%"
            search_query = search_query.filter(
                or_(
                    Project.title.ilike(search_term),
                    Project.abstract.ilike(search_term),
                    func.array_to_string(Project.authors, ' ').ilike(search_term),
                    func.array_to_string(Project.tags, ' ').ilike(search_term)
                )
            )

        # Apply additional filters
        if filters:
            if 'year' in filters:
                search_query = search_query.filter(Project.year == filters['year'])
            if 'tags' in filters:
                for tag in filters['tags']:
                    search_query = search_query.filter(Project.tags.contains([tag]))
            if 'status' in filters:
                search_query = search_query.filter(Project.status == filters['status'])
            if 'privacy_level' in filters:
                search_query = search_query.filter(Project.privacy_level == filters['privacy_level'])

        # Get results
        projects = search_query.offset(skip).limit(limit).all()

        # Filter by access
        if current_user:
            projects = [p for p in projects if p.can_access(current_user.id, current_user.role)]

        return projects

    @staticmethod
    def get_project_stats(db: Session, project_id: int) -> Dict[str, Any]:
        """Get statistics for a project"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None

        return {
            'id': project.id,
            'title': project.title,
            'view_count': project.view_count,
            'download_count': project.download_count,
            'created_at': project.created_at,
            'updated_at': project.updated_at,
            'has_file': project.has_file,
            'status': project.status.value,
            'privacy_level': project.privacy_level.value
        }

    @staticmethod
    def bulk_update_status(
        db: Session,
        project_ids: List[int],
        new_status: ProjectStatus,
        user_id: int
    ) -> int:
        """Bulk update status for multiple projects (admin/owner only)"""
        # For now, only allow users to update their own projects
        updated = db.query(Project).filter(
            and_(
                Project.id.in_(project_ids),
                Project.uploaded_by == user_id
            )
        ).update({'status': new_status})

        db.commit()
        return updated