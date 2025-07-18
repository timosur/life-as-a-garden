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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (areal_id) REFERENCES areals (id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_plants_areal_id ON plants(areal_id);
CREATE INDEX IF NOT EXISTS idx_plants_health ON plants(health);
CREATE INDEX IF NOT EXISTS idx_areals_position ON areals(horizontal_pos, vertical_pos);
