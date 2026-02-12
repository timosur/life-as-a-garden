"""Repository for managing plants in the garden database."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlmodel import select
from sqlalchemy.orm import joinedload
from ..models import Plant, Areal
from ..base import get_session


class PlantRepository:
    """Repository for plant-related database operations."""

    def insert_plant(
        self, areal_id: str, plant_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Insert a plant and return the created plant."""
        try:
            with get_session() as session:
                plant = Plant(
                    areal_id=areal_id,
                    name=plant_data["name"],
                    health=plant_data["health"],
                    image_path=plant_data.get("image_path", ""),
                    size=plant_data["size"],
                    position=plant_data["position"],
                    days_without_water=plant_data.get("days_without_water", 0),
                    water_streak=plant_data.get("water_streak", 1),
                    total_water_count=plant_data.get("total_water_count", 20),
                    last_watered=plant_data.get("last_watered"),
                )
                session.add(plant)
                session.commit()
                session.refresh(plant)
                return plant.model_dump()
        except Exception as e:
            print(f"Error inserting plant: {e}")
            return None

    def get_plants_by_areal(self, areal_id: str) -> List[Dict[str, Any]]:
        """Get all plants for a specific areal."""
        with get_session() as session:
            plants = session.exec(
                select(Plant).where(Plant.areal_id == areal_id).order_by(Plant.name)
            ).all()
            return [p.model_dump() for p in plants]

    def get_all_plants(self) -> List[Dict[str, Any]]:
        """Get all plants with areal name."""
        with get_session() as session:
            stmt = (
                select(Plant, Areal.name.label("areal_name"))
                .join(Areal)
                .order_by(Plant.name)
            )
            results = session.exec(stmt).all()
            return [
                {**plant.model_dump(), "areal_name": areal_name}
                for plant, areal_name in results
            ]

    def get_plants_by_health(self, health: str) -> List[Dict[str, Any]]:
        """Get all plants with a specific health status."""
        with get_session() as session:
            stmt = (
                select(Plant, Areal.name.label("areal_name"))
                .join(Areal)
                .where(Plant.health == health)
                .order_by(Plant.name)
            )
            results = session.exec(stmt).all()
            return [
                {**plant.model_dump(), "areal_name": areal_name}
                for plant, areal_name in results
            ]

    def get_plants_needing_water(self) -> List[Dict[str, Any]]:
        """Get plants that need water (sorted by priority)."""
        with get_session() as session:
            stmt = (
                select(Plant, Areal.name.label("areal_name"))
                .join(Areal)
                .where(
                    (Plant.health.in_(["okay", "dead"]))
                    | (Plant.days_without_water >= 3)
                )
                .order_by(
                    (Plant.health == "dead").desc(),
                    Plant.days_without_water.desc(),
                    Plant.water_streak.asc(),
                )
            )
            results = session.exec(stmt).all()
            return [
                {**plant.model_dump(), "areal_name": areal_name}
                for plant, areal_name in results
            ]

    def get_plant_by_name(self, plant_name: str) -> Optional[Dict[str, Any]]:
        """Get a plant by name."""
        with get_session() as session:
            plant = session.exec(select(Plant).where(Plant.name == plant_name)).first()
            return plant.model_dump() if plant else None

    def get_plant_by_id(self, plant_id: int) -> Optional[Dict[str, Any]]:
        """Get a plant by ID."""
        with get_session() as session:
            plant = session.get(Plant, plant_id)
            return plant.model_dump() if plant else None

    def update_plant_health(self, plant_id: int, health: str) -> bool:
        """Update the health status of a plant."""
        try:
            with get_session() as session:
                plant = session.get(Plant, plant_id)
                if not plant:
                    return False
                plant.health = health
                plant.updated_at = datetime.utcnow()
                session.commit()
                return True
        except Exception as e:
            print(f"Error updating plant health: {e}")
            return False

    def update_plant(self, plant_id: int, plant_data: dict) -> bool:
        """Update plant information with provided fields."""
        try:
            allowed = {
                "areal_id",
                "name",
                "health",
                "image_path",
                "size",
                "position",
                "days_without_water",
                "water_streak",
                "total_water_count",
                "last_watered",
            }
            with get_session() as session:
                plant = session.get(Plant, plant_id)
                if not plant:
                    return False
                updated = False
                for field, value in plant_data.items():
                    if value is not None and field in allowed:
                        if field == "last_watered" and value == "":
                            setattr(plant, field, None)
                        else:
                            setattr(plant, field, value)
                        updated = True
                if not updated:
                    return False
                plant.updated_at = datetime.utcnow()
                session.commit()
                return True
        except Exception as e:
            print(f"Error updating plant: {e}")
            return False

    def update_plant_watering_stats(
        self,
        plant_id: int,
        last_watered: str,
        days_without_water: int,
        water_streak: int,
        total_water_count: int,
        health: str,
        size: str,
    ) -> bool:
        """Update plant watering statistics and status."""
        try:
            with get_session() as session:
                plant = session.get(Plant, plant_id)
                if not plant:
                    return False
                plant.last_watered = last_watered
                plant.days_without_water = days_without_water
                plant.water_streak = water_streak
                plant.total_water_count = total_water_count
                plant.health = health
                plant.size = size
                plant.updated_at = datetime.utcnow()
                session.commit()
                return True
        except Exception as e:
            print(f"Error updating plant watering stats: {e}")
            return False

    def delete_plant(self, plant_id: int) -> bool:
        """Delete a plant."""
        try:
            with get_session() as session:
                plant = session.get(Plant, plant_id)
                if not plant:
                    return False
                session.delete(plant)
                session.commit()
                return True
        except Exception as e:
            print(f"Error deleting plant: {e}")
            return False
