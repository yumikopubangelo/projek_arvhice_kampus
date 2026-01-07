#!/bin/bash

# =====================================================
# CREATE INITIAL DATABASE MIGRATION
# =====================================================
# This script generates the first Alembic migration
# based on your SQLAlchemy models

set -e  # Exit on error

echo "🚀 Creating initial database migration..."
echo ""

# =====================================================
# 1. CHECK ENVIRONMENT
# =====================================================
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo "   Please create .env file with DATABASE_URL"
    echo "   Example: DATABASE_URL=postgresql://user:pass@localhost:5432/dbname"
    exit 1
fi

# Load .env
export $(cat .env | grep -v '^#' | xargs)

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL not set in .env file"
    exit 1
fi

echo "✅ Environment loaded"
echo "   DATABASE_URL: ${DATABASE_URL%%@*}@***"
echo ""

# =====================================================
# 2. CHECK PYTHON ENVIRONMENT
# =====================================================
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 not found"
    exit 1
fi

echo "✅ Python version: $(python3 --version)"
echo ""

# =====================================================
# 3. CHECK ALEMBIC INSTALLED
# =====================================================
if ! python3 -c "import alembic" 2>/dev/null; then
    echo "❌ ERROR: Alembic not installed"
    echo "   Install with: pip install alembic"
    exit 1
fi

echo "✅ Alembic installed"
echo ""

# =====================================================
# 4. VERIFY MODELS CAN BE IMPORTED
# =====================================================
echo "🔍 Verifying models..."

python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from app.database import Base
    from app.models import User, Project, AccessRequest
    
    print(f'✅ Found {len(Base.metadata.tables)} tables:')
    for table_name in Base.metadata.tables.keys():
        print(f'   - {table_name}')
    
except ImportError as e:
    print(f'❌ ERROR importing models: {e}')
    sys.exit(1)
" || exit 1

echo ""

# =====================================================
# 5. CHECK IF MIGRATIONS DIRECTORY EXISTS
# =====================================================
if [ ! -d "alembic/versions" ]; then
    echo "📁 Creating alembic/versions directory..."
    mkdir -p alembic/versions
fi

# =====================================================
# 6. DELETE OLD MIGRATIONS (OPTIONAL - BE CAREFUL!)
# =====================================================
read -p "⚠️  Delete existing migrations? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Deleting old migrations..."
    rm -f alembic/versions/*.py
    echo "   Done"
fi

echo ""

# =====================================================
# 7. GENERATE MIGRATION
# =====================================================
echo "📝 Generating initial migration..."
echo ""

alembic revision --autogenerate -m "Initial migration: users, projects, access_requests"

echo ""
echo "✅ Migration generated successfully!"
echo ""

# =====================================================
# 8. SHOW MIGRATION FILE
# =====================================================
LATEST_MIGRATION=$(ls -t alembic/versions/*.py | head -1)

if [ -f "$LATEST_MIGRATION" ]; then
    echo "📄 Migration file created: $LATEST_MIGRATION"
    echo ""
    echo "Preview (first 30 lines):"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    head -30 "$LATEST_MIGRATION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

echo ""
echo "🎯 Next steps:"
echo "   1. Review the migration file above"
echo "   2. Apply migration: alembic upgrade head"
echo "   3. Or run: ./apply_migration.sh"