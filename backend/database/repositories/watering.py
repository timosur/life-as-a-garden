"""Repository for managing watering history and configuration."""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlmodel import select, func, text, col
from ..models import (
    WateringHistory,
    DailyWateringConfig,
    Plant,
    Areal,
    PlantStatusChange,
    DailyUpdateTracker,
)
from ..base import get_session


class WateringRepository:
    """Repository for watering-related database operations."""

    def get_daily_watering_limit(self) -> int:
        """Get the current daily watering limit."""
        with get_session() as session:
            config = session.get(DailyWateringConfig, 1)
            return config.max_plants_per_day if config else 5

    def set_daily_watering_limit(self, new_limit: int) -> bool:
        """Update the daily watering limit."""
        try:
            with get_session() as session:
                config = session.get(DailyWateringConfig, 1)
                if not config:
                    config = DailyWateringConfig(id=1, max_plants_per_day=new_limit)
                    session.add(config)
                else:
                    config.max_plants_per_day = new_limit
                    config.updated_at = datetime.utcnow()
                session.commit()
                return True
        except Exception as e:
            print(f"Error updating watering limit: {e}")
            return False

    def get_plants_watered_today_count(self, date_str: str) -> int:
        """Get count of plants watered on a specific date."""
        with get_session() as session:
            count = session.exec(
                select(func.count())
                .select_from(WateringHistory)
                .where(WateringHistory.watering_date == date_str)
            ).one()
            return count

    def add_watering_record(self, plant_id: int, watering_date: str) -> bool:
        """Add a watering record for a plant."""
        try:
            with get_session() as session:
                record = WateringHistory(plant_id=plant_id, watering_date=watering_date)
                session.add(record)
                session.commit()
                return True
        except Exception as e:
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                return False  # Already watered today
            print(f"Error adding watering record: {e}")
            return False

    def is_plant_watered_today(self, plant_id: int, date_str: str) -> bool:
        """Check if a plant has been watered today."""
        with get_session() as session:
            count = session.exec(
                select(func.count())
                .select_from(WateringHistory)
                .where(
                    WateringHistory.plant_id == plant_id,
                    WateringHistory.watering_date == date_str,
                )
            ).one()
            return count > 0

    def get_daily_watering_stats(self, date_str: str) -> Dict[str, Any]:
        """Get watering statistics for a specific day."""
        with get_session() as session:
            max_plants = self.get_daily_watering_limit()
            watered_today = self.get_plants_watered_today_count(date_str)

            stmt = (
                select(Plant.name, Plant.health, Plant.size)
                .join(WateringHistory, WateringHistory.plant_id == Plant.id)
                .where(WateringHistory.watering_date == date_str)
            )
            watered_plants = session.exec(stmt).all()

            return {
                "date": date_str,
                "daily_limit": max_plants,
                "plants_watered": watered_today,
                "remaining_capacity": max_plants - watered_today,
                "watered_plants": [
                    {"name": name, "health": health, "size": size}
                    for name, health, size in watered_plants
                ],
            }

    def get_watering_history(
        self, plant_id: int = None, limit: int = None
    ) -> List[Dict[str, Any]]:
        """Get watering history, optionally filtered by plant_id."""
        with get_session() as session:
            stmt = (
                select(WateringHistory, Plant.name.label("plant_name"))
                .join(Plant)
                .order_by(WateringHistory.watering_date.desc())
            )
            if plant_id:
                stmt = stmt.where(WateringHistory.plant_id == plant_id)
            if limit:
                stmt = stmt.limit(limit)

            results = session.exec(stmt).all()
            return [
                {**wh.model_dump(), "plant_name": plant_name}
                for wh, plant_name in results
            ]

    def get_last_watering_details(self) -> Dict[str, Any]:
        """Get detailed information about the last watering session."""
        with get_session() as session:
            latest = session.exec(
                select(WateringHistory.watering_date)
                .order_by(WateringHistory.watering_date.desc())
                .limit(1)
            ).first()

            if not latest:
                return {"success": False, "message": "No watering history found"}

            latest_date = latest

            # Get all plants watered on the latest date with status changes
            stmt = (
                select(
                    Plant,
                    Areal.name.label("areal_name"),
                    WateringHistory.created_at.label("watering_time"),
                )
                .join(WateringHistory, WateringHistory.plant_id == Plant.id)
                .join(Areal, Plant.areal_id == Areal.id)
                .where(WateringHistory.watering_date == latest_date)
                .order_by(WateringHistory.created_at.asc())
            )
            watered = session.exec(stmt).all()

            daily_stats = self.get_daily_watering_stats(str(latest_date))

            plant_details = []
            for plant, areal_name, watering_time in watered:
                # Get status change for this plant on this date
                sc = session.exec(
                    select(PlantStatusChange).where(
                        PlantStatusChange.plant_id == plant.id,
                        PlantStatusChange.change_date == latest_date,
                        PlantStatusChange.change_type == "watered",
                    )
                ).first()

                if sc:
                    before_state = {
                        "health": sc.old_health,
                        "size": sc.old_size,
                        "water_streak": sc.old_water_streak,
                        "total_water_count": sc.old_total_water_count,
                        "days_without_water": sc.old_days_without_water,
                    }
                    after_state = {
                        "health": sc.new_health,
                        "size": sc.new_size,
                        "water_streak": sc.new_water_streak,
                        "total_water_count": sc.new_total_water_count,
                        "days_without_water": sc.new_days_without_water,
                    }
                else:
                    after_state = {
                        "health": plant.health,
                        "size": plant.size,
                        "water_streak": plant.water_streak,
                        "total_water_count": plant.total_water_count,
                        "days_without_water": plant.days_without_water,
                    }
                    before_state = after_state.copy()

                changes = {
                    "health_changed": before_state["health"] != after_state["health"],
                    "size_changed": before_state["size"] != after_state["size"],
                    "water_streak_increased": after_state["water_streak"]
                    > before_state["water_streak"],
                    "days_without_water_reset": after_state["days_without_water"] == 0
                    and before_state["days_without_water"] > 0,
                }

                plant_details.append(
                    {
                        "id": plant.id,
                        "name": plant.name,
                        "areal_name": areal_name,
                        "watering_time": str(watering_time) if watering_time else None,
                        "before": before_state,
                        "after": after_state,
                        "changes": changes,
                    }
                )

            return {
                "success": True,
                "watering_date": str(latest_date),
                "daily_stats": daily_stats,
                "plants_watered": len(plant_details),
                "plant_details": plant_details,
            }

    def record_plant_status_change(
        self,
        plant_id: int,
        change_date: str,
        change_type: str,
        old_state: Dict[str, Any],
        new_state: Dict[str, Any],
    ) -> bool:
        """Record a plant status change."""
        try:
            with get_session() as session:
                sc = PlantStatusChange(
                    plant_id=plant_id,
                    change_date=change_date,
                    change_type=change_type,
                    old_health=old_state["health"],
                    new_health=new_state["health"],
                    old_water_streak=old_state["water_streak"],
                    new_water_streak=new_state["water_streak"],
                    old_days_without_water=old_state["days_without_water"],
                    new_days_without_water=new_state["days_without_water"],
                    old_total_water_count=old_state["total_water_count"],
                    new_total_water_count=new_state["total_water_count"],
                    old_size=old_state["size"],
                    new_size=new_state["size"],
                )
                session.add(sc)
                session.commit()
                return True
        except Exception as e:
            print(f"Error recording status change: {e}")
            return False

    def get_plant_status_changes(
        self, plant_id: int = None, limit: int = None
    ) -> List[Dict[str, Any]]:
        """Get plant status changes."""
        with get_session() as session:
            stmt = (
                select(PlantStatusChange, Plant.name.label("plant_name"))
                .join(Plant)
                .order_by(
                    PlantStatusChange.change_date.desc(),
                    PlantStatusChange.created_at.desc(),
                )
            )
            if plant_id:
                stmt = stmt.where(PlantStatusChange.plant_id == plant_id)
            if limit:
                stmt = stmt.limit(limit)

            results = session.exec(stmt).all()
            return [{**sc.model_dump(), "plant_name": pn} for sc, pn in results]

    def get_todays_plant_status_changes(self) -> List[Dict[str, Any]]:
        """Get plant status changes for today."""
        today = date.today()
        with get_session() as session:
            stmt = (
                select(PlantStatusChange, Plant.name.label("plant_name"))
                .join(Plant)
                .where(PlantStatusChange.change_date == today)
                .order_by(PlantStatusChange.created_at.desc())
            )
            results = session.exec(stmt).all()
            return [{**sc.model_dump(), "plant_name": pn} for sc, pn in results]

    def migrate_daily_limit_to_4(self) -> bool:
        """Set daily limit to 4."""
        return self.set_daily_watering_limit(4)

    def is_daily_update_completed(self, date_str: str) -> bool:
        """Check if daily update has been completed for a specific date."""
        with get_session() as session:
            count = session.exec(
                select(func.count())
                .select_from(DailyUpdateTracker)
                .where(DailyUpdateTracker.update_date == date_str)
            ).one()
            return count > 0

    def record_daily_update_completion(
        self, date_str: str, plants_processed: int, plants_updated: int
    ) -> bool:
        """Record daily update completion."""
        try:
            with get_session() as session:
                tracker = DailyUpdateTracker(
                    update_date=date_str,
                    completed_at=datetime.utcnow(),
                    plants_processed=plants_processed,
                    plants_updated=plants_updated,
                )
                session.add(tracker)
                session.commit()
                return True
        except Exception as e:
            print(f"Error recording daily update completion: {e}")
            return False

    def get_daily_update_info(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Get info about a daily update for a specific date."""
        with get_session() as session:
            tracker = session.exec(
                select(DailyUpdateTracker).where(
                    DailyUpdateTracker.update_date == date_str
                )
            ).first()
            return tracker.model_dump() if tracker else None

    def get_watering_history_by_date_range(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """Get watering history within a date range."""
        with get_session() as session:
            stmt = (
                select(
                    WateringHistory.watering_date,
                    Plant.name.label("plant_name"),
                    Plant.id.label("plant_id"),
                )
                .join(Plant)
                .where(
                    WateringHistory.watering_date >= start_date,
                    WateringHistory.watering_date <= end_date,
                )
                .order_by(WateringHistory.watering_date.desc(), Plant.name.asc())
            )
            results = session.exec(stmt).all()
            return [
                {"watering_date": str(wd), "plant_name": pn, "plant_id": pid}
                for wd, pn, pid in results
            ]

    def get_plants_not_watered(self, date_str: str) -> List[Dict[str, Any]]:
        """Get all plants that were NOT watered on the given date."""
        with get_session() as session:
            watered_ids = select(WateringHistory.plant_id).where(
                WateringHistory.watering_date == date_str
            )
            stmt = select(Plant).where(Plant.id.not_in(watered_ids))
            plants = session.exec(stmt).all()
            return [p.model_dump() for p in plants]
