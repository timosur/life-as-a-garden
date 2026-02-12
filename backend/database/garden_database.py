"""
Refactored Garden Database - Main entry point using SQLModel + PostgreSQL.

Maintains the same interface as before while using SQLModel ORM internally.
"""

from typing import List, Dict, Any, Optional
from datetime import date
from .services import GardenService, NotesService
from .utils import DataSeeder
from .migrate import run_migrations_on_startup


class GardenDatabase:
    """
    Main database handler for the garden application.

    Maintains backward compatibility with the original interface.
    """

    def __init__(self):
        """Initialize database services and run migrations."""
        self.garden_service = GardenService()
        self.notes_service = NotesService()
        self.data_seeder = DataSeeder()
        self.init_database()

    def init_database(self):
        """Initialize the database with migrations and seed initial data."""
        migration_success = run_migrations_on_startup()
        if not migration_success:
            raise RuntimeError("Failed to run database migrations")
        self.data_seeder.seed_initial_data()

    # Areal methods
    def insert_areal(self, areal_data: Dict[str, Any]) -> bool:
        return self.garden_service.insert_areal(areal_data)

    def get_all_areals(self) -> List[Dict[str, Any]]:
        return self.garden_service.get_all_areals()

    def delete_areal(self, areal_id: str) -> bool:
        return self.garden_service.delete_areal(areal_id)

    # Plant methods
    def insert_plant(
        self, areal_id: str, plant_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return self.garden_service.insert_plant(areal_id, plant_data)

    def get_plants_by_areal(self, areal_id: str) -> List[Dict[str, Any]]:
        return self.garden_service.get_plants_by_areal(areal_id)

    def get_all_plants(self) -> List[Dict[str, Any]]:
        return self.garden_service.get_all_plants()

    def get_plants_by_health(self, health: str) -> List[Dict[str, Any]]:
        return self.garden_service.get_plants_by_health(health)

    def get_plants_needing_water(self) -> List[Dict[str, Any]]:
        return self.garden_service.get_plants_needing_water()

    def update_plant_health(self, plant_id: int, health: str) -> bool:
        return self.garden_service.update_plant_health(plant_id, health)

    def update_plant(self, plant_id: int, plant_data: dict) -> bool:
        return self.garden_service.update_plant(plant_id, plant_data)

    def get_plant_by_id(self, plant_id: int) -> Optional[Dict[str, Any]]:
        return self.garden_service.get_plant_by_id(plant_id)

    def get_areal_by_id(self, areal_id: str) -> Optional[Dict[str, Any]]:
        return self.garden_service.get_areal_by_id(areal_id)

    def update_areal(self, areal_id: str, areal_data: dict) -> bool:
        return self.garden_service.update_areal(areal_id, areal_data)

    def delete_plant(self, plant_id: int) -> bool:
        return self.garden_service.delete_plant(plant_id)

    # Garden data methods
    def get_garden_data(self) -> Dict[str, List[Dict[str, Any]]]:
        return self.garden_service.get_garden_data()

    def get_database_stats(self) -> Dict[str, int]:
        return self.garden_service.get_database_stats()

    # Watering methods
    def water_plants(
        self, checked_plant_names: List[str], watering_date: str = None
    ) -> Dict[str, Any]:
        return self.garden_service.water_plants(checked_plant_names, watering_date)

    def water_single_plant(
        self, plant_identifier: str, watering_date: str = None, by_id: bool = False
    ) -> Dict[str, Any]:
        return self.garden_service.water_single_plant(
            plant_identifier, watering_date, by_id
        )

    def get_daily_watering_stats(self, date_str: str = None) -> Dict[str, Any]:
        return self.garden_service.get_daily_watering_stats(date_str)

    def set_daily_watering_limit(self, new_limit: int) -> bool:
        return self.garden_service.set_daily_watering_limit(new_limit)

    def get_last_watering_details(self) -> Dict[str, Any]:
        return self.garden_service.get_last_watering_details()

    def update_daily_plant_status(self, current_date: str = None) -> Dict[str, Any]:
        return self.garden_service.update_daily_plant_status(current_date)

    def get_plant_status_changes(
        self, plant_id: int = None, limit: int = None
    ) -> List[Dict[str, Any]]:
        return self.garden_service.get_plant_status_changes(plant_id, limit)

    def get_todays_plant_status_changes(self) -> List[Dict[str, Any]]:
        return self.garden_service.get_todays_plant_status_changes()

    def get_watering_history_by_date_range(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        return self.garden_service.get_watering_history_by_date_range(
            start_date, end_date
        )

    def migrate_daily_limit_to_4(self) -> bool:
        return self.garden_service.migrate_daily_limit_to_4()

    def seed_initial_data(self) -> bool:
        return self.data_seeder.seed_initial_data()

    # Notes methods
    def create_note(self, content: str, extracted_at: date) -> int:
        return self.notes_service.create_note(content, extracted_at)

    def get_notes_by_date(self, date_filter: date) -> List[Dict[str, Any]]:
        return self.notes_service.get_notes_by_date(date_filter)

    def get_all_notes(self) -> List[Dict[str, Any]]:
        return self.notes_service.get_all_notes()

    def get_note_by_id(self, note_id: int) -> Optional[Dict[str, Any]]:
        return self.notes_service.get_note_by_id(note_id)

    def get_notes_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        return self.notes_service.get_notes_by_date_range(start_date, end_date)

    def update_note(self, note_id: int, content: str) -> bool:
        return self.notes_service.update_note(note_id, content)

    def delete_note(self, note_id: int) -> bool:
        return self.notes_service.delete_note(note_id)

    def note_exists_for_date(self, date_filter: date) -> bool:
        return self.notes_service.note_exists_for_date(date_filter)
