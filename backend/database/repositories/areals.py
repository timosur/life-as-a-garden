"""Repository for managing areals in the garden database."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlmodel import select
from ..models import Areal
from ..base import get_session


class ArealRepository:
    """Repository for areal-related database operations."""

    def insert_areal(self, areal_data: Dict[str, Any]) -> bool:
        """Insert or replace an areal."""
        try:
            with get_session() as session:
                existing = session.get(Areal, areal_data["id"])
                if existing:
                    existing.name = areal_data["name"]
                    existing.horizontal_pos = areal_data["horizontalPos"]
                    existing.vertical_pos = areal_data["verticalPos"]
                    existing.size = areal_data["size"]
                    existing.updated_at = datetime.utcnow()
                else:
                    areal = Areal(
                        id=areal_data["id"],
                        name=areal_data["name"],
                        horizontal_pos=areal_data["horizontalPos"],
                        vertical_pos=areal_data["verticalPos"],
                        size=areal_data["size"],
                    )
                    session.add(areal)
                session.commit()
                return True
        except Exception as e:
            print(f"Error inserting areal: {e}")
            return False

    def get_all_areals(self) -> List[Dict[str, Any]]:
        """Get all areals ordered by name."""
        with get_session() as session:
            areals = session.exec(select(Areal).order_by(Areal.name)).all()
            return [areal.model_dump() for areal in areals]

    def delete_areal(self, areal_id: str) -> bool:
        """Delete an areal (cascades to plants)."""
        try:
            with get_session() as session:
                areal = session.get(Areal, areal_id)
                if not areal:
                    return False
                session.delete(areal)
                session.commit()
                return True
        except Exception as e:
            print(f"Error deleting areal: {e}")
            return False

    def get_areal_by_id(self, areal_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific areal by ID."""
        with get_session() as session:
            areal = session.get(Areal, areal_id)
            return areal.model_dump() if areal else None

    def update_areal(self, areal_id: str, areal_data: dict) -> bool:
        """Update areal information with provided fields."""
        try:
            allowed = {"name", "horizontal_pos", "vertical_pos", "size"}
            with get_session() as session:
                areal = session.get(Areal, areal_id)
                if not areal:
                    return False
                updated = False
                for field, value in areal_data.items():
                    if value is not None and field in allowed:
                        setattr(areal, field, value)
                        updated = True
                if not updated:
                    return False
                areal.updated_at = datetime.utcnow()
                session.commit()
                return True
        except Exception as e:
            print(f"Error updating areal: {e}")
            return False
