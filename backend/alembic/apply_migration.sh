#!/bin/bash

# =====================================================
# APPLY DATABASE MIGRATION
# =====================================================
# This script applies pending Alembic migrations to the database

set -e  # Exit on error

echo "🚀 Applying database migrations..."
echo ""

# =====================================================
# 1. CHECK ENVIRONMENT
# =====================================================
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    exit 1
fi

# Load .env
export $(cat .env | grep -v '^#' | xargs)

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL not set in .env file"
    exit 1
fi

echo "✅ Environment loaded"
echo ""

# =====================================================
# 2. CHECK CURRENT DATABASE STATE
# =====================================================
echo "📊 Current database state:"
alembic current
echo ""

# =====================================================
# 3. SHOW PENDING MIGRATIONS
# =====================================================
echo "📋 Pending migrations:"
alembic history --indicate-current
echo ""

# =====================================================
# 4. APPLY MIGRATIONS
# =====================================================
read -p "Apply migrations? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "⚙️  Applying migrations..."
    echo ""
    
    alembic upgrade head
    
    echo ""
    echo "✅ Migrations applied successfully!"
    echo ""
    
    # =====================================================
    # 5. VERIFY DATABASE STRUCTURE
    # =====================================================
    echo "🔍 Verifying database structure..."
    echo ""
    
    python3 -c "
from sqlalchemy import create_engine, inspect
import os

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print('📊 Database Tables:')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

for table_name in inspector.get_table_names():
    print(f'\n✅ {table_name}')
    columns = inspector.get_columns(table_name)
    print(f'   Columns: {len(columns)}')
    for col in columns:
        nullable = 'NULL' if col['nullable'] else 'NOT NULL'
        print(f'   - {col[\"name\"]}: {col[\"type\"]} ({nullable})')
    
    # Show indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print(f'   Indexes: {len(indexes)}')
        for idx in indexes:
            print(f'   - {idx[\"name\"]}: {idx[\"column_names\"]}')

print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('✅ Database structure verified!')
"
    
    echo ""
    echo "🎉 All done! Database is ready."
    
else
    echo ""
    echo "ℹ️  Migration cancelled."
fi