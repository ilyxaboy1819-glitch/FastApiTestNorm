"""add timestamps and is_deleted

Revision ID: e0ae4e84e751
Revises: 43c735cb84b3
Create Date: 2026-03-13 16:09:03.561200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e0ae4e84e751'
down_revision: Union[str, Sequence[str], None] = '789b3121b09c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('applications', sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('categories', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('categories', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('categories', sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('comments', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('comments', sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('profiles', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('profiles', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('profiles', sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('roles', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('roles', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('roles', sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False))


def downgrade() -> None:
    op.drop_column('applications', 'is_deleted')
    op.drop_column('users', 'is_deleted')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('roles', 'is_deleted')
    op.drop_column('roles', 'updated_at')
    op.drop_column('roles', 'created_at')
    op.drop_column('profiles', 'is_deleted')
    op.drop_column('profiles', 'updated_at')
    op.drop_column('profiles', 'created_at')
    op.drop_column('comments', 'is_deleted')
    op.drop_column('comments', 'updated_at')
    op.drop_column('categories', 'is_deleted')
    op.drop_column('categories', 'updated_at')
    op.drop_column('categories', 'created_at')