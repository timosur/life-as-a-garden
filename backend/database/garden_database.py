"""
Refactored Garden Database - Main entry point that maintains backward compatibility.

This is the new main database class that uses the refactored modular structure
while maintaining the same interface as the original GardenDatabase class.
"""

from typing import List, Dict, Any
from .base import DatabaseConnection
from .services import GardenService
from .utils import DataSeeder


class GardenDatabase:
    """
    Main database handler for the garden application.

    This class maintains backward compatibility with the original interface
    while using the new modular structure internally.
    """

    def __init__(self, db_path: str = "garden.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.db_connection = DatabaseConnection(db_path)
        self.garden_service = GardenService(self.db_connection)
        self.data_seeder = DataSeeder(self.db_connection)
        self.init_database()

    def init_database(self):
        """Initialize the database with the schema and seed initial data."""
        self.db_connection.init_database()
        # Seed initial data if database is empty
        self.data_seeder.seed_initial_data()

    def get_connection(self):
        """Get a database connection with row factory enabled."""
        return self.db_connection.get_connection()

    # Areal methods
    def insert_areal(self, areal_data: Dict[str, Any]) -> bool:
        """Insert an areal into the database."""
        return self.garden_service.insert_areal(areal_data)

    def get_all_areals(self) -> List[Dict[str, Any]]:
        """Get all areals from the database."""
        return self.garden_service.get_all_areals()

    def delete_areal(self, areal_id: str) -> bool:
        """Delete an areal and all its plants from the database."""
        return self.garden_service.delete_areal(areal_id)

    # Plant methods
    def insert_plant(self, areal_id: str, plant_data: Dict[str, Any]) -> bool:
        """Insert a plant into the database."""
        return self.garden_service.insert_plant(areal_id, plant_data)

    def get_plants_by_areal(self, areal_id: str) -> List[Dict[str, Any]]:
        """Get all plants for a specific areal."""
        return self.garden_service.get_plants_by_areal(areal_id)

    def get_all_plants(self) -> List[Dict[str, Any]]:
        """Get all plants with their complete information."""
        return self.garden_service.get_all_plants()

    def get_plants_by_health(self, health: str) -> List[Dict[str, Any]]:
        """Get all plants with a specific health status."""
        return self.garden_service.get_plants_by_health(health)

    def get_plants_needing_water(self) -> List[Dict[str, Any]]:
        """Get plants that need water (sorted by priority)."""
        return self.garden_service.get_plants_needing_water()

    def update_plant_health(self, plant_id: int, health: str) -> bool:
        """Update the health status of a plant."""
        return self.garden_service.update_plant_health(plant_id, health)

    def delete_plant(self, plant_id: int) -> bool:
        """Delete a plant from the database."""
        return self.garden_service.delete_plant(plant_id)

    # Garden data methods
    def get_garden_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the complete garden data in the original format."""
        return self.garden_service.get_garden_data()

    def get_database_stats(self) -> Dict[str, int]:
        """Get basic statistics about the database."""
        return self.garden_service.get_database_stats()

    # Watering methods
    def water_plants(
        self, checked_plant_names: List[str], watering_date: str = None
    ) -> Dict[str, Any]:
        """Water the checked plants and update their status."""
        return self.garden_service.water_plants(checked_plant_names, watering_date)

    def water_single_plant(
        self, plant_identifier: str, watering_date: str = None, by_id: bool = False
    ) -> Dict[str, Any]:
        """Water a single plant by name or ID."""
        return self.garden_service.water_single_plant(
            plant_identifier, watering_date, by_id
        )

    def get_daily_watering_stats(self, date_str: str = None) -> Dict[str, Any]:
        """Get watering statistics for a specific day."""
        return self.garden_service.get_daily_watering_stats(date_str)

    def set_daily_watering_limit(self, new_limit: int) -> bool:
        """Update the daily watering limit."""
        return self.garden_service.set_daily_watering_limit(new_limit)

    def migrate_daily_limit_to_4(self) -> bool:
        """Migrate existing database to set daily limit to 4 plants."""
        return self.garden_service.migrate_daily_limit_to_4()

    # Seed data method
    def seed_initial_data(self) -> bool:
        """Seed the database with initial garden data if it's empty."""
        return self.data_seeder.seed_initial_data()
