import sqlite3
from typing import List, Dict, Any
from pathlib import Path


class GardenDatabase:
    """Database handler for the garden application using SQLite."""

    def __init__(self, db_path: str = "garden.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with the schema and seed initial data."""
        # Get the schema file path
        schema_path = Path(__file__).parent / "schema.sql"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Enable column access by name

            # Read and execute schema
            if schema_path.exists():
                with open(schema_path, "r") as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
            else:
                # Fallback schema if file doesn't exist
                self._create_tables_fallback(conn)

        # Seed initial data if database is empty
        self.seed_initial_data()

    def _create_tables_fallback(self, conn: sqlite3.Connection):
        """Fallback method to create tables if schema.sql is not found."""
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS areals (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                horizontal_pos TEXT NOT NULL,
                vertical_pos TEXT NOT NULL,
                size TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS plants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                areal_id TEXT NOT NULL,
                name TEXT NOT NULL,
                health TEXT NOT NULL,
                image_path TEXT NOT NULL,
                size TEXT NOT NULL,
                position TEXT NOT NULL,
                growth_stage INTEGER DEFAULT 1,
                last_watered DATE NULL,
                days_without_water INTEGER DEFAULT 0,
                water_streak INTEGER DEFAULT 0,
                total_water_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (areal_id) REFERENCES areals (id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS watering_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER NOT NULL,
                watering_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plant_id) REFERENCES plants (id) ON DELETE CASCADE,
                UNIQUE(plant_id, watering_date)
            );
            
            CREATE TABLE IF NOT EXISTS daily_watering_config (
                id INTEGER PRIMARY KEY,
                max_plants_per_day INTEGER DEFAULT 5,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            INSERT OR IGNORE INTO daily_watering_config (id, max_plants_per_day) VALUES (1, 4);
                position TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (areal_id) REFERENCES areals (id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_plants_areal_id ON plants(areal_id);
            CREATE INDEX IF NOT EXISTS idx_plants_health ON plants(health);
            CREATE INDEX IF NOT EXISTS idx_plants_last_watered ON plants(last_watered);
            CREATE INDEX IF NOT EXISTS idx_areals_position ON areals(horizontal_pos, vertical_pos);
            CREATE INDEX IF NOT EXISTS idx_watering_history_date ON watering_history(watering_date);
            CREATE INDEX IF NOT EXISTS idx_watering_history_plant ON watering_history(plant_id);
        """)

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def insert_areal(self, areal_data: Dict[str, Any]) -> bool:
        """Insert an areal into the database."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO areals 
                    (id, name, horizontal_pos, vertical_pos, size)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        areal_data["id"],
                        areal_data["name"],
                        areal_data["horizontalPos"],
                        areal_data["verticalPos"],
                        areal_data["size"],
                    ),
                )
                return True
        except sqlite3.Error as e:
            print(f"Error inserting areal: {e}")
            return False

    def insert_plant(self, areal_id: str, plant_data: Dict[str, Any]) -> bool:
        """Insert a plant into the database."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO plants 
                    (areal_id, name, health, image_path, size, position)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        areal_id,
                        plant_data["name"],
                        plant_data["health"],
                        plant_data["imagePath"],
                        plant_data["size"],
                        plant_data["position"],
                    ),
                )
                return True
        except sqlite3.Error as e:
            print(f"Error inserting plant: {e}")
            return False

    def get_all_areals(self) -> List[Dict[str, Any]]:
        """Get all areals from the database."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM areals ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def get_plants_by_areal(self, areal_id: str) -> List[Dict[str, Any]]:
        """Get all plants for a specific areal."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM plants WHERE areal_id = ? ORDER BY name", (areal_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_garden_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the complete garden data in the original format."""
        areals = []

        for areal in self.get_all_areals():
            plants = self.get_plants_by_areal(areal["id"])

            # Convert database format back to original format
            areal_data = {
                "id": areal["id"],
                "name": areal["name"],
                "horizontalPos": areal["horizontal_pos"],
                "verticalPos": areal["vertical_pos"],
                "size": areal["size"],
                "plants": [],
            }

            for plant in plants:
                plant_data = {
                    "name": plant["name"],
                    "health": plant["health"],
                    "imagePath": plant["image_path"],
                    "size": plant["size"],
                    "position": plant["position"],
                }
                areal_data["plants"].append(plant_data)

            areals.append(areal_data)

        return {"areals": areals}

    def update_plant_health(self, plant_id: int, health: str) -> bool:
        """Update the health status of a plant."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE plants SET health = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (health, plant_id),
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating plant health: {e}")
            return False

    def delete_plant(self, plant_id: int) -> bool:
        """Delete a plant from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting plant: {e}")
            return False

    def delete_areal(self, areal_id: str) -> bool:
        """Delete an areal and all its plants from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("DELETE FROM areals WHERE id = ?", (areal_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting areal: {e}")
            return False

    def get_plants_by_health(self, health: str) -> List[Dict[str, Any]]:
        """Get all plants with a specific health status."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """SELECT p.*, a.name as areal_name 
                   FROM plants p 
                   JOIN areals a ON p.areal_id = a.id 
                   WHERE p.health = ? 
                   ORDER BY p.name""",
                (health,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_database_stats(self) -> Dict[str, int]:
        """Get basic statistics about the database."""
        with self.get_connection() as conn:
            areal_count = conn.execute("SELECT COUNT(*) FROM areals").fetchone()[0]
            plant_count = conn.execute("SELECT COUNT(*) FROM plants").fetchone()[0]
            healthy_plants = conn.execute(
                "SELECT COUNT(*) FROM plants WHERE health = 'healthy'"
            ).fetchone()[0]
            dead_plants = conn.execute(
                "SELECT COUNT(*) FROM plants WHERE health = 'dead'"
            ).fetchone()[0]

            return {
                "total_areals": areal_count,
                "total_plants": plant_count,
                "healthy_plants": healthy_plants,
                "dead_plants": dead_plants,
            }

    def water_plants(
        self, checked_plant_names: List[str], watering_date: str = None
    ) -> Dict[str, Any]:
        """
        Water the checked plants and update their status based on watering algorithm.

        Args:
            checked_plant_names: List of plant names that were checked (watered)
            watering_date: Date in YYYY-MM-DD format (defaults to today)

        Returns:
            Dict with operation results and updated plant statuses
        """
        from datetime import date

        if watering_date is None:
            watering_date = date.today().strftime("%Y-%m-%d")

        try:
            with self.get_connection() as conn:
                # Get daily watering limit
                max_plants = conn.execute(
                    "SELECT max_plants_per_day FROM daily_watering_config WHERE id = 1"
                ).fetchone()[0]

                # Count plants already watered today
                plants_watered_today = conn.execute(
                    "SELECT COUNT(*) FROM watering_history WHERE watering_date = ?",
                    (watering_date,),
                ).fetchone()[0]

                remaining_capacity = max_plants - plants_watered_today

                if remaining_capacity <= 0:
                    return {
                        "success": False,
                        "message": f"Daily watering limit ({max_plants}) already reached",
                        "plants_watered_today": plants_watered_today,
                        "updated_plants": [],
                    }

                # Limit checked plants to remaining capacity
                plants_to_water = checked_plant_names[:remaining_capacity]

                updated_plants = []
                for plant_name in plants_to_water:
                    # Get plant info
                    plant = conn.execute(
                        "SELECT * FROM plants WHERE name = ?", (plant_name,)
                    ).fetchone()

                    if not plant:
                        continue

                    plant_id = plant["id"]

                    # Record watering event (ignore if already watered today)
                    try:
                        conn.execute(
                            "INSERT INTO watering_history (plant_id, watering_date) VALUES (?, ?)",
                            (plant_id, watering_date),
                        )

                        # Update plant watering stats and calculate new status
                        new_stats = self._calculate_plant_status_after_watering(
                            conn, plant_id, watering_date
                        )
                        updated_plants.append(
                            {"plant_id": plant_id, "name": plant_name, **new_stats}
                        )

                    except sqlite3.IntegrityError:
                        # Plant already watered today, skip
                        pass

                # Update plants that weren't watered (increase days_without_water)
                self._update_non_watered_plants(conn, watering_date)

                return {
                    "success": True,
                    "message": f"Watered {len(updated_plants)} plants",
                    "daily_limit": max_plants,
                    "plants_watered_today": plants_watered_today + len(updated_plants),
                    "updated_plants": updated_plants,
                }

        except sqlite3.Error as e:
            print(f"Error watering plants: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_plant_status_after_watering(
        self, conn: sqlite3.Connection, plant_id: int, watering_date: str
    ) -> Dict[str, Any]:
        """Calculate new plant status after watering with improved health and size logic."""
        from datetime import datetime

        # Get current plant data
        plant = conn.execute(
            "SELECT * FROM plants WHERE id = ?", (plant_id,)
        ).fetchone()

        # Calculate new water streak
        last_watered = plant["last_watered"]
        current_date = datetime.strptime(watering_date, "%Y-%m-%d").date()

        if last_watered:
            last_watered_date = datetime.strptime(last_watered, "%Y-%m-%d").date()
            days_gap = (current_date - last_watered_date).days

            if days_gap == 1:
                # Consecutive day - increase streak
                new_streak = plant["water_streak"] + 1
            else:
                # Gap in watering - reset streak but don't penalize too much
                new_streak = 1
        else:
            # First time watering
            new_streak = 1

        # Update total water count
        new_total_count = plant["total_water_count"] + 1

        # Calculate health based on watering consistency and current health
        current_health = plant["health"]

        if current_health == "dead":
            # Dead plants can recover but need consistent watering
            if new_streak >= 5:
                new_health = "okay"
            elif new_streak >= 3:
                new_health = "dead"  # Still dead but improving
            else:
                new_health = "dead"
        elif current_health == "okay":
            # Okay plants can improve to healthy or decline
            if new_streak >= 7:
                new_health = "healthy"
            elif new_streak >= 3:
                new_health = "okay"
            else:
                new_health = "okay"  # Stay okay for now
        else:  # healthy or other states
            # Healthy plants maintain health with regular watering
            if new_streak >= 5:
                new_health = "healthy"
            elif new_streak >= 2:
                new_health = "healthy"
            elif new_total_count >= 3:
                new_health = "okay"
            else:
                new_health = "okay"

        # Calculate growth stage (1-5 based on total water count and streak)
        # More emphasis on consistency (streak) for growth
        growth_from_streak = min(3, new_streak // 2)  # Max 3 from streak
        growth_from_total = min(2, new_total_count // 5)  # Max 2 from total count
        new_growth_stage = min(5, max(1, growth_from_streak + growth_from_total + 1))

        # Calculate size based on growth stage and health
        if new_health == "dead":
            # Dead plants shrink regardless of growth stage
            new_size = "small"
        elif new_health == "okay":
            # Okay plants can be small to medium
            if new_growth_stage >= 4:
                new_size = "medium"
            else:
                new_size = "small"
        else:  # healthy
            # Healthy plants can reach full size potential
            if new_growth_stage >= 4:
                new_size = "big"
            elif new_growth_stage >= 3:
                new_size = "medium"
            else:
                new_size = "small"

        # Update the plant in database
        conn.execute(
            """UPDATE plants SET 
               last_watered = ?, 
               days_without_water = 0, 
               water_streak = ?, 
               total_water_count = ?,
               growth_stage = ?,
               health = ?,
               size = ?,
               updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                watering_date,
                new_streak,
                new_total_count,
                new_growth_stage,
                new_health,
                new_size,
                plant_id,
            ),
        )

        return {
            "health": new_health,
            "size": new_size,
            "growth_stage": new_growth_stage,
            "water_streak": new_streak,
            "total_water_count": new_total_count,
            "days_without_water": 0,
        }

    def _update_non_watered_plants(self, conn: sqlite3.Connection, current_date: str):
        """Update plants that weren't watered today with improved declining logic."""
        # Get plants not watered today
        plants_not_watered = conn.execute(
            """SELECT p.* FROM plants p 
               WHERE p.id NOT IN (
                   SELECT wh.plant_id FROM watering_history wh 
                   WHERE wh.watering_date = ?
               )""",
            (current_date,),
        ).fetchall()

        for plant in plants_not_watered:
            days_without_water = plant["days_without_water"] + 1
            current_health = plant["health"]

            # Calculate declining health based on current health and days without water
            if current_health == "healthy":
                if days_without_water >= 5:
                    new_health = "okay"
                elif days_without_water >= 8:
                    new_health = "dead"
                else:
                    new_health = "healthy"  # Stay healthy for a while
            elif current_health == "okay":
                if days_without_water >= 3:
                    new_health = "dead"
                else:
                    new_health = "okay"
            else:  # dead or other states
                new_health = "dead"  # Stay dead

            # Reset water streak if too many days without water
            new_streak = 0 if days_without_water >= 2 else plant["water_streak"]

            # Size reduction for plants not watered
            current_size = plant["size"]
            if days_without_water >= 4 and current_size == "big":
                new_size = "medium"
            elif days_without_water >= 6 and current_size == "medium":
                new_size = "small"
            else:
                new_size = current_size

            conn.execute(
                """UPDATE plants SET 
                   days_without_water = ?, 
                   water_streak = ?,
                   health = ?,
                   size = ?,
                   updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (days_without_water, new_streak, new_health, new_size, plant["id"]),
            )

    def get_daily_watering_stats(self, date_str: str = None) -> Dict[str, Any]:
        """Get watering statistics for a specific day."""
        from datetime import date

        if date_str is None:
            date_str = date.today().strftime("%Y-%m-%d")

        with self.get_connection() as conn:
            # Get daily limit
            max_plants = conn.execute(
                "SELECT max_plants_per_day FROM daily_watering_config WHERE id = 1"
            ).fetchone()[0]

            # Count plants watered today
            watered_today = conn.execute(
                "SELECT COUNT(*) FROM watering_history WHERE watering_date = ?",
                (date_str,),
            ).fetchone()[0]

            # Get list of plants watered today
            watered_plants = conn.execute(
                """SELECT p.name, p.health, p.size, p.growth_stage 
                   FROM plants p 
                   JOIN watering_history wh ON p.id = wh.plant_id 
                   WHERE wh.watering_date = ?""",
                (date_str,),
            ).fetchall()

            return {
                "date": date_str,
                "daily_limit": max_plants,
                "plants_watered": watered_today,
                "remaining_capacity": max_plants - watered_today,
                "watered_plants": [dict(row) for row in watered_plants],
            }

    def set_daily_watering_limit(self, new_limit: int) -> bool:
        """Update the daily watering limit."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "UPDATE daily_watering_config SET max_plants_per_day = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
                    (new_limit,),
                )
                return True
        except sqlite3.Error as e:
            print(f"Error updating watering limit: {e}")
            return False

    def get_plants_needing_water(self) -> List[Dict[str, Any]]:
        """Get plants that need water (sorted by priority)."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """SELECT p.*, a.name as areal_name 
                   FROM plants p 
                   JOIN areals a ON p.areal_id = a.id 
                   WHERE p.health IN ('okay', 'dead') OR p.days_without_water >= 2
                   ORDER BY p.days_without_water DESC, p.health = 'dead' DESC, p.water_streak ASC""",
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_all_plants(self) -> List[Dict[str, Any]]:
        """Get all plants with their complete information."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """SELECT p.*, a.name as areal_name 
                   FROM plants p 
                   JOIN areals a ON p.areal_id = a.id 
                   ORDER BY p.name"""
            )
            return [dict(row) for row in cursor.fetchall()]

    def migrate_daily_limit_to_4(self) -> bool:
        """Migrate existing database to set daily limit to 4 plants."""
        try:
            with self.get_connection() as conn:
                # Update existing config to limit of 4
                conn.execute(
                    "UPDATE daily_watering_config SET max_plants_per_day = 4, updated_at = CURRENT_TIMESTAMP WHERE id = 1"
                )
                return True
        except sqlite3.Error as e:
            print(f"Error migrating daily limit: {e}")
            return False

    def seed_initial_data(self) -> bool:
        """Seed the database with initial garden data if it's empty."""
        try:
            with self.get_connection() as conn:
                # Check if database is empty (no areals exist)
                areal_count = conn.execute("SELECT COUNT(*) FROM areals").fetchone()[0]

                if areal_count > 0:
                    print("Database already contains data, skipping seeding.")
                    return True

                print("Seeding database with initial garden data...")

                # Initial garden data
                garden_data = {
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

                # Insert areals and plants
                for areal_data in garden_data["areals"]:
                    # Insert areal
                    if not self.insert_areal(areal_data):
                        print(f"Failed to insert areal: {areal_data['name']}")
                        return False

                    # Insert plants for this areal
                    for plant_data in areal_data["plants"]:
                        if not self.insert_plant(areal_data["id"], plant_data):
                            print(f"Failed to insert plant: {plant_data['name']}")
                            return False

                print("Database seeded successfully with initial garden data.")
                return True

        except sqlite3.Error as e:
            print(f"Error seeding database: {e}")
            return False

    def water_single_plant(
        self, plant_identifier: str, watering_date: str = None, by_id: bool = False
    ) -> Dict[str, Any]:
        """
        Water a single plant by name or ID.

        Args:
            plant_identifier: Plant name or ID
            watering_date: Date in YYYY-MM-DD format (defaults to today)
            by_id: If True, plant_identifier is treated as plant ID, otherwise as plant name

        Returns:
            Dict with operation results and updated plant status
        """
        from datetime import date

        if watering_date is None:
            watering_date = date.today().strftime("%Y-%m-%d")

        try:
            with self.get_connection() as conn:
                # Get daily watering limit
                max_plants = conn.execute(
                    "SELECT max_plants_per_day FROM daily_watering_config WHERE id = 1"
                ).fetchone()[0]

                # Count plants already watered today
                plants_watered_today = conn.execute(
                    "SELECT COUNT(*) FROM watering_history WHERE watering_date = ?",
                    (watering_date,),
                ).fetchone()[0]

                if plants_watered_today >= max_plants:
                    return {
                        "success": False,
                        "message": f"Daily watering limit ({max_plants}) already reached",
                        "plants_watered_today": plants_watered_today,
                    }

                # Find the plant
                if by_id:
                    plant = conn.execute(
                        "SELECT * FROM plants WHERE id = ?", (int(plant_identifier),)
                    ).fetchone()
                else:
                    plant = conn.execute(
                        "SELECT * FROM plants WHERE name = ?", (plant_identifier,)
                    ).fetchone()

                if not plant:
                    return {
                        "success": False,
                        "message": f"Plant {'ID' if by_id else 'name'} '{plant_identifier}' not found",
                    }

                plant_id = plant["id"]
                plant_name = plant["name"]

                # Check if plant is already watered today
                already_watered = conn.execute(
                    "SELECT COUNT(*) FROM watering_history WHERE plant_id = ? AND watering_date = ?",
                    (plant_id, watering_date),
                ).fetchone()[0]

                if already_watered > 0:
                    return {
                        "success": False,
                        "message": f"Plant '{plant_name}' has already been watered today",
                    }

                # Record watering event
                conn.execute(
                    "INSERT INTO watering_history (plant_id, watering_date) VALUES (?, ?)",
                    (plant_id, watering_date),
                )

                # Update plant watering stats and calculate new status
                new_stats = self._calculate_plant_status_after_watering(
                    conn, plant_id, watering_date
                )

                # Update plants that weren't watered (increase days_without_water)
                self._update_non_watered_plants(conn, watering_date)

                return {
                    "success": True,
                    "message": f"Successfully watered '{plant_name}'",
                    "plant": {
                        "id": plant_id,
                        "name": plant_name,
                        **new_stats,
                    },
                    "plants_watered_today": plants_watered_today + 1,
                    "daily_limit": max_plants,
                }

        except sqlite3.Error as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
