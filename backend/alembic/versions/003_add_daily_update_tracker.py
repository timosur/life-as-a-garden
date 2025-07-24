"""Add daily update tracker table

Revision ID: 003
Revises: 002
Create Date: 2025-07-24 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create daily_update_tracker table
    op.create_table(
        "daily_update_tracker",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("update_date", sa.String(10), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=False),
        sa.Column("plants_processed", sa.Integer(), nullable=False, default=0),
        sa.Column("plants_updated", sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("update_date", name="unique_update_date"),
    )

    # Create index for faster date lookups
    op.create_index("idx_daily_update_date", "daily_update_tracker", ["update_date"])


def downgrade() -> None:
    op.drop_index("idx_daily_update_date", table_name="daily_update_tracker")
    op.drop_table("daily_update_tracker")
