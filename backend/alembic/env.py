"""
Alembic Migration Environment Configuration

This file is used by Alembic to generate and run database migrations.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# =====================================================
# FIX PYTHON PATH
# =====================================================
# Get the directory containing alembic/ folder (project root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add to Python path so we can import app.* modules
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# =====================================================
# ALEMBIC CONFIG
# =====================================================
config = context.config

# Setup logging if config file exists
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# =====================================================
# IMPORT SQLALCHEMY BASE & MODELS
# =====================================================
try:
    # Import Base (contains metadata)
    from app.database import Base
    
    # Import ALL models (this registers them with SQLAlchemy)
    from app.models import (
        User, 
        Project, 
        AccessRequest,
        PrivacyLevel,
        ProjectStatus,
        AccessRequestStatus
    )
    
    # Set target metadata for Alembic
    target_metadata = Base.metadata
    
    print(f"✅ Successfully imported {len(target_metadata.tables)} tables:")
    for table_name in target_metadata.tables.keys():
        print(f"   - {table_name}")

except ImportError as e:
    print(f"❌ ERROR: Failed to import models: {e}")
    print(f"   BASE_DIR: {BASE_DIR}")
    print(f"   sys.path: {sys.path}")
    raise

# =====================================================
# DATABASE URL
# =====================================================
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "❌ DATABASE_URL environment variable is not set!\n"
        "   Please create a .env file with DATABASE_URL or set it in your environment.\n"
        "   Example: DATABASE_URL=postgresql://user:pass@localhost:5432/dbname"
    )

# Validate DATABASE_URL format
if not DATABASE_URL.startswith("postgresql"):
    raise ValueError(
        f"❌ Invalid DATABASE_URL: {DATABASE_URL}\n"
        "   Must start with 'postgresql://' or 'postgresql+psycopg2://'"
    )

print(f"✅ Database URL configured: {DATABASE_URL.split('@')[0]}@***")

# Set in Alembic config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# =====================================================
# MIGRATION FUNCTIONS
# =====================================================

def run_migrations_offline():
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate
    a connection with the context.
    """
    # Get Alembic config section
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DATABASE_URL
    
    # Create engine
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Detect column type changes
            compare_server_default=True,  # Detect default value changes
            include_schemas=False,  # Don't include other schemas
            # Add custom naming convention for constraints
            render_as_batch=True,  # For SQLite compatibility (if needed)
        )

        with context.begin_transaction():
            context.run_migrations()


# =====================================================
# MAIN EXECUTION
# =====================================================
if context.is_offline_mode():
    print("🔄 Running migrations in OFFLINE mode...")
    run_migrations_offline()
else:
    print("🔄 Running migrations in ONLINE mode...")
    run_migrations_online()

print("✅ Migration completed successfully!")