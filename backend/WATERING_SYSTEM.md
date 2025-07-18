# Updated Watering System

## Overview

The watering system has been updated with improved logic for plant health and size management based on watering frequency. The system now properly tracks watering history and enforces daily limits.

## Key Features

### Daily Watering Limits

- **Maximum plants per day**: 4 plants (reduced from 5)
- **One watering per plant per day**: Each plant can only be watered once per day
- **Remaining capacity tracking**: System shows how many more plants can be watered today

### Plant Health States

Plants have three health states that change based on watering consistency:

1. **Healthy**: Well-maintained plants with regular watering
2. **Okay**: Plants that need attention but are still alive
3. **Dead**: Plants that have been neglected but can still recover

### Plant Sizes

Plants have three sizes that change based on growth and health:

1. **Small**: New or struggling plants
2. **Medium**: Growing plants with moderate care
3. **Big**: Mature, well-cared-for plants

## Watering Logic

### When Plants Are Watered

- **Water streak**: Consecutive days of watering (resets after 2+ days gap)
- **Total water count**: Lifetime total of watering events
- **Growth stage**: 1-5 scale based on care consistency

#### Health Progression (with watering):

- **Dead → Okay**: Requires 5+ consecutive days of watering
- **Okay → Healthy**: Requires 7+ consecutive days of watering
- **Healthy**: Maintained with regular watering (2+ day streak)

#### Size Progression (with watering):

- **Dead plants**: Always remain small until health improves
- **Okay plants**: Can grow to medium size (growth stage 4+)
- **Healthy plants**: Can reach full size potential:
  - Growth stage 4+: Big size
  - Growth stage 3: Medium size
  - Growth stage 1-2: Small size

### When Plants Are NOT Watered

Plants that aren't watered experience decline:

#### Health Decline:

- **Healthy plants**:
  - 5+ days without water → Okay
  - 8+ days without water → Dead
- **Okay plants**:
  - 3+ days without water → Dead
- **Dead plants**: Remain dead

#### Size Decline:

- **Big → Medium**: After 4+ days without water
- **Medium → Small**: After 6+ days without water

#### Other Effects:

- **Water streak reset**: After 2+ days without water
- **Days without water counter**: Increments daily for non-watered plants

## API Endpoints

### Get Watering Stats

```
GET /api/garden/watering/stats
```

Returns current watering statistics and plants needing water.

### Update Daily Limit

```
PUT /api/garden/watering/limit
Body: {"new_limit": 4}
```

Updates the daily watering limit (1-50 plants).

### Water Plants from Analysis

```
POST /api/garden/water
```

Analyzes checklist image and waters checked plants.

## Database Schema Changes

### New Columns in `plants` table:

- `growth_stage`: INTEGER (1-5 growth stages)
- `last_watered`: DATE (last watering date)
- `days_without_water`: INTEGER (days since last watering)
- `water_streak`: INTEGER (consecutive watering days)
- `total_water_count`: INTEGER (lifetime watering count)

### New Tables:

- `watering_history`: Tracks daily watering events
- `daily_watering_config`: Stores daily limits

## Migration

The system includes a migration script (`migrate_watering_system.py`) that:

1. Adds missing columns to existing plants
2. Creates new watering tables
3. Sets daily limit to 4 plants
4. Creates necessary indexes

## Examples

### Healthy Plant Care

```
Day 1: Water → Health: okay, Size: small, Streak: 1
Day 2: Water → Health: okay, Size: small, Streak: 2
Day 3: Water → Health: okay, Size: small, Streak: 3
Day 4: Water → Health: okay, Size: medium, Streak: 4
Day 5: Water → Health: okay, Size: medium, Streak: 5
Day 6: Water → Health: okay, Size: medium, Streak: 6
Day 7: Water → Health: healthy, Size: big, Streak: 7
```

### Plant Recovery from Dead

```
Dead plant + 5 consecutive days watering → Okay
Okay plant + 7 consecutive days watering → Healthy
```

### Daily Limit Example

```
Daily limit: 4 plants
Plants watered today: 2
Remaining capacity: 2
```

The system ensures sustainable plant care while preventing overwatering and encouraging consistent care routines.
