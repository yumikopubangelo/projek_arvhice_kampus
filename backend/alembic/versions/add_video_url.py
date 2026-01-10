"""add video_url

Revision ID: add_video_url
Revises: add_assignment_type
Create Date: 2026-01-08 13:19:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_video_url'
down_revision: str = 'add_assignment_type'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add video_url column to projects table
    op.add_column('projects', sa.Column('video_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove video_url column from projects table
    op.drop_column('projects', 'video_url')