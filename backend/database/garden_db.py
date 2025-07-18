import sqlite3
from typing import List, Dict, Any
from pathlib import Path


class GardenDatabase:
    """Database handler for the garden application using SQLite."""

    def __init__(self, db_path: str = "garden.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with the schema."""
        # Get the schema file path
        schema_path = Path(__file__).parent / "schema.sql"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Enable column access by name

            # Read and execute schema
            if schema_path.exists():
                with open(schema_path, "r") as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
            else:
                # Fallback schema if file doesn't exist
                self._create_tables_fallback(conn)

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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (areal_id) REFERENCES areals (id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_plants_areal_id ON plants(areal_id);
            CREATE INDEX IF NOT EXISTS idx_plants_health ON plants(health);
            CREATE INDEX IF NOT EXISTS idx_areals_position ON areals(horizontal_pos, vertical_pos);
        """)

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def insert_areal(self, areal_data: Dict[str, Any]) -> bool:
        """Insert an areal into the database."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO areals 
                    (id, name, horizontal_pos, vertical_pos, size)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        areal_data["id"],
                        areal_data["name"],
                        areal_data["horizontalPos"],
                        areal_data["verticalPos"],
                        areal_data["size"],
                    ),
                )
                return True
        except sqlite3.Error as e:
            print(f"Error inserting areal: {e}")
            return False

    def insert_plant(self, areal_id: str, plant_data: Dict[str, Any]) -> bool:
        """Insert a plant into the database."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO plants 
                    (areal_id, name, health, image_path, size, position)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        areal_id,
                        plant_data["name"],
                        plant_data["health"],
                        plant_data["imagePath"],
                        plant_data["size"],
                        plant_data["position"],
                    ),
                )
                return True
        except sqlite3.Error as e:
            print(f"Error inserting plant: {e}")
            return False

    def get_all_areals(self) -> List[Dict[str, Any]]:
        """Get all areals from the database."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM areals ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def get_plants_by_areal(self, areal_id: str) -> List[Dict[str, Any]]:
        """Get all plants for a specific areal."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM plants WHERE areal_id = ? ORDER BY name", (areal_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_garden_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the complete garden data in the original format."""
        areals = []

        for areal in self.get_all_areals():
            plants = self.get_plants_by_areal(areal["id"])

            # Convert database format back to original format
            areal_data = {
                "id": areal["id"],
                "name": areal["name"],
                "horizontalPos": areal["horizontal_pos"],
                "verticalPos": areal["vertical_pos"],
                "size": areal["size"],
                "plants": [],
            }

            for plant in plants:
                plant_data = {
                    "name": plant["name"],
                    "health": plant["health"],
                    "imagePath": plant["image_path"],
                    "size": plant["size"],
                    "position": plant["position"],
                }
                areal_data["plants"].append(plant_data)

            areals.append(areal_data)

        return {"areals": areals}

    def update_plant_health(self, plant_id: int, health: str) -> bool:
        """Update the health status of a plant."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE plants SET health = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (health, plant_id),
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating plant health: {e}")
            return False

    def delete_plant(self, plant_id: int) -> bool:
        """Delete a plant from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting plant: {e}")
            return False

    def delete_areal(self, areal_id: str) -> bool:
        """Delete an areal and all its plants from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("DELETE FROM areals WHERE id = ?", (areal_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting areal: {e}")
            return False

    def get_plants_by_health(self, health: str) -> List[Dict[str, Any]]:
        """Get all plants with a specific health status."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """SELECT p.*, a.name as areal_name 
                   FROM plants p 
                   JOIN areals a ON p.areal_id = a.id 
                   WHERE p.health = ? 
                   ORDER BY p.name""",
                (health,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_database_stats(self) -> Dict[str, int]:
        """Get basic statistics about the database."""
        with self.get_connection() as conn:
            areal_count = conn.execute("SELECT COUNT(*) FROM areals").fetchone()[0]
            plant_count = conn.execute("SELECT COUNT(*) FROM plants").fetchone()[0]
            healthy_plants = conn.execute(
                "SELECT COUNT(*) FROM plants WHERE health = 'healthy'"
            ).fetchone()[0]
            dead_plants = conn.execute(
                "SELECT COUNT(*) FROM plants WHERE health = 'dead'"
            ).fetchone()[0]

            return {
                "total_areals": areal_count,
                "total_plants": plant_count,
                "healthy_plants": healthy_plants,
                "dead_plants": dead_plants,
            }
