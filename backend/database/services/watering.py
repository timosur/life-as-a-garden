"""Service layer for garden watering logic and plant status calculations."""

from datetime import datetime, date
from typing import List, Dict, Any
from ..repositories import PlantRepository, WateringRepository


class WateringService:
    """Service for handling watering operations and plant status calculations."""

    def __init__(self):
        """Initialize with repositories."""
        self.plant_repo = PlantRepository()
        self.watering_repo = WateringRepository()

    def water_plants(
        self, checked_plant_names: List[str], watering_date: str = None
    ) -> Dict[str, Any]:
        """Water the checked plants and update their status."""
        if watering_date is None:
            watering_date = date.today().strftime("%Y-%m-%d")

        try:
            max_plants = self.watering_repo.get_daily_watering_limit()
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

            plants_to_water = checked_plant_names[:remaining_capacity]
            updated_plants = []

            for plant_name in plants_to_water:
                plant = self.plant_repo.get_plant_by_name(plant_name)
                if not plant:
                    continue

                watering_added = self.watering_repo.add_watering_record(
                    plant["id"], watering_date
                )
                if watering_added:
                    new_stats = self._calculate_plant_status_after_watering(
                        plant, watering_date
                    )
                    updated_plants.append(
                        {"plant_id": plant["id"], "name": plant_name, **new_stats}
                    )

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
        """Water a single plant by name or ID."""
        if watering_date is None:
            watering_date = date.today().strftime("%Y-%m-%d")

        try:
            max_plants = self.watering_repo.get_daily_watering_limit()
            plants_watered_today = self.watering_repo.get_plants_watered_today_count(
                watering_date
            )

            if plants_watered_today >= max_plants:
                return {
                    "success": False,
                    "message": f"Daily watering limit ({max_plants}) already reached",
                    "plants_watered_today": plants_watered_today,
                }

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

            if self.watering_repo.is_plant_watered_today(plant_id, watering_date):
                return {
                    "success": False,
                    "message": f"Plant '{plant_name}' has already been watered today",
                }

            watering_added = self.watering_repo.add_watering_record(
                plant_id, watering_date
            )
            if not watering_added:
                return {
                    "success": False,
                    "message": f"Failed to record watering for '{plant_name}'",
                }

            new_stats = self._calculate_plant_status_after_watering(
                plant, watering_date
            )
            self.update_daily_plant_status(watering_date)

            return {
                "success": True,
                "message": f"Successfully watered '{plant_name}'",
                "plant": {"id": plant_id, "name": plant_name, **new_stats},
                "plants_watered_today": plants_watered_today + 1,
                "daily_limit": max_plants,
            }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def get_last_watering_details(self) -> Dict[str, Any]:
        return self.watering_repo.get_last_watering_details()

    def get_todays_plant_status_changes(self) -> List[Dict[str, Any]]:
        return self.watering_repo.get_todays_plant_status_changes()

    def _calculate_plant_status_after_watering(
        self, plant: Dict[str, Any], watering_date: str
    ) -> Dict[str, Any]:
        """Calculate new plant status after watering."""
        old_state = {
            "health": plant["health"],
            "size": plant["size"],
            "water_streak": plant["water_streak"],
            "total_water_count": plant["total_water_count"],
            "days_without_water": plant["days_without_water"],
        }

        last_watered = plant["last_watered"]
        current_date = datetime.strptime(watering_date, "%Y-%m-%d").date()

        if last_watered:
            if isinstance(last_watered, str):
                last_watered_date = datetime.strptime(last_watered, "%Y-%m-%d").date()
            else:
                last_watered_date = last_watered
            days_gap = (current_date - last_watered_date).days

            if days_gap == 1:
                new_streak = plant["water_streak"] + 1
            elif days_gap > 5:
                new_streak = 1
            else:
                new_streak = plant["water_streak"]
        else:
            new_streak = 1

        new_total_count = plant["total_water_count"] + 1
        current_health = plant["health"]

        if current_health == "dead":
            if new_streak >= 5:
                new_health = "healthy"
            elif new_streak >= 3:
                new_health = "okay"
            else:
                new_health = "dead"
        elif current_health == "okay":
            new_health = "healthy" if new_streak >= 3 else "okay"
        else:
            new_health = "healthy"

        current_size = plant["size"]
        if new_total_count >= 40:
            new_size = "big"
        elif new_total_count >= 20:
            new_size = "medium"
        else:
            new_size = "small"

        size_hierarchy = {"small": 1, "medium": 2, "big": 3}
        if size_hierarchy.get(current_size, 1) > size_hierarchy.get(new_size, 1):
            new_size = current_size

        new_state = {
            "health": new_health,
            "size": new_size,
            "water_streak": new_streak,
            "total_water_count": new_total_count,
            "days_without_water": 0,
        }

        if self._has_state_changed(old_state, new_state):
            self.watering_repo.record_plant_status_change(
                plant["id"], watering_date, "watered", old_state, new_state
            )

        self.plant_repo.update_plant_watering_stats(
            plant["id"],
            watering_date,
            0,
            new_streak,
            new_total_count,
            new_health,
            new_size,
        )

        return new_state

    def update_daily_plant_status(self, current_date: str = None) -> Dict[str, Any]:
        """Update status of all plants for daily maintenance (plants not watered today)."""
        if current_date is None:
            current_date = date.today().strftime("%Y-%m-%d")

        try:
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

            plants_not_watered = self.watering_repo.get_plants_not_watered(current_date)
            updated_plants = []
            plants_with_changes = 0

            for plant in plants_not_watered:
                old_state = {
                    "health": plant["health"],
                    "size": plant["size"],
                    "water_streak": plant["water_streak"],
                    "total_water_count": plant["total_water_count"],
                    "days_without_water": plant["days_without_water"],
                }

                new_state = self._calculate_plant_status_without_watering(plant)
                has_changes = self._has_state_changed(old_state, new_state)

                if has_changes:
                    self.watering_repo.record_plant_status_change(
                        plant["id"], current_date, "daily_update", old_state, new_state
                    )
                    plants_with_changes += 1

                self.plant_repo.update_plant_watering_stats(
                    plant["id"],
                    str(plant["last_watered"]) if plant["last_watered"] else None,
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
        if current_date is None:
            current_date = date.today().strftime("%Y-%m-%d")
        return not self.watering_repo.is_daily_update_completed(current_date)

    def _calculate_plant_status_without_watering(
        self, plant: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate new plant status when not watered."""
        days_without_water = plant["days_without_water"] + 1
        current_health = plant["health"]
        current_size = plant["size"]

        new_health = current_health
        if current_health == "healthy" and days_without_water >= 7:
            new_health = "okay"
        elif current_health == "okay" and days_without_water >= 14:
            new_health = "dead"

        new_streak = 0 if days_without_water >= 3 else plant["water_streak"]

        return {
            "health": new_health,
            "water_streak": new_streak,
            "total_water_count": plant["total_water_count"],
            "days_without_water": days_without_water,
            "size": current_size,
        }

    def _has_state_changed(
        self, old_state: Dict[str, Any], new_state: Dict[str, Any]
    ) -> bool:
        return (
            old_state["health"] != new_state["health"]
            or old_state["size"] != new_state["size"]
            or old_state["water_streak"] != new_state["water_streak"]
            or old_state["days_without_water"] != new_state["days_without_water"]
            or old_state["total_water_count"] != new_state["total_water_count"]
        )
