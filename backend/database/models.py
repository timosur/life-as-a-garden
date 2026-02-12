"""SQLModel ORM models for the garden database."""

from datetime import date, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Areal(SQLModel, table=True):
    """An areal (zone) in the garden."""

    __tablename__ = "areals"

    id: str = Field(primary_key=True)
    name: str
    horizontal_pos: str
    vertical_pos: str
    size: str
    created_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"server_default": "now()"}
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"server_default": "now()"}
    )

    plants: List["Plant"] = Relationship(back_populates="areal", cascade_delete=True)


class Plant(SQLModel, table=True):
    """A plant in the garden."""

    __tablename__ = "plants"

    id: Optional[int] = Field(default=None, primary_key=True)
    areal_id: str = Field(foreign_key="areals.id", index=True)
    name: str
    health: str = Field(index=True)
    image_path: str = ""
    size: str
    position: str
    last_watered: Optional[date] = Field(default=None, index=True)
    days_without_water: int = Field(default=0)
    water_streak: int = Field(default=0)
    total_water_count: int = Field(default=0)
    created_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"server_default": "now()"}
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"server_default": "now()"}
    )

    areal: Optional[Areal] = Relationship(back_populates="plants")
    watering_history: List["WateringHistory"] = Relationship(
        back_populates="plant", cascade_delete=True
    )
    status_changes: List["PlantStatusChange"] = Relationship(
        back_populates="plant", cascade_delete=True
    )


class WateringHistory(SQLModel, table=True):
    """Record of a plant being watered on a specific date."""

    __tablename__ = "watering_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    plant_id: int = Field(foreign_key="plants.id", index=True)
    watering_date: date = Field(index=True)
    created_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"server_default": "now()"}
    )

    plant: Optional[Plant] = Relationship(back_populates="watering_history")

    class Config:
        table_args = {"UniqueConstraint": ("plant_id", "watering_date")}


class DailyWateringConfig(SQLModel, table=True):
    """Configuration for daily watering limits."""

    __tablename__ = "daily_watering_config"

    id: Optional[int] = Field(default=None, primary_key=True)
    max_plants_per_day: int = Field(default=5)
    updated_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"server_default": "now()"}
    )


class PlantStatusChange(SQLModel, table=True):
    """Tracks changes in plant status over time."""

    __tablename__ = "plant_status_changes"

    id: Optional[int] = Field(default=None, primary_key=True)
    plant_id: int = Field(foreign_key="plants.id", index=True)
    change_date: date = Field(index=True)
    change_type: str
    old_health: str
    new_health: str
    old_water_streak: int
    new_water_streak: int
    old_days_without_water: int
    new_days_without_water: int
    old_total_water_count: int
    new_total_water_count: int
    old_size: Optional[str] = None
    new_size: Optional[str] = None
    created_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"server_default": "now()"}
    )

    plant: Optional[Plant] = Relationship(back_populates="status_changes")


class DailyUpdateTracker(SQLModel, table=True):
    """Tracks whether daily plant status update has been run for a given date."""

    __tablename__ = "daily_update_tracker"

    id: Optional[int] = Field(default=None, primary_key=True)
    update_date: str = Field(unique=True, index=True)
    completed_at: datetime
    plants_processed: int = Field(default=0)
    plants_updated: int = Field(default=0)


class Note(SQLModel, table=True):
    """Handwritten notes extracted from reMarkable."""

    __tablename__ = "notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    extracted_at: date
    created_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"server_default": "now()"}
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column_kwargs={"server_default": "now()"}
    )
