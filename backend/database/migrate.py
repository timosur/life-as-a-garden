#!/usr/bin/env python3
"""Database migration utilities using Alembic."""

import os
import sys
from pathlib import Path
from alembic.config import Config
from alembic import command
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text


class DatabaseMigrator:
    """Handle database migrations using Alembic."""

    def __init__(self, db_path: str = "db/garden.db"):
        """Initialize migrator with database path."""
        self.db_path = db_path
        self.db_url = f"sqlite:///{db_path}"

        # Get the backend directory (where alembic.ini is located)
        self.backend_dir = Path(__file__).parent.parent
        self.alembic_cfg_path = self.backend_dir / "alembic.ini"

        # Create alembic config
        self.alembic_cfg = Config(str(self.alembic_cfg_path))
        self.alembic_cfg.set_main_option("sqlalchemy.url", self.db_url)

        # Ensure db directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def get_current_revision(self) -> str:
        """Get the current database revision."""
        try:
            engine = create_engine(self.db_url)
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception:
            # Database might not exist or not have alembic_version table
            return None

    def get_head_revision(self) -> str:
        """Get the latest available revision."""
        script = ScriptDirectory.from_config(self.alembic_cfg)
        return script.get_current_head()

    def needs_migration(self) -> bool:
        """Check if database needs migration."""
        current = self.get_current_revision()
        head = self.get_head_revision()
        return current != head

    def run_migrations(self) -> bool:
        """Run all pending migrations."""
        try:
            print("🔄 Checking for database migrations...")

            if not self.needs_migration():
                current = self.get_current_revision()
                print(f"✅ Database is up to date (revision: {current or 'initial'})")
                return True

            current = self.get_current_revision()
            head = self.get_head_revision()
            print(f"🔄 Running migrations from {current or 'initial'} to {head}...")

            # Run migrations
            command.upgrade(self.alembic_cfg, "head")

            print("✅ Database migrations completed successfully")
            return True

        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            return False

    def stamp_head(self) -> bool:
        """Stamp the database with the current head revision without running migrations."""
        try:
            command.stamp(self.alembic_cfg, "head")
            print("✅ Database stamped with head revision")
            return True
        except Exception as e:
            print(f"❌ Failed to stamp database: {str(e)}")
            return False


def run_migrations_on_startup(db_path: str = "db/garden.db") -> bool:
    """
    Run database migrations on application startup.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        bool: True if migrations were successful, False otherwise
    """
    migrator = DatabaseMigrator(db_path)
    return migrator.run_migrations()


if __name__ == "__main__":
    # For running migrations manually
    db_path = sys.argv[1] if len(sys.argv) > 1 else "db/garden.db"
    success = run_migrations_on_startup(db_path)
    sys.exit(0 if success else 1)
