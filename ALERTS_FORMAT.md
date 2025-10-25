# Real-Time Alerts JSON Format

## Overview
The dashboard reads real-time alerts from two separate JSON files:
- `alerts_nq.json` - NQ alerts
- `alerts_es.json` - ES alerts

These files are refreshed **every 1 second** by the dashboard (independent of the main 5-minute refresh).

## JSON Structure

Each alert file should contain an array of alert objects with the following fields:

```json
[
  {
    "timestamp": "2024-01-15T10:35:22",
    "symbol": "NQ",
    "type": "IB Extension",
    "priority": "critical",
    "message": "30% IB extension reached - Historical probability to 50%: 65%",
    "price": 16265.00
  }
]
```

## Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string | ISO 8601 timestamp | `"2024-01-15T10:35:22"` |
| `symbol` | string | Trading symbol | `"NQ"` or `"ES"` |
| `type` | string | Alert category | `"IB Extension"`, `"Gap Fill"`, etc. |
| `priority` | string | Alert level | `"critical"`, `"warning"`, or `"info"` |
| `message` | string | Alert description | Any descriptive text |

## Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `price` | number | Price level associated with alert | `16265.00` |

## Priority Levels

### Critical (Red)
Use for important trading signals that require immediate attention:
- IB extension milestones (30%, 50%, 100%)
- Major gap fills
- Single print fills near current price

### Warning (Yellow)
Use for notable events that may impact trading:
- Price approaching gap fill (within X points)
- IB forming (near 10:30 EST)
- Potential reversals

### Info (Blue)
Use for general market information:
- Market open/close
- New single prints forming
- Minor updates

## Alert Types

Suggested alert types (you can create your own):
- `"Market Open"` / `"Market Close"`
- `"Gap Fill"`
- `"IB Extension"`
- `"Single Print"`
- `"Price Level"`
- `"Custom Study"`

## Display Behavior

- Alerts are sorted by timestamp (newest first)
- Only alerts from the last **2 hours** are displayed
- Maximum **20 alerts** shown per symbol
- Alert counts are grouped by priority level

## Sierra Chart Integration

Your Sierra Chart ACSIL studies should:

1. **Append new alerts** to the appropriate JSON file (alerts_nq.json or alerts_es.json)
2. **Write complete array** on each update (overwrite the file)
3. **Use ISO 8601 timestamp format**: `YYYY-MM-DDTHH:MM:SS`
4. **Keep array size manageable** - suggest limiting to last 50-100 alerts

### Example Sierra Chart Workflow

```cpp
// Pseudocode for ACSIL study
void WriteAlert(const char* symbol, const char* type, const char* priority,
                const char* message, double price) {

    // 1. Read existing alerts from file
    // 2. Add new alert with current timestamp
    // 3. Keep only last 100 alerts
    // 4. Write complete array back to file
}
```

## Example Files

See `alerts_nq.json.example` and `alerts_es.json.example` for sample data.

## Testing

To test the dashboard with sample data:
1. Copy `alerts_nq.json.example` to `alerts_nq.json`
2. Copy `alerts_es.json.example` to `alerts_es.json`
3. Run the dashboard - alerts should appear in the Real-Time Alerts section
4. Modify the timestamps to current time to see "live" alerts

## Notes

- The dashboard caches alert data for only **1 second** (TTL=1)
- File I/O should be fast enough for 1-second updates
- Consider using file locking if writing from multiple studies
- JSON must be valid - invalid JSON will cause the alerts section to show "Waiting for alerts"
