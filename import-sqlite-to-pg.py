#!/usr/bin/env python3
"""Import data from a SQLite garden.db backup into the local PostgreSQL database.

Usage:
    docker compose exec backend python3 /app/import-sqlite-to-pg.py /path/to/garden.db

Or run locally (with DATABASE_URL set or .env configured):
    python3 import-sqlite-to-pg.py backup_tmp/backup-20260212-010003/garden.db
"""

import sqlite3
import sys
import os

# Add backend to path so we can reuse settings/models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from sqlmodel import Session, create_engine, SQLModel, text
from settings import settings
from database.models import (
    Areal,
    Plant,
    WateringHistory,
    DailyWateringConfig,
    PlantStatusChange,
    DailyUpdateTracker,
    Note,
)


# Table import order (respecting foreign keys)
TABLES = [
    ("areals", Areal),
    ("daily_watering_config", DailyWateringConfig),
    ("daily_update_tracker", DailyUpdateTracker),
    ("notes", Note),
    ("plants", Plant),
    ("watering_history", WateringHistory),
    ("plant_status_changes", PlantStatusChange),
]


def get_valid_ids(sqlite_conn: sqlite3.Connection) -> tuple[set, set]:
    """Get valid areal IDs and plant IDs (plants whose areal exists)."""
    areal_ids = {
        row[0] for row in sqlite_conn.execute("SELECT id FROM areals").fetchall()
    }
    plant_ids = {
        row[0]
        for row in sqlite_conn.execute("SELECT id, areal_id FROM plants").fetchall()
        if row[1] in areal_ids  # only plants with valid areals
    }
    return areal_ids, plant_ids


# Tables with FK that needs validation
FK_PLANT_TABLES = {"watering_history", "plant_status_changes"}
FK_AREAL_TABLES = {"plants"}


def import_table(
    pg_session: Session,
    sqlite_conn: sqlite3.Connection,
    table_name: str,
    model_class,
    valid_plant_ids: set,
    valid_areal_ids: set,
):
    """Import all rows from a SQLite table into PostgreSQL."""
    cursor = sqlite_conn.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    if not rows:
        print(f"  {table_name}: 0 rows (empty)")
        return 0

    skipped = 0
    with pg_session.no_autoflush:
        for row in rows:
            row_dict = dict(zip(columns, row))

            # Skip orphaned rows referencing deleted plants
            if (
                table_name in FK_PLANT_TABLES
                and row_dict.get("plant_id") not in valid_plant_ids
            ):
                skipped += 1
                continue

            # Skip plants referencing deleted areals
            if (
                table_name in FK_AREAL_TABLES
                and row_dict.get("areal_id") not in valid_areal_ids
            ):
                skipped += 1
                continue

            # Remove any columns not in the model (e.g. alembic internals)
            valid_fields = set(model_class.model_fields.keys())
            row_dict = {k: v for k, v in row_dict.items() if k in valid_fields}
            obj = model_class(**row_dict)
            pg_session.merge(obj)

    pg_session.flush()
    msg = f"  {table_name}: {len(rows) - skipped} rows imported"
    if skipped:
        msg += f" ({skipped} orphaned rows skipped)"
    print(msg)
    return len(rows) - skipped


def reset_sequences(pg_session: Session):
    """Reset PostgreSQL sequences for auto-increment columns after import."""
    sequence_tables = [
        ("plants", "id"),
        ("watering_history", "id"),
        ("daily_watering_config", "id"),
        ("plant_status_changes", "id"),
        ("daily_update_tracker", "id"),
        ("notes", "id"),
    ]
    for table, col in sequence_tables:
        pg_session.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table}', '{col}'), COALESCE(MAX({col}), 1)) FROM {table}"
            )
        )
    print("  Sequences reset.")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path-to-garden.db>")
        sys.exit(1)

    sqlite_path = sys.argv[1]
    if not os.path.exists(sqlite_path):
        print(f"Error: SQLite file not found: {sqlite_path}")
        sys.exit(1)

    print(f"SQLite source: {sqlite_path}")
    print(f"PostgreSQL target: {settings.database_url}")
    print()

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = None

    # Connect to PostgreSQL
    pg_engine = create_engine(settings.database_url, echo=False)
    SQLModel.metadata.create_all(pg_engine)

    total = 0
    valid_areal_ids, valid_plant_ids = get_valid_ids(sqlite_conn)

    with Session(pg_engine) as session:
        # Wipe existing data (reverse FK order)
        print("Clearing existing data:")
        for table_name, _ in reversed(TABLES):
            session.execute(text(f"DELETE FROM {table_name}"))
            print(f"  {table_name}: cleared")
        session.flush()
        print()

        print("Importing tables:")
        for table_name, model_class in TABLES:
            count = import_table(
                session,
                sqlite_conn,
                table_name,
                model_class,
                valid_plant_ids,
                valid_areal_ids,
            )
            total += count

        print()
        print("Resetting sequences:")
        reset_sequences(session)

        session.commit()

    sqlite_conn.close()
    print()
    print(f"Done! Imported {total} rows total.")


if __name__ == "__main__":
    main()
