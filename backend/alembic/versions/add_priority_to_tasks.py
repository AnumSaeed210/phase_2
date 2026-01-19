"""Add priority field to tasks table

Revision ID: 002_add_priority
Revises: None
Create Date: 2026-01-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '002_add_priority'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Add nullable column
    op.add_column('tasks', sa.Column('priority', sa.String(10), nullable=True))

    # Step 2: Set default for existing rows
    op.execute("UPDATE tasks SET priority = 'medium' WHERE priority IS NULL")

    # Step 3: Make non-nullable
    op.alter_column('tasks', 'priority', nullable=False)

    # Step 4: Add check constraint
    op.create_check_constraint(
        'check_priority',
        'tasks',
        "priority IN ('low', 'medium', 'high')"
    )


def downgrade() -> None:
    # Remove check constraint
    op.drop_constraint('check_priority', 'tasks', type_='check')

    # Drop column
    op.drop_column('tasks', 'priority')
