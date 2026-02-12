"""Initial PostgreSQL schema

Revision ID: 001
Revises:
Create Date: 2026-02-12 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Areals table
    op.create_table(
        "areals",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("horizontal_pos", sa.String(), nullable=False),
        sa.Column("vertical_pos", sa.String(), nullable=False),
        sa.Column("size", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    # Plants table
    op.create_table(
        "plants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("areal_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("health", sa.String(), nullable=False),
        sa.Column("image_path", sa.String(), server_default=""),
        sa.Column("size", sa.String(), nullable=False),
        sa.Column("position", sa.String(), nullable=False),
        sa.Column("last_watered", sa.Date(), nullable=True),
        sa.Column("days_without_water", sa.Integer(), server_default=sa.text("0")),
        sa.Column("water_streak", sa.Integer(), server_default=sa.text("0")),
        sa.Column("total_water_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["areal_id"], ["areals.id"], ondelete="CASCADE"),
    )

    # Watering history table
    op.create_table(
        "watering_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("watering_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("plant_id", "watering_date", name="uq_watering_plant_date"),
    )

    # Daily watering config table
    op.create_table(
        "daily_watering_config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("max_plants_per_day", sa.Integer(), server_default=sa.text("5")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    # Plant status changes table
    op.create_table(
        "plant_status_changes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("change_date", sa.Date(), nullable=False),
        sa.Column("change_type", sa.String(), nullable=False),
        sa.Column("old_health", sa.String(), nullable=False),
        sa.Column("new_health", sa.String(), nullable=False),
        sa.Column("old_water_streak", sa.Integer(), nullable=False),
        sa.Column("new_water_streak", sa.Integer(), nullable=False),
        sa.Column("old_days_without_water", sa.Integer(), nullable=False),
        sa.Column("new_days_without_water", sa.Integer(), nullable=False),
        sa.Column("old_total_water_count", sa.Integer(), nullable=False),
        sa.Column("new_total_water_count", sa.Integer(), nullable=False),
        sa.Column("old_size", sa.String(), nullable=True),
        sa.Column("new_size", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"], ondelete="CASCADE"),
    )

    # Daily update tracker table
    op.create_table(
        "daily_update_tracker",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("update_date", sa.String(10), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=False),
        sa.Column(
            "plants_processed",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "plants_updated", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("update_date", name="unique_update_date"),
    )

    # Notes table
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("extracted_at", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("idx_plants_areal_id", "plants", ["areal_id"])
    op.create_index("idx_plants_health", "plants", ["health"])
    op.create_index("idx_plants_last_watered", "plants", ["last_watered"])
    op.create_index("idx_areals_position", "areals", ["horizontal_pos", "vertical_pos"])
    op.create_index("idx_watering_history_date", "watering_history", ["watering_date"])
    op.create_index("idx_watering_history_plant", "watering_history", ["plant_id"])
    op.create_index(
        "idx_plant_status_changes_plant", "plant_status_changes", ["plant_id"]
    )
    op.create_index(
        "idx_plant_status_changes_date", "plant_status_changes", ["change_date"]
    )
    op.create_index("idx_daily_update_date", "daily_update_tracker", ["update_date"])

    # Insert default config
    op.execute(
        "INSERT INTO daily_watering_config (id, max_plants_per_day) VALUES (1, 4) ON CONFLICT (id) DO NOTHING"
    )


def downgrade() -> None:
    op.drop_table("notes")
    op.drop_table("daily_update_tracker")
    op.drop_table("plant_status_changes")
    op.drop_table("daily_watering_config")
    op.drop_table("watering_history")
    op.drop_table("plants")
    op.drop_table("areals")
