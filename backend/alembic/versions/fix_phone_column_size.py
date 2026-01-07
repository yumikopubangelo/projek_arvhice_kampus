"""fix phone column size

Revision ID: fix_phone_column_size
Revises: 442648875932
Create Date: 2026-01-07 12:22:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_phone_column_size'
down_revision: str = '442648875932'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alter phone column to increase size to accommodate encrypted data
    op.alter_column('users', 'phone',
                    existing_type=sa.String(length=20),
                    type_=sa.String(length=255),
                    existing_nullable=True)


def downgrade() -> None:
    # Revert phone column size back to 20
    op.alter_column('users', 'phone',
                    existing_type=sa.String(length=255),
                    type_=sa.String(length=20),
                    existing_nullable=True)