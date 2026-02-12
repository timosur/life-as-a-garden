"""Data seeding utilities for initializing the garden database."""

from typing import Dict, Any
from ..repositories import ArealRepository, PlantRepository
from ..base import get_session
from ..models import Areal
from sqlmodel import select, func


class DataSeeder:
    """Utility class for seeding the database with initial garden data."""

    def __init__(self):
        self.areal_repo = ArealRepository()
        self.plant_repo = PlantRepository()

    def seed_initial_data(self) -> bool:
        """Seed the database with initial garden data if it's empty."""
        try:
            with get_session() as session:
                areal_count = session.exec(
                    select(func.count()).select_from(Areal)
                ).one()
                if areal_count > 0:
                    print("Database already contains data, skipping seeding.")
                    return True

            print("Seeding database with initial garden data...")
            garden_data = self._get_initial_garden_data()

            for areal_data in garden_data["areals"]:
                if not self.areal_repo.insert_areal(areal_data):
                    print(f"Failed to insert areal: {areal_data['name']}")
                    return False
                for plant_data in areal_data["plants"]:
                    if not self.plant_repo.insert_plant(areal_data["id"], plant_data):
                        print(f"Failed to insert plant: {plant_data['name']}")
                        return False

            # Seed default watering config
            from ..models import DailyWateringConfig

            with get_session() as session:
                config = session.get(DailyWateringConfig, 1)
                if not config:
                    session.add(DailyWateringConfig(id=1, max_plants_per_day=4))
                    session.commit()

            print("Database seeded successfully with initial garden data.")
            return True
        except Exception as e:
            print(f"Error seeding database: {e}")
            return False

    def _get_initial_garden_data(self) -> Dict[str, Any]:
        return {
            "areals": [
                {
                    "id": "default",
                    "name": "My Garden",
                    "horizontalPos": "left",
                    "verticalPos": "bottom",
                    "size": "medium",
                    "plants": [
                        {
                            "name": "Example Plant",
                            "health": "healthy",
                            "image_path": "rose",
                            "size": "medium",
                            "position": "center",
                        },
                    ],
                },
            ],
        }
