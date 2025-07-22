"""Data seeding utilities for initializing the garden database."""

import sqlite3
from typing import Dict, Any
from ..base import DatabaseConnection
from ..repositories import ArealRepository, PlantRepository


class DataSeeder:
    """Utility class for seeding the database with initial garden data."""

    def __init__(self, db_connection: DatabaseConnection):
        """Initialize with database connection."""
        self.db = db_connection
        self.areal_repo = ArealRepository(db_connection)
        self.plant_repo = PlantRepository(db_connection)

    def seed_initial_data(self) -> bool:
        """Seed the database with initial garden data if it's empty."""
        try:
            with self.db.get_connection() as conn:
                # Check if database is empty (no areals exist)
                areal_count = conn.execute("SELECT COUNT(*) FROM areals").fetchone()[0]

                if areal_count > 0:
                    print("Database already contains data, skipping seeding.")
                    return True

                print("Seeding database with initial garden data...")

                # Initial garden data
                garden_data = self._get_initial_garden_data()

                # Insert areals and plants
                for areal_data in garden_data["areals"]:
                    # Insert areal
                    if not self.areal_repo.insert_areal(areal_data):
                        print(f"Failed to insert areal: {areal_data['name']}")
                        return False

                    # Insert plants for this areal
                    for plant_data in areal_data["plants"]:
                        if not self.plant_repo.insert_plant(
                            areal_data["id"], plant_data
                        ):
                            print(f"Failed to insert plant: {plant_data['name']}")
                            return False

                print("Database seeded successfully with initial garden data.")
                return True

        except sqlite3.Error as e:
            print(f"Error seeding database: {e}")
            return False

    def _get_initial_garden_data(self) -> Dict[str, Any]:
        """Get the initial garden data structure."""
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
                            "imagePath": "rose",
                            "size": "big",
                            "position": "top",
                        },
                        {
                            "name": "Finja",
                            "health": "healthy",
                            "imagePath": "sunflower",
                            "size": "big",
                            "position": "left",
                        },
                        {
                            "name": "Mats",
                            "health": "healthy",
                            "imagePath": "happy-bamboo",
                            "size": "big",
                            "position": "right",
                        },
                        {
                            "name": "Mama",
                            "health": "healthy",
                            "imagePath": "lavendel",
                            "size": "medium",
                            "position": "center",
                        },
                        {
                            "name": "Papa",
                            "health": "okay",
                            "imagePath": "cactus",
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
                            "imagePath": "thymian",
                            "size": "big",
                            "position": "top",
                        },
                        {
                            "name": "Joggen",
                            "health": "okay",
                            "imagePath": "oat-grass",
                            "size": "big",
                            "position": "center",
                        },
                        {
                            "name": "Klettern",
                            "health": "healthy",
                            "imagePath": "hop",
                            "size": "big",
                            "position": "left",
                        },
                        {
                            "name": "Yoga",
                            "health": "healthy",
                            "imagePath": "lotus-flower",
                            "size": "medium",
                            "position": "right",
                        },
                        {
                            "name": "Schwimmen",
                            "health": "okay",
                            "imagePath": "water-hyacinth",
                            "size": "medium",
                            "position": "bottom-left",
                        },
                        {
                            "name": "Fußball",
                            "health": "dead",
                            "imagePath": "grass",
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
                            "imagePath": "bonsai",
                            "size": "big",
                            "position": "center",
                        },
                        {
                            "name": "Lesen",
                            "health": "healthy",
                            "imagePath": "ivy",
                            "size": "medium",
                            "position": "left",
                        },
                        {
                            "name": "Journaling",
                            "health": "healthy",
                            "imagePath": "sage",
                            "size": "medium",
                            "position": "right",
                        },
                        {
                            "name": "Waldbaden",
                            "health": "okay",
                            "imagePath": "sequoia",
                            "size": "medium",
                            "position": "bottom",
                        },
                        {
                            "name": "Psychotherapie",
                            "health": "healthy",
                            "imagePath": "aloe-vera",
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
                            "imagePath": "snowdrop",
                            "size": "small",
                            "position": "left",
                        },
                        {
                            "name": "Frankes",
                            "health": "healthy",
                            "imagePath": "marigold",
                            "size": "big",
                            "position": "center-top-mid",
                        },
                        {
                            "name": "Schwiegereltern",
                            "health": "healthy",
                            "imagePath": "cucumber",
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
                            "imagePath": "red-maple",
                            "size": "big",
                            "position": "center",
                        },
                        {
                            "name": "Magic",
                            "health": "dead",
                            "imagePath": "black-lotus",
                            "size": "small",
                            "position": "bottom",
                        },
                        {
                            "name": "Schach",
                            "health": "okay",
                            "imagePath": "cypress",
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
                            "imagePath": "dandelion",
                            "size": "medium",
                            "position": "center",
                        },
                        {
                            "name": "Sinn in der Arbeit",
                            "health": "dead",
                            "imagePath": "oak",
                            "size": "small",
                            "position": "bottom",
                        },
                    ],
                },
            ]
        }
