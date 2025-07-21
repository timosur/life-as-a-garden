# Simplified Watering System

## Overview

The watering system has been redesigned with simplified, intuitive logic for plant health and size management. The system emphasizes clear timelines and predictable behavior, making garden management more enjoyable while still encouraging consistent care.

## Key Principles

- **Forgiving Grace Periods**: Plants have reasonable time before health/size decline
- **Clear Recovery Paths**: Simple, consistent requirements for plant improvement
- **Long-term Growth**: Plant maturity is based on total care over time
- **Predictable Timelines**: All changes follow logical, easy-to-understand schedules

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

- **Water streak**: Consecutive days of watering (resets after gap in watering)
- **Total water count**: Lifetime total of watering events
- **Growth stage**: 1-5 scale based on total water count (long-term care)

#### Health Recovery (with watering):

- **Dead → Okay**: Requires 3 consecutive days of watering
- **Dead → Healthy**: Requires 5 consecutive days of watering
- **Okay → Healthy**: Requires 3 consecutive days of watering
- **Healthy**: Stays healthy with any watering

#### Size Progression (with watering):

- **Dead plants**: Always remain small
- **Okay plants**:
  - Growth stage 3+: Medium size
  - Growth stage 1-2: Small size
- **Healthy plants**: Can reach full size potential:
  - Growth stage 4+: Big size
  - Growth stage 2-3: Medium size
  - Growth stage 1: Small size

#### Growth Stage Calculation:

Growth stages are based on total water count (long-term care):

- **Stage 1**: 1-4 total waters (new plants)
- **Stage 2**: 5-9 total waters (establishing)
- **Stage 3**: 10-14 total waters (developing)
- **Stage 4**: 15-19 total waters (mature)
- **Stage 5**: 20+ total waters (fully established)

### When Plants Are NOT Watered

Plants that aren't watered experience gradual decline:

#### Health Decline:

- **Healthy plants**: Stay healthy for 5 days, become "okay" after 6 days without water
- **Okay plants**: Become "dead" after 4 days without water
- **Dead plants**: Remain dead

#### Size Decline:

- **Big → Medium**: After 8 days without water
- **Medium → Small**: After 10 days without water
- **Small**: Stays small

#### Other Effects:

- **Water streak reset**: After 3 days without water
- **Days without water counter**: Increments daily for non-watered plants
- **Priority system**: Plants needing water are those with "okay"/"dead" health or 3+ days without water

## Examples

### Simplified Plant Care Journey

**New Plant (starting as "okay"):**

```
Day 1: Water → Health: okay, Size: small, Streak: 1, Growth: 1
Day 2: Water → Health: okay, Size: small, Streak: 2, Growth: 1
Day 3: Water → Health: healthy, Size: small, Streak: 3, Growth: 1
Day 4: Water → Health: healthy, Size: small, Streak: 4, Growth: 1
Day 5: Water → Health: healthy, Size: medium, Streak: 5, Growth: 2
```

**Plant Recovery from Dead:**

```
Dead plant + 3 consecutive days watering → Okay
Dead plant + 5 consecutive days watering → Healthy
Okay plant + 3 consecutive days watering → Healthy
```

**Plant Neglect Timeline:**

```
Healthy plant:
- Days 1-5: Stays healthy
- Day 6: Becomes okay
- Day 10: Becomes dead (if "okay" for 4 days)

Size decline:
- Big plant: Becomes medium after 8 days
- Medium plant: Becomes small after 10 days
```

### Daily Limit Example

```
Daily limit: 4 plants
Plants watered today: 2
Remaining capacity: 2
```

The system ensures sustainable plant care while preventing overwatering and encouraging consistent care routines.
