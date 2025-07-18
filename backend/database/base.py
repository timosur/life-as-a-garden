"""Base database connection and initialization module."""

import sqlite3
from pathlib import Path


class DatabaseConnection:
    """Base database connection handler."""

    def __init__(self, db_path: str = "garden.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self._shared_connection = None

        # For in-memory databases, we need to keep the connection alive
        if db_path == ":memory:":
            self._shared_connection = self._create_connection()

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory enabled."""
        if self._shared_connection:
            return self._shared_connection
        return self._create_connection()

    def init_database(self):
        """Initialize the database with the schema."""
        schema_path = Path(__file__).parent / "schema.sql"

        conn = self.get_connection()
        if schema_path.exists():
            with open(schema_path, "r") as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
        else:
            self._create_tables_fallback(conn)

        # Don't close the connection for in-memory databases
        if not self._shared_connection:
            conn.close()

    def _create_tables_fallback(self, conn: sqlite3.Connection):
        """Fallback method to create tables if schema.sql is not found."""
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS areals (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                horizontal_pos TEXT NOT NULL,
                vertical_pos TEXT NOT NULL,
                size TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS plants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                areal_id TEXT NOT NULL,
                name TEXT NOT NULL,
                health TEXT NOT NULL,
                image_path TEXT NOT NULL,
                size TEXT NOT NULL,
                position TEXT NOT NULL,
                growth_stage INTEGER DEFAULT 1,
                last_watered DATE NULL,
                days_without_water INTEGER DEFAULT 0,
                water_streak INTEGER DEFAULT 0,
                total_water_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (areal_id) REFERENCES areals (id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS watering_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER NOT NULL,
                watering_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plant_id) REFERENCES plants (id) ON DELETE CASCADE,
                UNIQUE(plant_id, watering_date)
            );
            
            CREATE TABLE IF NOT EXISTS daily_watering_config (
                id INTEGER PRIMARY KEY,
                max_plants_per_day INTEGER DEFAULT 5,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            INSERT OR IGNORE INTO daily_watering_config (id, max_plants_per_day) VALUES (1, 4);
            
            CREATE INDEX IF NOT EXISTS idx_plants_areal_id ON plants(areal_id);
            CREATE INDEX IF NOT EXISTS idx_plants_health ON plants(health);
            CREATE INDEX IF NOT EXISTS idx_plants_last_watered ON plants(last_watered);
            CREATE INDEX IF NOT EXISTS idx_areals_position ON areals(horizontal_pos, vertical_pos);
            CREATE INDEX IF NOT EXISTS idx_watering_history_date ON watering_history(watering_date);
            CREATE INDEX IF NOT EXISTS idx_watering_history_plant ON watering_history(plant_id);
        """)
