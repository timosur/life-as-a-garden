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
            # Use the new centralized method with status change tracking
            self.update_daily_plant_status(watering_date)

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
            self.update_daily_plant_status(watering_date)

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

    def get_last_watering_details(self) -> Dict[str, Any]:
        """Get detailed information about the last watering session."""
        return self.watering_repo.get_last_watering_details()

    def get_todays_plant_status_changes(self) -> List[Dict[str, Any]]:
        """Get plant status changes for today only."""
        return self.watering_repo.get_todays_plant_status_changes()

    def _calculate_plant_status_after_watering(
        self, plant: Dict[str, Any], watering_date: str
    ) -> Dict[str, Any]:
        """
        Calculate new plant status after watering with simplified logic.

        Simplified Recovery Logic:
        - Dead plants: Need 3 consecutive days to become "okay", 5 days to become "healthy"
        - Okay plants: Need 3 consecutive days to become "healthy"
        - Healthy plants: Stay healthy with any watering
        - Growth is based on total water count and consistency
        - Size growth: Every 20 waterings increases size (small->medium->big)
        - Plants never decrease in size
        """
        # Store old state for change tracking
        old_state = {
            "health": plant["health"],
            "size": plant["size"],
            "water_streak": plant["water_streak"],
            "total_water_count": plant["total_water_count"],
            "days_without_water": plant["days_without_water"],
        }

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
                # If more than 5 days gap, reset streak
                if days_gap > 5:
                    new_streak = 1
                else:
                    # If within 5 days, keep the streak
                    new_streak = plant["water_streak"]
        else:
            # First time watering
            new_streak = 1

        # Update total water count
        new_total_count = plant["total_water_count"] + 1

        # Simplified health recovery logic
        current_health = plant["health"]

        if current_health == "dead":
            # Dead plants need consistent watering to recover
            if new_streak >= 5:
                new_health = "healthy"
            elif new_streak >= 3:
                new_health = "okay"
            else:
                new_health = "dead"  # Still dead, needs more consistency
        elif current_health == "okay":
            # Okay plants can improve to healthy fairly quickly
            if new_streak >= 3:
                new_health = "healthy"
            else:
                new_health = "okay"  # Stay okay
        else:  # healthy
            # Healthy plants stay healthy with any watering
            new_health = "healthy"

        # Size calculation based on total water count (every 20 waterings = next size)
        # Plants never decrease in size
        current_size = plant["size"]
        if new_total_count >= 40:
            new_size = "big"
        elif new_total_count >= 20:
            new_size = "medium"
        else:
            new_size = "small"

        # Ensure size never decreases
        size_hierarchy = {"small": 1, "medium": 2, "big": 3}
        if size_hierarchy.get(current_size, 1) > size_hierarchy.get(new_size, 1):
            new_size = current_size

        # Create new state for change tracking
        new_state = {
            "health": new_health,
            "size": new_size,
            "water_streak": new_streak,
            "total_water_count": new_total_count,
            "days_without_water": 0,
        }

        # Record status change if there's any difference
        if self._has_state_changed(old_state, new_state):
            self.watering_repo.record_plant_status_change(
                plant["id"], watering_date, "watered", old_state, new_state
            )

        # Update the plant in database
        self.plant_repo.update_plant_watering_stats(
            plant["id"],
            watering_date,
            0,  # days_without_water reset to 0
            new_streak,
            new_total_count,
            new_health,
            new_size,
        )

        return {
            "health": new_health,
            "size": new_size,
            "water_streak": new_streak,
            "total_water_count": new_total_count,
            "days_without_water": 0,
        }

    def update_daily_plant_status(self, current_date: str = None) -> Dict[str, Any]:
        """
        Update status of all plants for daily maintenance (plants not watered today).
        This method centralizes the plant status calculation logic.
        IMPORTANT: This method ensures it only runs once per day using a dedicated tracking table.
        """
        if current_date is None:
            current_date = date.today().strftime("%Y-%m-%d")

        try:
            # Safety check: Ensure this method only runs once per day
            if self.watering_repo.is_daily_update_completed(current_date):
                existing_info = self.watering_repo.get_daily_update_info(current_date)
                return {
                    "success": False,
                    "message": f"Daily plant status update already completed for {current_date}",
                    "already_processed": True,
                    "completed_at": existing_info["completed_at"]
                    if existing_info
                    else None,
                    "plants_processed": existing_info["plants_processed"]
                    if existing_info
                    else 0,
                    "plants_updated": existing_info["plants_updated"]
                    if existing_info
                    else 0,
                    "updated_plants": [],
                }

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

                updated_plants = []
                plants_with_changes = 0

                for plant in plants_not_watered:
                    # Store old state
                    old_state = {
                        "health": plant["health"],
                        "size": plant["size"],
                        "water_streak": plant["water_streak"],
                        "total_water_count": plant["total_water_count"],
                        "days_without_water": plant["days_without_water"],
                    }

                    # Calculate new state using centralized logic
                    new_state = self._calculate_plant_status_without_watering(
                        dict(plant)
                    )

                    # Record status change if there's any difference
                    has_changes = self._has_state_changed(old_state, new_state)
                    if has_changes:
                        self.watering_repo.record_plant_status_change(
                            plant["id"],
                            current_date,
                            "daily_update",
                            old_state,
                            new_state,
                        )
                        plants_with_changes += 1

                    # Update plant in database
                    self.plant_repo.update_plant_watering_stats(
                        plant["id"],
                        plant["last_watered"],  # Keep existing last_watered date
                        new_state["days_without_water"],
                        new_state["water_streak"],
                        new_state["total_water_count"],
                        new_state["health"],
                        new_state["size"],
                    )

                    updated_plants.append(
                        {
                            "id": plant["id"],
                            "name": plant["name"],
                            "old_state": old_state,
                            "new_state": new_state,
                            "has_changes": has_changes,
                        }
                    )

                # Record that daily update has been completed
                self.watering_repo.record_daily_update_completion(
                    current_date, len(plants_not_watered), plants_with_changes
                )

                return {
                    "success": True,
                    "message": f"Daily update completed for {current_date}",
                    "date_processed": current_date,
                    "plants_processed": len(plants_not_watered),
                    "plants_with_changes": plants_with_changes,
                    "updated_plants": updated_plants,
                }

        except Exception as e:
            print(f"Error updating daily plant status: {e}")
            return {"success": False, "error": str(e)}

    def is_daily_update_needed(self, current_date: str = None) -> bool:
        """
        Check if daily update is needed for the given date.

        Returns:
            bool: True if daily update is needed, False if already completed
        """
        if current_date is None:
            current_date = date.today().strftime("%Y-%m-%d")

        return not self.watering_repo.is_daily_update_completed(current_date)

    def _calculate_plant_status_without_watering(
        self, plant: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate new plant status when not watered (centralized logic).

        Simplified Watering Timeline:
        - Healthy plants: Stay healthy for 5 days, become "okay" after 6 days
        - Okay plants: Become "dead" after 4 days without water
        - Dead plants: Stay dead
        - Water streak: Reset after 3 days without water
        - Size: Never decreases, only grows based on total water count
        """
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

        # Size never decreases - plants only grow based on total water count
        new_size = current_size  # Keep current size (no reduction)

        return {
            "health": new_health,
            "water_streak": new_streak,
            "total_water_count": plant[
                "total_water_count"
            ],  # Total count doesn't decrease
            "days_without_water": days_without_water,
            "size": new_size,
        }

    def _has_state_changed(
        self, old_state: Dict[str, Any], new_state: Dict[str, Any]
    ) -> bool:
        """Check if any relevant plant state has changed."""
        return (
            old_state["health"] != new_state["health"]
            or old_state["size"] != new_state["size"]
            or old_state["water_streak"] != new_state["water_streak"]
            or old_state["days_without_water"] != new_state["days_without_water"]
            or old_state["total_water_count"] != new_state["total_water_count"]
        )
