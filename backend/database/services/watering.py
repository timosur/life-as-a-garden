"""Service layer for garden watering logic and plant status calculations."""

from datetime import datetime, date
from typing import List, Dict, Any
from ..base import DatabaseConnection
from ..repositories import ArealRepository, PlantRepository, WateringRepository


class WateringService:
    """Service for handling watering operations and plant status calculations."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize with database connection and repositories."""
        self.db = db_connection
        self.areal_repo = ArealRepository(db_connection)
        self.plant_repo = PlantRepository(db_connection)
        self.watering_repo = WateringRepository(db_connection)

    def water_plants(
        self, checked_plant_names: List[str], watering_date: str = None
    ) -> Dict[str, Any]:
        """
        Water the checked plants and update their status based on watering algorithm.

        Args:
            checked_plant_names: List of plant names that were checked (watered)
            watering_date: Date in YYYY-MM-DD format (defaults to today)

        Returns:
            Dict with operation results and updated plant statuses
        """
        if watering_date is None:
            watering_date = date.today().strftime("%Y-%m-%d")

        try:
            # Get daily watering limit
            max_plants = self.watering_repo.get_daily_watering_limit()

            # Count plants already watered today
            plants_watered_today = self.watering_repo.get_plants_watered_today_count(
                watering_date
            )

            remaining_capacity = max_plants - plants_watered_today

            if remaining_capacity <= 0:
                return {
                    "success": False,
                    "message": f"Daily watering limit ({max_plants}) already reached",
                    "plants_watered_today": plants_watered_today,
                    "updated_plants": [],
                }

            # Limit checked plants to remaining capacity
            plants_to_water = checked_plant_names[:remaining_capacity]

            updated_plants = []
            for plant_name in plants_to_water:
                # Get plant info
                plant = self.plant_repo.get_plant_by_name(plant_name)

                if not plant:
                    continue

                plant_id = plant["id"]

                # Record watering event
                watering_added = self.watering_repo.add_watering_record(
                    plant_id, watering_date
                )

                if watering_added:
                    # Update plant watering stats and calculate new status
                    new_stats = self._calculate_plant_status_after_watering(
                        plant, watering_date
                    )
                    updated_plants.append(
                        {"plant_id": plant_id, "name": plant_name, **new_stats}
                    )

            # Update plants that weren't watered (increase days_without_water)
            self.plant_repo.update_non_watered_plants(watering_date)

            return {
                "success": True,
                "message": f"Watered {len(updated_plants)} plants",
                "daily_limit": max_plants,
                "plants_watered_today": plants_watered_today + len(updated_plants),
                "updated_plants": updated_plants,
            }

        except Exception as e:
            print(f"Error watering plants: {e}")
            return {"success": False, "error": str(e)}

    def water_single_plant(
        self, plant_identifier: str, watering_date: str = None, by_id: bool = False
    ) -> Dict[str, Any]:
        """
        Water a single plant by name or ID.

        Args:
            plant_identifier: Plant name or ID
            watering_date: Date in YYYY-MM-DD format (defaults to today)
            by_id: If True, plant_identifier is treated as plant ID, otherwise as plant name

        Returns:
            Dict with operation results and updated plant status
        """
        if watering_date is None:
            watering_date = date.today().strftime("%Y-%m-%d")

        try:
            # Get daily watering limit
            max_plants = self.watering_repo.get_daily_watering_limit()

            # Count plants already watered today
            plants_watered_today = self.watering_repo.get_plants_watered_today_count(
                watering_date
            )

            if plants_watered_today >= max_plants:
                return {
                    "success": False,
                    "message": f"Daily watering limit ({max_plants}) already reached",
                    "plants_watered_today": plants_watered_today,
                }

            # Find the plant
            if by_id:
                plant = self.plant_repo.get_plant_by_id(int(plant_identifier))
            else:
                plant = self.plant_repo.get_plant_by_name(plant_identifier)

            if not plant:
                return {
                    "success": False,
                    "message": f"Plant {'ID' if by_id else 'name'} '{plant_identifier}' not found",
                }

            plant_id = plant["id"]
            plant_name = plant["name"]

            # Check if plant is already watered today
            if self.watering_repo.is_plant_watered_today(plant_id, watering_date):
                return {
                    "success": False,
                    "message": f"Plant '{plant_name}' has already been watered today",
                }

            # Record watering event
            watering_added = self.watering_repo.add_watering_record(
                plant_id, watering_date
            )

            if not watering_added:
                return {
                    "success": False,
                    "message": f"Failed to record watering for '{plant_name}'",
                }

            # Update plant watering stats and calculate new status
            new_stats = self._calculate_plant_status_after_watering(
                plant, watering_date
            )

            # Update plants that weren't watered (increase days_without_water)
            self.plant_repo.update_non_watered_plants(watering_date)

            return {
                "success": True,
                "message": f"Successfully watered '{plant_name}'",
                "plant": {
                    "id": plant_id,
                    "name": plant_name,
                    **new_stats,
                },
                "plants_watered_today": plants_watered_today + 1,
                "daily_limit": max_plants,
            }

        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def _calculate_plant_status_after_watering(
        self, plant: Dict[str, Any], watering_date: str
    ) -> Dict[str, Any]:
        """Calculate new plant status after watering with improved health and size logic."""
        # Calculate new water streak
        last_watered = plant["last_watered"]
        current_date = datetime.strptime(watering_date, "%Y-%m-%d").date()

        if last_watered:
            last_watered_date = datetime.strptime(last_watered, "%Y-%m-%d").date()
            days_gap = (current_date - last_watered_date).days

            if days_gap == 1:
                # Consecutive day - increase streak
                new_streak = plant["water_streak"] + 1
            else:
                # Gap in watering - reset streak but don't penalize too much
                new_streak = 1
        else:
            # First time watering
            new_streak = 1

        # Update total water count
        new_total_count = plant["total_water_count"] + 1

        # Calculate health based on watering consistency and current health
        current_health = plant["health"]

        if current_health == "dead":
            # Dead plants can recover but need consistent watering
            if new_streak >= 5:
                new_health = "okay"
            elif new_streak >= 3:
                new_health = "dead"  # Still dead but improving
            else:
                new_health = "dead"
        elif current_health == "okay":
            # Okay plants can improve to healthy or decline
            if new_streak >= 7:
                new_health = "healthy"
            elif new_streak >= 3:
                new_health = "okay"
            else:
                new_health = "okay"  # Stay okay for now
        else:  # healthy or other states
            # Healthy plants maintain health with regular watering
            if new_streak >= 5:
                new_health = "healthy"
            elif new_streak >= 2:
                new_health = "healthy"
            elif new_total_count >= 3:
                new_health = "okay"
            else:
                new_health = "okay"

        # Calculate growth stage (1-5 based on total water count and streak)
        # More emphasis on consistency (streak) for growth
        growth_from_streak = min(3, new_streak // 2)  # Max 3 from streak
        growth_from_total = min(2, new_total_count // 5)  # Max 2 from total count
        new_growth_stage = min(5, max(1, growth_from_streak + growth_from_total + 1))

        # Calculate size based on growth stage and health
        if new_health == "dead":
            # Dead plants shrink regardless of growth stage
            new_size = "small"
        elif new_health == "okay":
            # Okay plants can be small to medium
            if new_growth_stage >= 4:
                new_size = "medium"
            else:
                new_size = "small"
        else:  # healthy
            # Healthy plants can reach full size potential
            if new_growth_stage >= 4:
                new_size = "big"
            elif new_growth_stage >= 3:
                new_size = "medium"
            else:
                new_size = "small"

        # Update the plant in database
        self.plant_repo.update_plant_watering_stats(
            plant["id"],
            watering_date,
            0,  # days_without_water reset to 0
            new_streak,
            new_total_count,
            new_growth_stage,
            new_health,
            new_size,
        )

        return {
            "health": new_health,
            "size": new_size,
            "growth_stage": new_growth_stage,
            "water_streak": new_streak,
            "total_water_count": new_total_count,
            "days_without_water": 0,
        }
