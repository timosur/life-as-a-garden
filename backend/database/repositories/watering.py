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

    def get_last_watering_details(self) -> Dict[str, Any]:
        """Get detailed information about the last watering session."""
        with self.db.get_connection() as conn:
            # Get the most recent watering date
            latest_date_result = conn.execute(
                "SELECT watering_date FROM watering_history ORDER BY watering_date DESC LIMIT 1"
            ).fetchone()

            if not latest_date_result:
                return {"success": False, "message": "No watering history found"}

            latest_date = latest_date_result[0]

            # Get all plants watered on the latest date with their status changes
            watered_plants_query = """
                SELECT 
                    p.id,
                    p.name,
                    p.health,
                    p.size,
                    p.growth_stage,
                    p.last_watered,
                    p.days_without_water,
                    p.water_streak,
                    p.total_water_count,
                    a.name as areal_name,
                    wh.watering_date,
                    wh.created_at as watering_time,
                    psc.old_health,
                    psc.new_health,
                    psc.old_growth_stage,
                    psc.new_growth_stage,
                    psc.old_water_streak,
                    psc.new_water_streak,
                    psc.old_days_without_water,
                    psc.new_days_without_water,
                    psc.old_total_water_count,
                    psc.new_total_water_count,
                    psc.old_size,
                    psc.new_size
                FROM plants p
                JOIN watering_history wh ON p.id = wh.plant_id
                JOIN areals a ON p.areal_id = a.id
                LEFT JOIN plant_status_changes psc ON p.id = psc.plant_id 
                    AND psc.change_date = wh.watering_date 
                    AND psc.change_type = 'watered'
                WHERE wh.watering_date = ?
                ORDER BY wh.created_at ASC
            """

            watered_plants = conn.execute(
                watered_plants_query, (latest_date,)
            ).fetchall()

            # Get daily stats for that date
            daily_stats = self.get_daily_watering_stats(latest_date)

            # Format plant details with actual before/after data
            plant_details = []
            for plant_row in watered_plants:
                plant = dict(plant_row)

                # If we have status change data, use it; otherwise use current state
                if plant["old_health"] is not None:
                    before_state = {
                        "health": plant["old_health"],
                        "size": plant["old_size"],
                        "growth_stage": plant["old_growth_stage"],
                        "water_streak": plant["old_water_streak"],
                        "total_water_count": plant["old_total_water_count"],
                        "days_without_water": plant["old_days_without_water"],
                    }

                    after_state = {
                        "health": plant["new_health"],
                        "size": plant["new_size"],
                        "growth_stage": plant["new_growth_stage"],
                        "water_streak": plant["new_water_streak"],
                        "total_water_count": plant["new_total_water_count"],
                        "days_without_water": plant["new_days_without_water"],
                    }
                else:
                    # Fallback if no status change recorded
                    after_state = {
                        "health": plant["health"],
                        "size": plant["size"],
                        "growth_stage": plant["growth_stage"],
                        "water_streak": plant["water_streak"],
                        "total_water_count": plant["total_water_count"],
                        "days_without_water": plant["days_without_water"],
                    }
                    before_state = after_state.copy()  # No change data available

                # Calculate changes
                changes = {
                    "health_changed": before_state["health"] != after_state["health"],
                    "size_changed": before_state["size"] != after_state["size"],
                    "growth_increased": after_state["growth_stage"]
                    > before_state["growth_stage"],
                    "water_streak_increased": after_state["water_streak"]
                    > before_state["water_streak"],
                    "days_without_water_reset": after_state["days_without_water"] == 0
                    and before_state["days_without_water"] > 0,
                }

                plant_details.append(
                    {
                        "id": plant["id"],
                        "name": plant["name"],
                        "areal_name": plant["areal_name"],
                        "watering_time": plant["watering_time"],
                        "before": before_state,
                        "after": after_state,
                        "changes": changes,
                    }
                )

            return {
                "success": True,
                "watering_date": latest_date,
                "daily_stats": daily_stats,
                "plants_watered": len(plant_details),
                "plant_details": plant_details,
            }

    def record_plant_status_change(
        self,
        plant_id: int,
        change_date: str,
        change_type: str,
        old_state: Dict[str, Any],
        new_state: Dict[str, Any],
    ) -> bool:
        """Record a plant status change in the database."""
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    """INSERT INTO plant_status_changes 
                       (plant_id, change_date, change_type, old_health, new_health, 
                        old_growth_stage, new_growth_stage, old_water_streak, new_water_streak,
                        old_days_without_water, new_days_without_water, 
                        old_total_water_count, new_total_water_count, old_size, new_size)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        plant_id,
                        change_date,
                        change_type,
                        old_state["health"],
                        new_state["health"],
                        old_state["growth_stage"],
                        new_state["growth_stage"],
                        old_state["water_streak"],
                        new_state["water_streak"],
                        old_state["days_without_water"],
                        new_state["days_without_water"],
                        old_state["total_water_count"],
                        new_state["total_water_count"],
                        old_state["size"],
                        new_state["size"],
                    ),
                )
                return True
        except sqlite3.Error as e:
            print(f"Error recording status change: {e}")
            return False

    def get_plant_status_changes(
        self, plant_id: int = None, limit: int = None
    ) -> List[Dict[str, Any]]:
        """Get plant status changes, optionally filtered by plant_id and limited."""
        with self.db.get_connection() as conn:
            if plant_id:
                query = """SELECT psc.*, p.name as plant_name 
                          FROM plant_status_changes psc 
                          JOIN plants p ON psc.plant_id = p.id 
                          WHERE psc.plant_id = ? 
                          ORDER BY psc.change_date DESC, psc.created_at DESC"""
                params = (plant_id,)
            else:
                query = """SELECT psc.*, p.name as plant_name 
                          FROM plant_status_changes psc 
                          JOIN plants p ON psc.plant_id = p.id 
                          ORDER BY psc.change_date DESC, psc.created_at DESC"""
                params = ()

            if limit:
                query += f" LIMIT {limit}"

            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_todays_plant_status_changes(self) -> List[Dict[str, Any]]:
        """Get plant status changes for today only."""
        with self.db.get_connection() as conn:
            query = """SELECT psc.*, p.name as plant_name 
                      FROM plant_status_changes psc 
                      JOIN plants p ON psc.plant_id = p.id 
                      WHERE psc.change_date = date('now')
                      ORDER BY psc.created_at DESC"""

            cursor = conn.execute(query)
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

    def is_daily_update_completed(self, date_str: str) -> bool:
        """Check if daily update has been completed for a specific date."""
        with self.db.get_connection() as conn:
            result = conn.execute(
                "SELECT COUNT(*) FROM daily_update_tracker WHERE update_date = ?",
                (date_str,),
            ).fetchone()[0]
            return result > 0

    def record_daily_update_completion(
        self, date_str: str, plants_processed: int, plants_updated: int
    ) -> bool:
        """Record that daily update has been completed for a specific date."""
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    """INSERT INTO daily_update_tracker 
                       (update_date, completed_at, plants_processed, plants_updated) 
                       VALUES (?, CURRENT_TIMESTAMP, ?, ?)""",
                    (date_str, plants_processed, plants_updated),
                )
                return True
        except sqlite3.Error as e:
            print(f"Error recording daily update completion: {e}")
            return False

    def get_daily_update_info(self, date_str: str) -> Dict[str, Any]:
        """Get information about a daily update for a specific date."""
        with self.db.get_connection() as conn:
            row = conn.execute(
                """SELECT update_date, completed_at, plants_processed, plants_updated 
                   FROM daily_update_tracker WHERE update_date = ?""",
                (date_str,),
            ).fetchone()

            if row:
                return dict(row)
            return None
