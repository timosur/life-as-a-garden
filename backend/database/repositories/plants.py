"""Repository for managing plants in the garden database."""

import sqlite3
from typing import List, Dict, Any, Optional
from ..base import DatabaseConnection


class PlantRepository:
    """Repository for plant-related database operations."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize with database connection."""
        self.db = db_connection

    def insert_plant(
        self, areal_id: str, plant_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Insert a plant into the database and return the created plant."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO plants 
                    (areal_id, name, health, image_path, size, position, 
                     days_without_water, water_streak, total_water_count, growth_stage, last_watered)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        areal_id,
                        plant_data["name"],
                        plant_data["health"],
                        plant_data.get("image_path", ""),
                        plant_data["size"],
                        plant_data["position"],
                        plant_data.get("days_without_water", 0),
                        plant_data.get("water_streak", 1),
                        plant_data.get("total_water_count", 20),
                        plant_data.get("growth_stage", 5),
                        plant_data.get("last_watered", None),
                    ),
                )

                # Get the created plant ID
                plant_id = cursor.lastrowid

                # Fetch and return the created plant
                cursor = conn.execute("SELECT * FROM plants WHERE id = ?", (plant_id,))
                result = cursor.fetchone()
                return dict(result) if result else None

        except sqlite3.Error as e:
            print(f"Error inserting plant: {e}")
            return None

    def get_plants_by_areal(self, areal_id: str) -> List[Dict[str, Any]]:
        """Get all plants for a specific areal."""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM plants WHERE areal_id = ? ORDER BY name", (areal_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_all_plants(self) -> List[Dict[str, Any]]:
        """Get all plants with their complete information."""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """SELECT p.*, a.name as areal_name 
                   FROM plants p 
                   JOIN areals a ON p.areal_id = a.id 
                   ORDER BY p.name"""
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_plants_by_health(self, health: str) -> List[Dict[str, Any]]:
        """Get all plants with a specific health status."""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """SELECT p.*, a.name as areal_name 
                   FROM plants p 
                   JOIN areals a ON p.areal_id = a.id 
                   WHERE p.health = ? 
                   ORDER BY p.name""",
                (health,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_plants_needing_water(self) -> List[Dict[str, Any]]:
        """Get plants that need water (sorted by priority)."""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """SELECT p.*, a.name as areal_name 
                   FROM plants p 
                   JOIN areals a ON p.areal_id = a.id 
                   WHERE p.health IN ('okay', 'dead') OR p.days_without_water >= 3
                   ORDER BY p.health = 'dead' DESC, p.days_without_water DESC, p.water_streak ASC""",
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_plant_by_name(self, plant_name: str) -> Dict[str, Any] | None:
        """Get a plant by name."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM plants WHERE name = ?", (plant_name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_plant_by_id(self, plant_id: int) -> Dict[str, Any] | None:
        """Get a plant by ID."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM plants WHERE id = ?", (plant_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_plant_health(self, plant_id: int, health: str) -> bool:
        """Update the health status of a plant."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE plants SET health = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (health, plant_id),
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating plant health: {e}")
            return False

    def update_plant(self, plant_id: int, plant_data: dict) -> bool:
        """Update plant information with provided fields."""
        try:
            # Build dynamic update query based on provided fields
            update_fields = []
            values = []

            # Define allowed fields mapping
            field_mapping = {
                "areal_id": "areal_id",
                "name": "name",
                "health": "health",
                "image_path": "image_path",
                "size": "size",
                "position": "position",
                "days_without_water": "days_without_water",
                "water_streak": "water_streak",
                "total_water_count": "total_water_count",
                "growth_stage": "growth_stage",
                "last_watered": "last_watered",
            }

            for field, value in plant_data.items():
                if value is not None and field in field_mapping:
                    update_fields.append(f"{field_mapping[field]} = ?")
                    values.append(value)

            if not update_fields:
                return False

            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE plants SET {', '.join(update_fields)} WHERE id = ?"
            values.append(plant_id)

            with self.db.get_connection() as conn:
                cursor = conn.execute(query, values)
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating plant: {e}")
            return False

    def update_plant_watering_stats(
        self,
        plant_id: int,
        last_watered: str,
        days_without_water: int,
        water_streak: int,
        total_water_count: int,
        growth_stage: int,
        health: str,
        size: str,
    ) -> bool:
        """Update plant watering statistics and status."""
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    """UPDATE plants SET 
                       last_watered = ?, 
                       days_without_water = ?, 
                       water_streak = ?, 
                       total_water_count = ?,
                       growth_stage = ?,
                       health = ?,
                       size = ?,
                       updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (
                        last_watered,
                        days_without_water,
                        water_streak,
                        total_water_count,
                        growth_stage,
                        health,
                        size,
                        plant_id,
                    ),
                )
                return True
        except sqlite3.Error as e:
            print(f"Error updating plant watering stats: {e}")
            return False

    def update_non_watered_plants(self, current_date: str) -> bool:
        """
        Update plants that weren't watered today with simplified logic.

        NOTE: This method is deprecated. Use WateringService.update_daily_plant_status() instead
        for centralized business logic and status change tracking.
        """
        # This method is kept for backward compatibility but should be replaced
        # by the service layer method that includes status change tracking
        print(
            "WARNING: Using deprecated update_non_watered_plants. Use WateringService.update_daily_plant_status() instead."
        )

        try:
            with self.db.get_connection() as conn:
                # Get plants not watered today
                plants_not_watered = conn.execute(
                    """SELECT p.* FROM plants p 
                       WHERE p.id NOT IN (
                           SELECT wh.plant_id FROM watering_history wh 
                           WHERE wh.watering_date = ?
                       )""",
                    (current_date,),
                ).fetchall()

                for plant in plants_not_watered:
                    days_without_water = plant["days_without_water"] + 1
                    current_health = plant["health"]
                    current_size = plant["size"]

                    # Simplified health degradation logic
                    new_health = current_health
                    if current_health == "healthy":
                        # Healthy plants downgrade to okay after 6 days without water
                        if days_without_water >= 6:
                            new_health = "okay"
                    elif current_health == "okay":
                        # Okay plants become dead after 4 days without water
                        if days_without_water >= 4:
                            new_health = "dead"
                    # Dead plants stay dead

                    # Reset water streak after 3 days without water
                    new_streak = 0 if days_without_water >= 3 else plant["water_streak"]

                    # Simplified size reduction logic - only after extended periods
                    new_size = current_size
                    if current_size == "big" and days_without_water >= 8:
                        new_size = "medium"
                    elif current_size == "medium" and days_without_water >= 10:
                        new_size = "small"
                    # Small plants stay small

                    conn.execute(
                        """UPDATE plants SET 
                           days_without_water = ?, 
                           water_streak = ?,
                           health = ?,
                           size = ?,
                           updated_at = CURRENT_TIMESTAMP
                           WHERE id = ?""",
                        (
                            days_without_water,
                            new_streak,
                            new_health,
                            new_size,
                            plant["id"],
                        ),
                    )
                return True
        except sqlite3.Error as e:
            print(f"Error updating non-watered plants: {e}")
            return False

    def delete_plant(self, plant_id: int) -> bool:
        """Delete a plant from the database."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting plant: {e}")
            return False
