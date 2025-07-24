"""Add size fields to plant status changes table

Revision ID: 004
Revises: 003
Create Date: 2025-07-24 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add old_size and new_size columns to plant_status_changes table
    op.add_column(
        "plant_status_changes", sa.Column("old_size", sa.Text(), nullable=True)
    )
    op.add_column(
        "plant_status_changes", sa.Column("new_size", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    # Remove the size columns
    op.drop_column("plant_status_changes", "new_size")
    op.drop_column("plant_status_changes", "old_size")
