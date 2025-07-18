"""Main garden service for handling garden data operations."""

from typing import List, Dict, Any
from ..base import DatabaseConnection
from ..repositories import ArealRepository, PlantRepository, WateringRepository
from .watering import WateringService


class GardenService:
    """Main service for garden data operations."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize with database connection and repositories."""
        self.db = db_connection
        self.areal_repo = ArealRepository(db_connection)
        self.plant_repo = PlantRepository(db_connection)
        self.watering_repo = WateringRepository(db_connection)
        self.watering_service = WateringService(db_connection)

    def get_garden_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the complete garden data in the original format."""
        areals = []

        for areal in self.areal_repo.get_all_areals():
            plants = self.plant_repo.get_plants_by_areal(areal["id"])

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

    def get_database_stats(self) -> Dict[str, int]:
        """Get basic statistics about the database."""
        with self.db.get_connection() as conn:
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

    def insert_areal(self, areal_data: Dict[str, Any]) -> bool:
        """Insert an areal into the database."""
        return self.areal_repo.insert_areal(areal_data)

    def insert_plant(self, areal_id: str, plant_data: Dict[str, Any]) -> bool:
        """Insert a plant into the database."""
        return self.plant_repo.insert_plant(areal_id, plant_data)

    def get_all_areals(self) -> List[Dict[str, Any]]:
        """Get all areals from the database."""
        return self.areal_repo.get_all_areals()

    def get_plants_by_areal(self, areal_id: str) -> List[Dict[str, Any]]:
        """Get all plants for a specific areal."""
        return self.plant_repo.get_plants_by_areal(areal_id)

    def get_all_plants(self) -> List[Dict[str, Any]]:
        """Get all plants with their complete information."""
        return self.plant_repo.get_all_plants()

    def get_plants_by_health(self, health: str) -> List[Dict[str, Any]]:
        """Get all plants with a specific health status."""
        return self.plant_repo.get_plants_by_health(health)

    def get_plants_needing_water(self) -> List[Dict[str, Any]]:
        """Get plants that need water (sorted by priority)."""
        return self.plant_repo.get_plants_needing_water()

    def update_plant_health(self, plant_id: int, health: str) -> bool:
        """Update the health status of a plant."""
        return self.plant_repo.update_plant_health(plant_id, health)

    def delete_plant(self, plant_id: int) -> bool:
        """Delete a plant from the database."""
        return self.plant_repo.delete_plant(plant_id)

    def delete_areal(self, areal_id: str) -> bool:
        """Delete an areal and all its plants from the database."""
        return self.areal_repo.delete_areal(areal_id)

    def get_daily_watering_stats(self, date_str: str = None) -> Dict[str, Any]:
        """Get watering statistics for a specific day."""
        from datetime import date

        if date_str is None:
            date_str = date.today().strftime("%Y-%m-%d")

        return self.watering_repo.get_daily_watering_stats(date_str)

    def set_daily_watering_limit(self, new_limit: int) -> bool:
        """Update the daily watering limit."""
        return self.watering_repo.set_daily_watering_limit(new_limit)

    def water_plants(
        self, checked_plant_names: List[str], watering_date: str = None
    ) -> Dict[str, Any]:
        """Water the checked plants using the watering service."""
        return self.watering_service.water_plants(checked_plant_names, watering_date)

    def water_single_plant(
        self, plant_identifier: str, watering_date: str = None, by_id: bool = False
    ) -> Dict[str, Any]:
        """Water a single plant using the watering service."""
        return self.watering_service.water_single_plant(
            plant_identifier, watering_date, by_id
        )

    def migrate_daily_limit_to_4(self) -> bool:
        """Migrate existing database to set daily limit to 4 plants."""
        return self.watering_repo.migrate_daily_limit_to_4()
