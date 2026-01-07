from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Centralized application configuration.
    Loaded from environment variables or .env file.
    """

    # =====================================================
    # APP
    # =====================================================
    APP_NAME: str = "Campus Archive Platform"
    ENVIRONMENT: str = Field(default="development", description="development | production")
    DEBUG: bool = True

    # =====================================================
    # SECURITY / AUTH
    # =====================================================
    SECRET_KEY: str = Field(..., description="JWT secret key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # =====================================================
    # DATABASE
    # =====================================================
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")

    # =====================================================
    # CORS
    # =====================================================
    CORS_ORIGINS: list[str] = ["*"]  # ganti di production

    # =====================================================
    # FILE UPLOAD
    # =====================================================
    UPLOAD_DIR: str = "/var/uploads/projects"
    MAX_UPLOAD_SIZE_MB: int = 10

    # =====================================================
    # ENCRYPTION
    # =====================================================
    ENCRYPTION_KEY: str = Field(default="campus-archive-secret-key-2024", description="Key for encrypting sensitive data")

    # =====================================================
    # LOGGING
    # =====================================================
    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    Import this instead of creating Settings() manually.
    """
    return Settings()
