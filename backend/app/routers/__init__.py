"""
API Routers Package

Contains all FastAPI router modules for the Campus Archive API.
"""

from app.routers.auth import router as auth_router
from app.routers.projects import router as projects_router
from app.routers.access import router as access_router
from app.routers.search import router as search_router
from app.routers.files import router as files_router

# Export routers for easy inclusion in main app
__all__ = [
    "auth_router",
    "projects_router",
    "access_router",
    "search_router",
    "files_router"
]