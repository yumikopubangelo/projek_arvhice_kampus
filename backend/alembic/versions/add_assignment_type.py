"""add assignment type

Revision ID: add_assignment_type
Revises: fix_phone_column_size
Create Date: 2026-01-07 13:16:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_assignment_type'
down_revision: str = 'fix_phone_column_size'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add assignment_type column to projects table
    op.add_column('projects', sa.Column('assignment_type', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove assignment_type column from projects table
    op.drop_column('projects', 'assignment_type')