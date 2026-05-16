"""add local_orders table

Revision ID: a1b2c3d4e5f6
Revises: 789b3121b09c
Create Date: 2026-05-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.models.order import OrderStatus


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '789b3121b09c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table(
        'local_orders',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('external_id', sa.UUID(), nullable=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default=OrderStatus.NEW.value),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('local_orders')
