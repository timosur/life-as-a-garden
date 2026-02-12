#!/usr/bin/env python3
"""Database migration utilities using Alembic with PostgreSQL."""

import sys
from pathlib import Path
from alembic.config import Config
from alembic import command
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from settings import settings


class DatabaseMigrator:
    """Handle database migrations using Alembic."""

    def __init__(self):
        """Initialize migrator with database URL from settings."""
        self.db_url = settings.database_url

        # Get the backend directory (where alembic.ini is located)
        self.backend_dir = Path(__file__).parent.parent
        self.alembic_cfg_path = self.backend_dir / "alembic.ini"

        # Create alembic config
        self.alembic_cfg = Config(str(self.alembic_cfg_path))
        self.alembic_cfg.set_main_option("sqlalchemy.url", self.db_url)

    def get_current_revision(self) -> str:
        """Get the current database revision."""
        try:
            engine = create_engine(self.db_url)
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception:
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


def run_migrations_on_startup() -> bool:
    """Run database migrations on application startup."""
    migrator = DatabaseMigrator()
    return migrator.run_migrations()


if __name__ == "__main__":
    success = run_migrations_on_startup()
    sys.exit(0 if success else 1)
