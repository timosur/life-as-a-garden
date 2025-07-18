"""
Garden Database Package

Refactored modular database package for the garden application.
Provides the same interface as before while using a clean, maintainable structure.
"""

# Main database class for backward compatibility
from .garden_database import GardenDatabase

# Individual components for advanced usage
from .base import DatabaseConnection
from .repositories import ArealRepository, PlantRepository, WateringRepository
from .services import GardenService, WateringService
from .utils import DataSeeder

__all__ = [
    "GardenDatabase",
    "DatabaseConnection",
    "ArealRepository",
    "PlantRepository",
    "WateringRepository",
    "GardenService",
    "WateringService",
    "DataSeeder",
]
