from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, projects, search, access

# =====================================================
# LOAD SETTINGS
# =====================================================
settings = get_settings()

# =====================================================
# FASTAPI APPLICATION
# =====================================================
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
)

# =====================================================
# CORS MIDDLEWARE
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# ROUTERS
# =====================================================
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(access.router, prefix="/api", tags=["access"])

# =====================================================
# ROOT & HEALTH CHECK
# =====================================================
@app.get("/", tags=["root"])
def root():
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
