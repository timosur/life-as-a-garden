"""
Garden Database Package

Modular database package using SQLModel ORM + PostgreSQL.
"""

from .garden_database import GardenDatabase
from .base import get_session, engine, init_db
from .models import (
    Areal,
    Plant,
    WateringHistory,
    DailyWateringConfig,
    PlantStatusChange,
    DailyUpdateTracker,
    Note,
)
from .repositories import (
    ArealRepository,
    PlantRepository,
    WateringRepository,
    NotesRepository,
)
from .services import GardenService, WateringService, NotesService
from .utils import DataSeeder

__all__ = [
    "GardenDatabase",
    "get_session",
    "engine",
    "init_db",
    "Areal",
    "Plant",
    "WateringHistory",
    "DailyWateringConfig",
    "PlantStatusChange",
    "DailyUpdateTracker",
    "Note",
    "ArealRepository",
    "PlantRepository",
    "WateringRepository",
    "NotesRepository",
    "GardenService",
    "WateringService",
    "NotesService",
    "DataSeeder",
]
