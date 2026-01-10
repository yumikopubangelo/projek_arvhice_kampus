"""empty message

Revision ID: b94a1430dce0
Revises: add_uuid_to_user, add_video_url
Create Date: 2026-01-08 16:50:43.364673+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b94a1430dce0'
down_revision: str = ('add_uuid_to_user', 'add_video_url')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass