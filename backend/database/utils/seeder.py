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
                    "id": "core-family",
                    "name": "Core Family",
                    "horizontalPos": "left",
                    "verticalPos": "bottom",
                    "size": "large",
                    "plants": [
                        {
                            "name": "Bobo",
                            "health": "healthy",
                            "image_path": "rose",
                            "size": "big",
                            "position": "top",
                        },
                        {
                            "name": "Finja",
                            "health": "healthy",
                            "image_path": "sunflower",
                            "size": "big",
                            "position": "left",
                        },
                        {
                            "name": "Mats",
                            "health": "healthy",
                            "image_path": "happy-bamboo",
                            "size": "big",
                            "position": "right",
                        },
                        {
                            "name": "Mama",
                            "health": "healthy",
                            "image_path": "lavendel",
                            "size": "medium",
                            "position": "center",
                        },
                        {
                            "name": "Papa",
                            "health": "okay",
                            "image_path": "cactus",
                            "size": "small",
                            "position": "bottom",
                        },
                    ],
                },
                {
                    "id": "sport",
                    "name": "Sport",
                    "horizontalPos": "right",
                    "verticalPos": "bottom",
                    "size": "large",
                    "plants": [
                        {
                            "name": "Fahrrad fahren",
                            "health": "healthy",
                            "image_path": "thymian",
                            "size": "big",
                            "position": "top",
                        },
                        {
                            "name": "Joggen",
                            "health": "okay",
                            "image_path": "oat-grass",
                            "size": "big",
                            "position": "center",
                        },
                        {
                            "name": "Klettern",
                            "health": "healthy",
                            "image_path": "hop",
                            "size": "big",
                            "position": "left",
                        },
                        {
                            "name": "Yoga",
                            "health": "healthy",
                            "image_path": "lotus-flower",
                            "size": "medium",
                            "position": "right",
                        },
                        {
                            "name": "Schwimmen",
                            "health": "okay",
                            "image_path": "water-hyacinth",
                            "size": "medium",
                            "position": "bottom-left",
                        },
                        {
                            "name": "Fußball",
                            "health": "dead",
                            "image_path": "grass",
                            "size": "small",
                            "position": "bottom-right",
                        },
                    ],
                },
                {
                    "id": "mental-health",
                    "name": "Mental Health",
                    "horizontalPos": "left",
                    "verticalPos": "middle",
                    "size": "large",
                    "plants": [
                        {
                            "name": "Meditation",
                            "health": "healthy",
                            "image_path": "bonsai",
                            "size": "big",
                            "position": "center",
                        },
                        {
                            "name": "Lesen",
                            "health": "healthy",
                            "image_path": "ivy",
                            "size": "medium",
                            "position": "left",
                        },
                        {
                            "name": "Journaling",
                            "health": "healthy",
                            "image_path": "sage",
                            "size": "medium",
                            "position": "right",
                        },
                        {
                            "name": "Waldbaden",
                            "health": "okay",
                            "image_path": "sequoia",
                            "size": "medium",
                            "position": "bottom",
                        },
                        {
                            "name": "Psychotherapie",
                            "health": "healthy",
                            "image_path": "aloe-vera",
                            "size": "big",
                            "position": "top",
                        },
                    ],
                },
                {
                    "id": "extended-family",
                    "name": "Extended Family",
                    "horizontalPos": "right",
                    "verticalPos": "top",
                    "size": "medium",
                    "plants": [
                        {
                            "name": "Oma",
                            "health": "dead",
                            "image_path": "snowdrop",
                            "size": "small",
                            "position": "left",
                        },
                        {
                            "name": "Frankes",
                            "health": "healthy",
                            "image_path": "marigold",
                            "size": "big",
                            "position": "center-top-mid",
                        },
                        {
                            "name": "Schwiegereltern",
                            "health": "healthy",
                            "image_path": "cucumber",
                            "size": "big",
                            "position": "bottom",
                        },
                    ],
                },
                {
                    "id": "hobbies",
                    "name": "Hobbies",
                    "horizontalPos": "right",
                    "verticalPos": "middle",
                    "size": "medium",
                    "plants": [
                        {
                            "name": "DJ",
                            "health": "okay",
                            "image_path": "red-maple",
                            "size": "big",
                            "position": "center",
                        },
                        {
                            "name": "Magic",
                            "health": "dead",
                            "image_path": "black-lotus",
                            "size": "small",
                            "position": "bottom",
                        },
                        {
                            "name": "Schach",
                            "health": "okay",
                            "image_path": "cypress",
                            "size": "medium",
                            "position": "left",
                        },
                    ],
                },
                {
                    "id": "work",
                    "name": "Work",
                    "horizontalPos": "left",
                    "verticalPos": "top",
                    "size": "small",
                    "plants": [
                        {
                            "name": "Spaß bei der Arbeit",
                            "health": "okay",
                            "image_path": "dandelion",
                            "size": "medium",
                            "position": "center",
                        },
                        {
                            "name": "Sinn in der Arbeit",
                            "health": "dead",
                            "image_path": "oak",
                            "size": "small",
                            "position": "bottom",
                        },
                    ],
                },
            ],
        }
