-- Garden Database Schema

-- Areals table
CREATE TABLE IF NOT EXISTS areals (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    horizontal_pos TEXT NOT NULL,
    vertical_pos TEXT NOT NULL,
    size TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Plants table
CREATE TABLE IF NOT EXISTS plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    areal_id TEXT NOT NULL,
    name TEXT NOT NULL,
    health TEXT NOT NULL,
    image_path TEXT NOT NULL,
    size TEXT NOT NULL,
    position TEXT NOT NULL,
    growth_stage INTEGER DEFAULT 1, -- 1-5 representing plant growth stages
    last_watered DATE NULL,
    days_without_water INTEGER DEFAULT 0,
    water_streak INTEGER DEFAULT 0, -- consecutive days watered
    total_water_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (areal_id) REFERENCES areals (id) ON DELETE CASCADE
);

-- Watering history table to track daily watering events
CREATE TABLE IF NOT EXISTS watering_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    watering_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plant_id) REFERENCES plants (id) ON DELETE CASCADE,
    UNIQUE(plant_id, watering_date) -- Prevent duplicate waterings on same day
);

-- Daily watering limits table
CREATE TABLE IF NOT EXISTS daily_watering_config (
    id INTEGER PRIMARY KEY,
    max_plants_per_day INTEGER DEFAULT 4,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default config
INSERT OR IGNORE INTO daily_watering_config (id, max_plants_per_day) VALUES (1, 4);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_plants_areal_id ON plants(areal_id);
CREATE INDEX IF NOT EXISTS idx_plants_health ON plants(health);
CREATE INDEX IF NOT EXISTS idx_plants_last_watered ON plants(last_watered);
CREATE INDEX IF NOT EXISTS idx_areals_position ON areals(horizontal_pos, vertical_pos);
CREATE INDEX IF NOT EXISTS idx_watering_history_date ON watering_history(watering_date);
CREATE INDEX IF NOT EXISTS idx_watering_history_plant ON watering_history(plant_id);
