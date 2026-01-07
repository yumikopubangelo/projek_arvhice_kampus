from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings
from app.routers import auth, projects, search, access

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
)

# =====================================================
# CORS MIDDLEWARE - FIX UNTUK VITE DEV SERVER
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],              # Allow all origins for development
    allow_credentials=True,           # PENTING: Untuk JWT cookies/tokens
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
    expose_headers=["*"],             # Expose all response headers
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


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok", "message": "API is working"}