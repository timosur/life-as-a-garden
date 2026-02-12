"""Main garden service for handling garden operations."""

from typing import List, Dict, Any, Optional
from ..repositories import ArealRepository, PlantRepository, WateringRepository
from .watering import WateringService


class GardenService:
    """Main service for garden data operations."""

    def __init__(self):
        """Initialize with repositories."""
        self.areal_repo = ArealRepository()
        self.plant_repo = PlantRepository()
        self.watering_repo = WateringRepository()
        self.watering_service = WateringService()

    def get_garden_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the complete garden data in the original format."""
        areals = []
        for areal in self.areal_repo.get_all_areals():
            plants = self.plant_repo.get_plants_by_areal(areal["id"])
            areal_data = {
                "id": areal["id"],
                "name": areal["name"],
                "horizontalPos": areal["horizontal_pos"],
                "verticalPos": areal["vertical_pos"],
                "size": areal["size"],
                "plants": [
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "health": p["health"],
                        "imagePath": p["image_path"],
                        "size": p["size"],
                        "position": p["position"],
                        "last_watered": str(p["last_watered"])
                        if p["last_watered"]
                        else None,
                        "days_without_water": p["days_without_water"],
                        "water_streak": p["water_streak"],
                        "total_water_count": p["total_water_count"],
                    }
                    for p in plants
                ],
            }
            areals.append(areal_data)
        return {"areals": areals}

    def get_database_stats(self) -> Dict[str, int]:
        """Get basic statistics about the database."""
        from ..base import get_session
        from sqlmodel import select, func
        from ..models import Areal, Plant

        with get_session() as session:
            areal_count = session.exec(select(func.count()).select_from(Areal)).one()
            plant_count = session.exec(select(func.count()).select_from(Plant)).one()
            healthy = session.exec(
                select(func.count()).select_from(Plant).where(Plant.health == "healthy")
            ).one()
            dead = session.exec(
                select(func.count()).select_from(Plant).where(Plant.health == "dead")
            ).one()
            return {
                "total_areals": areal_count,
                "total_plants": plant_count,
                "healthy_plants": healthy,
                "dead_plants": dead,
            }

    def insert_areal(self, areal_data: Dict[str, Any]) -> bool:
        return self.areal_repo.insert_areal(areal_data)

    def insert_plant(
        self, areal_id: str, plant_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return self.plant_repo.insert_plant(areal_id, plant_data)

    def get_all_areals(self) -> List[Dict[str, Any]]:
        return self.areal_repo.get_all_areals()

    def get_plants_by_areal(self, areal_id: str) -> List[Dict[str, Any]]:
        return self.plant_repo.get_plants_by_areal(areal_id)

    def get_all_plants(self) -> List[Dict[str, Any]]:
        return self.plant_repo.get_all_plants()

    def get_plants_by_health(self, health: str) -> List[Dict[str, Any]]:
        return self.plant_repo.get_plants_by_health(health)

    def get_plants_needing_water(self) -> List[Dict[str, Any]]:
        return self.plant_repo.get_plants_needing_water()

    def update_plant_health(self, plant_id: int, health: str) -> bool:
        return self.plant_repo.update_plant_health(plant_id, health)

    def update_plant(self, plant_id: int, plant_data: dict) -> bool:
        return self.plant_repo.update_plant(plant_id, plant_data)

    def get_plant_by_id(self, plant_id: int) -> Optional[Dict[str, Any]]:
        return self.plant_repo.get_plant_by_id(plant_id)

    def get_areal_by_id(self, areal_id: str) -> Optional[Dict[str, Any]]:
        return self.areal_repo.get_areal_by_id(areal_id)

    def update_areal(self, areal_id: str, areal_data: dict) -> bool:
        return self.areal_repo.update_areal(areal_id, areal_data)

    def delete_plant(self, plant_id: int) -> bool:
        return self.plant_repo.delete_plant(plant_id)

    def delete_areal(self, areal_id: str) -> bool:
        return self.areal_repo.delete_areal(areal_id)

    def get_daily_watering_stats(self, date_str: str = None) -> Dict[str, Any]:
        from datetime import date

        if date_str is None:
            date_str = date.today().strftime("%Y-%m-%d")
        return self.watering_repo.get_daily_watering_stats(date_str)

    def set_daily_watering_limit(self, new_limit: int) -> bool:
        return self.watering_repo.set_daily_watering_limit(new_limit)

    def water_plants(
        self, checked_plant_names: List[str], watering_date: str = None
    ) -> Dict[str, Any]:
        return self.watering_service.water_plants(checked_plant_names, watering_date)

    def water_single_plant(
        self, plant_identifier: str, watering_date: str = None, by_id: bool = False
    ) -> Dict[str, Any]:
        return self.watering_service.water_single_plant(
            plant_identifier, watering_date, by_id
        )

    def get_last_watering_details(self) -> Dict[str, Any]:
        return self.watering_service.get_last_watering_details()

    def update_daily_plant_status(self, current_date: str = None) -> Dict[str, Any]:
        return self.watering_service.update_daily_plant_status(current_date)

    def get_plant_status_changes(
        self, plant_id: int = None, limit: int = None
    ) -> List[Dict[str, Any]]:
        return self.watering_repo.get_plant_status_changes(plant_id, limit)

    def get_todays_plant_status_changes(self) -> List[Dict[str, Any]]:
        return self.watering_service.get_todays_plant_status_changes()

    def get_watering_history_by_date_range(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        return self.watering_repo.get_watering_history_by_date_range(
            start_date, end_date
        )

    def migrate_daily_limit_to_4(self) -> bool:
        return self.watering_repo.migrate_daily_limit_to_4()
