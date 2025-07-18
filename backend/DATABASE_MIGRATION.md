# Garden Database Migration

This document explains how the garden data has been migrated from a Python dictionary to a SQLite database.

## Overview

The garden data has been successfully migrated from a static Python dictionary (`garden_data.py`) to a SQLite database (`garden.db`). This provides several benefits:

- **Persistence**: Data changes persist between application restarts
- **Performance**: Optimized queries with database indexes
- **Scalability**: Can handle larger datasets efficiently
- **Concurrent Access**: Multiple processes can safely access the data
- **Data Integrity**: ACID transactions ensure data consistency

## Database Schema

### Areals Table

```sql
CREATE TABLE areals (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    horizontal_pos TEXT NOT NULL,
    vertical_pos TEXT NOT NULL,
    size TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Plants Table

```sql
CREATE TABLE plants (
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
```

## Files Structure

```
backend/
├── garden.db                    # SQLite database file
├── database/
│   ├── __init__.py
│   ├── garden_db.py            # Database access layer
│   └── schema.sql              # Database schema
├── data/
│   ├── garden_data.py          # Original data (preserved)
│   └── garden_data_db.py       # Database-backed data access
├── db_util.py                  # Database utility script
└── main.py                     # Updated API with database
```

## API Endpoints

The API has been updated with new database-backed endpoints:

- `GET /api/garden` - Get complete garden data
- `GET /api/garden/stats` - Get database statistics
- `GET /api/garden/areals` - Get all areals
- `GET /api/garden/areals/{areal_id}/plants` - Get plants for an areal
- `GET /api/garden/plants/health/{health}` - Get plants by health status
- `PUT /api/garden/plants/{plant_id}/health` - Update plant health

## Database Utility

Use the `db_util.py` script to manage the database:

```bash
# Show database statistics
python db_util.py stats

# List all areals
python db_util.py areals

# List plants by health status
python db_util.py plants healthy
python db_util.py plants dead
python db_util.py plants okay

# Export data to JSON
python db_util.py export garden_backup.json
```

## Usage

The database is automatically initialized when the application starts. The original `garden_data.py` file has been preserved for reference, but the application now uses the database.

To start the API server:

```bash
cd backend
uvicorn main:app --reload
```

## Current Database Stats

- **6 areals**: Core Family, Sport, Mental Health, Extended Family, Hobbies, Work
- **24 plants**: Various plants representing different life aspects
- **13 healthy plants**: Well-maintained areas of life
- **4 dead plants**: Areas needing attention
- **7 okay plants**: Areas with moderate health

## Backward Compatibility

The API maintains backward compatibility. The same endpoints return the same data structure, ensuring the frontend continues to work without changes.
