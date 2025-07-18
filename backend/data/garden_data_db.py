"""
Garden data access layer using SQLite database.

This module provides a database-backed implementation of the garden data,
replacing the original Python dictionary approach.
"""

from pathlib import Path
import sys
from database.garden_db import GardenDatabase

# Add the database module to the path
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))


# Initialize database connection
_db_path = backend_dir / "garden.db"
_db = GardenDatabase(str(_db_path))


def get_garden_data():
    """
    Get the complete garden data from the database.

    Returns:
        dict: Garden data in the same format as the original dictionary
    """
    return _db.get_garden_data()


def get_areals():
    """Get all areals from the database."""
    return _db.get_all_areals()


def get_plants_by_areal(areal_id: str):
    """Get all plants for a specific areal."""
    return _db.get_plants_by_areal(areal_id)


def get_plants_by_health(health: str):
    """Get all plants with a specific health status."""
    return _db.get_plants_by_health(health)


def update_plant_health(plant_id: int, health: str):
    """Update the health status of a plant."""
    return _db.update_plant_health(plant_id, health)


def get_database_stats():
    """Get basic statistics about the garden database."""
    return _db.get_database_stats()


# For backward compatibility, expose the data as before
# This ensures existing code that imports garden_data continues to work
garden_data = get_garden_data()


def refresh_garden_data():
    """Refresh the garden_data variable with latest database content."""
    global garden_data
    garden_data = get_garden_data()
    return garden_data


# Export the database instance for advanced usage
garden_db = _db
