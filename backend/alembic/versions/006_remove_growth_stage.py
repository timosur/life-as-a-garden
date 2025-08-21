"""Remove growth_stage from plants and plant_status_changes tables

Revision ID: 006
Revises: 005
Create Date: 2025-08-21 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove growth_stage column from plants table
    with op.batch_alter_table("plants") as batch_op:
        batch_op.drop_column("growth_stage")

    # Remove old_growth_stage and new_growth_stage columns from plant_status_changes table
    with op.batch_alter_table("plant_status_changes") as batch_op:
        batch_op.drop_column("old_growth_stage")
        batch_op.drop_column("new_growth_stage")


def downgrade() -> None:
    # Add back growth_stage column to plants table
    with op.batch_alter_table("plants") as batch_op:
        batch_op.add_column(
            sa.Column("growth_stage", sa.Integer(), server_default=sa.text("1"))
        )

    # Add back old_growth_stage and new_growth_stage columns to plant_status_changes table
    with op.batch_alter_table("plant_status_changes") as batch_op:
        batch_op.add_column(sa.Column("old_growth_stage", sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column("new_growth_stage", sa.Integer(), nullable=False))
