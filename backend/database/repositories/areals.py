"""Repository for managing areals in the garden database."""

import sqlite3
from typing import List, Dict, Any
from ..base import DatabaseConnection


class ArealRepository:
    """Repository for areal-related database operations."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize with database connection."""
        self.db = db_connection

    def insert_areal(self, areal_data: Dict[str, Any]) -> bool:
        """Insert an areal into the database."""
        try:
            with self.db.get_connection() as conn:
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

    def get_all_areals(self) -> List[Dict[str, Any]]:
        """Get all areals from the database."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM areals ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def delete_areal(self, areal_id: str) -> bool:
        """Delete an areal and all its plants from the database."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute("DELETE FROM areals WHERE id = ?", (areal_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting areal: {e}")
            return False

    def get_areal_by_id(self, areal_id: str) -> Dict[str, Any] | None:
        """Get a specific areal by ID."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM areals WHERE id = ?", (areal_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
