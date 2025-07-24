"""Initial schema creation

Revision ID: 001
Revises:
Create Date: 2025-07-23 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Areals table
    op.create_table(
        "areals",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("horizontal_pos", sa.Text(), nullable=False),
        sa.Column("vertical_pos", sa.Text(), nullable=False),
        sa.Column("size", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Plants table
    op.create_table(
        "plants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("areal_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("health", sa.Text(), nullable=False),
        sa.Column("image_path", sa.Text(), nullable=False),
        sa.Column("size", sa.Text(), nullable=False),
        sa.Column("position", sa.Text(), nullable=False),
        sa.Column("growth_stage", sa.Integer(), server_default=sa.text("1")),
        sa.Column("last_watered", sa.Date(), nullable=True),
        sa.Column("days_without_water", sa.Integer(), server_default=sa.text("0")),
        sa.Column("water_streak", sa.Integer(), server_default=sa.text("0")),
        sa.Column("total_water_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column(
            "created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["areal_id"], ["areals.id"], ondelete="CASCADE"),
    )

    # Watering history table
    op.create_table(
        "watering_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("watering_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("plant_id", "watering_date"),
    )

    # Daily watering limits table
    op.create_table(
        "daily_watering_config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("max_plants_per_day", sa.Integer(), server_default=sa.text("6")),
        sa.Column(
            "updated_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Insert default config
    op.execute(
        "INSERT OR IGNORE INTO daily_watering_config (id, max_plants_per_day) VALUES (1, 6)"
    )

    # Create indexes
    op.create_index("idx_plants_areal_id", "plants", ["areal_id"])
    op.create_index("idx_plants_health", "plants", ["health"])
    op.create_index("idx_plants_last_watered", "plants", ["last_watered"])
    op.create_index("idx_areals_position", "areals", ["horizontal_pos", "vertical_pos"])
    op.create_index("idx_watering_history_date", "watering_history", ["watering_date"])
    op.create_index("idx_watering_history_plant", "watering_history", ["plant_id"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_watering_history_plant")
    op.drop_index("idx_watering_history_date")
    op.drop_index("idx_areals_position")
    op.drop_index("idx_plants_last_watered")
    op.drop_index("idx_plants_health")
    op.drop_index("idx_plants_areal_id")

    # Drop tables
    op.drop_table("daily_watering_config")
    op.drop_table("watering_history")
    op.drop_table("plants")
    op.drop_table("areals")
