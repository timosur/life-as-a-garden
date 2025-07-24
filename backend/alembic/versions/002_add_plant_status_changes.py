"""Add plant status changes table

Revision ID: 002
Revises: 001
Create Date: 2025-07-23 12:01:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Plant status changes table to track all status changes
    op.create_table(
        "plant_status_changes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("change_date", sa.Date(), nullable=False),
        sa.Column("change_type", sa.Text(), nullable=False),
        sa.Column("old_health", sa.Text(), nullable=False),
        sa.Column("new_health", sa.Text(), nullable=False),
        sa.Column("old_growth_stage", sa.Integer(), nullable=False),
        sa.Column("new_growth_stage", sa.Integer(), nullable=False),
        sa.Column("old_water_streak", sa.Integer(), nullable=False),
        sa.Column("new_water_streak", sa.Integer(), nullable=False),
        sa.Column("old_days_without_water", sa.Integer(), nullable=False),
        sa.Column("new_days_without_water", sa.Integer(), nullable=False),
        sa.Column("old_total_water_count", sa.Integer(), nullable=False),
        sa.Column("new_total_water_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
    )

    # Create indexes for the new table
    op.create_index(
        "idx_plant_status_changes_plant", "plant_status_changes", ["plant_id"]
    )
    op.create_index(
        "idx_plant_status_changes_date", "plant_status_changes", ["change_date"]
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_plant_status_changes_date")
    op.drop_index("idx_plant_status_changes_plant")

    # Drop table
    op.drop_table("plant_status_changes")
