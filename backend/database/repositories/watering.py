"""Repository for managing watering history and configuration in the garden database."""

import sqlite3
from typing import List, Dict, Any
from ..base import DatabaseConnection


class WateringRepository:
    """Repository for watering-related database operations."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize with database connection."""
        self.db = db_connection

    def get_daily_watering_limit(self) -> int:
        """Get the current daily watering limit."""
        with self.db.get_connection() as conn:
            return conn.execute(
                "SELECT max_plants_per_day FROM daily_watering_config WHERE id = 1"
            ).fetchone()[0]

    def set_daily_watering_limit(self, new_limit: int) -> bool:
        """Update the daily watering limit."""
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    "UPDATE daily_watering_config SET max_plants_per_day = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
                    (new_limit,),
                )
                return True
        except sqlite3.Error as e:
            print(f"Error updating watering limit: {e}")
            return False

    def get_plants_watered_today_count(self, date_str: str) -> int:
        """Get count of plants watered on a specific date."""
        with self.db.get_connection() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM watering_history WHERE watering_date = ?",
                (date_str,),
            ).fetchone()[0]

    def add_watering_record(self, plant_id: int, watering_date: str) -> bool:
        """Add a watering record for a plant."""
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO watering_history (plant_id, watering_date) VALUES (?, ?)",
                    (plant_id, watering_date),
                )
                return True
        except sqlite3.IntegrityError:
            # Plant already watered today
            return False
        except sqlite3.Error as e:
            print(f"Error adding watering record: {e}")
            return False

    def is_plant_watered_today(self, plant_id: int, date_str: str) -> bool:
        """Check if a plant has been watered today."""
        with self.db.get_connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM watering_history WHERE plant_id = ? AND watering_date = ?",
                (plant_id, date_str),
            ).fetchone()[0]
            return count > 0

    def get_daily_watering_stats(self, date_str: str) -> Dict[str, Any]:
        """Get watering statistics for a specific day."""
        with self.db.get_connection() as conn:
            # Get daily limit
            max_plants = self.get_daily_watering_limit()

            # Count plants watered today
            watered_today = self.get_plants_watered_today_count(date_str)

            # Get list of plants watered today
            watered_plants = conn.execute(
                """SELECT p.name, p.health, p.size, p.growth_stage 
                   FROM plants p 
                   JOIN watering_history wh ON p.id = wh.plant_id 
                   WHERE wh.watering_date = ?""",
                (date_str,),
            ).fetchall()

            return {
                "date": date_str,
                "daily_limit": max_plants,
                "plants_watered": watered_today,
                "remaining_capacity": max_plants - watered_today,
                "watered_plants": [dict(row) for row in watered_plants],
            }

    def get_watering_history(
        self, plant_id: int = None, limit: int = None
    ) -> List[Dict[str, Any]]:
        """Get watering history, optionally filtered by plant_id and limited."""
        with self.db.get_connection() as conn:
            if plant_id:
                query = """SELECT wh.*, p.name as plant_name 
                          FROM watering_history wh 
                          JOIN plants p ON wh.plant_id = p.id 
                          WHERE wh.plant_id = ? 
                          ORDER BY wh.watering_date DESC"""
                params = (plant_id,)
            else:
                query = """SELECT wh.*, p.name as plant_name 
                          FROM watering_history wh 
                          JOIN plants p ON wh.plant_id = p.id 
                          ORDER BY wh.watering_date DESC"""
                params = ()

            if limit:
                query += f" LIMIT {limit}"

            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def migrate_daily_limit_to_4(self) -> bool:
        """Migrate existing database to set daily limit to 4 plants."""
        try:
            with self.db.get_connection() as conn:
                # Update existing config to limit of 4
                conn.execute(
                    "UPDATE daily_watering_config SET max_plants_per_day = 4, updated_at = CURRENT_TIMESTAMP WHERE id = 1"
                )
                return True
        except sqlite3.Error as e:
            print(f"Error migrating daily limit: {e}")
            return False
