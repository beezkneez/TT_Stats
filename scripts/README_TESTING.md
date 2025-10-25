# Alert Testing Scripts

These scripts allow you to test the dashboard's alert system by sending test alerts to Supabase.

## 📋 Test Scripts

| Script | Priority | Sound | Description |
|--------|----------|-------|-------------|
| `test_high_alert.py` | 🔴 High (critical) | 3 beeps (1200Hz) | Tests critical/high priority alerts |
| `test_medium_alert.py` | 🟠 Medium (warning) | 2 beeps (800Hz) | Tests warning/medium priority alerts |
| `test_low_alert.py` | 🔵 Low (info) | 1 beep (500Hz) | Tests info/low priority alerts |

## 🚀 How to Use

### 1. Make sure you have the Supabase package installed:
```bash
pip install supabase
```

### 2. Run any test script:

**Test High Priority Alert:**
```bash
python scripts/test_high_alert.py
```

**Test Medium Priority Alert:**
```bash
python scripts/test_medium_alert.py
```

**Test Low Priority Alert:**
```bash
python scripts/test_low_alert.py
```

### 3. Check your dashboard:
- Open your Streamlit dashboard
- Make sure **Alert Sounds** are enabled in the sidebar
- You should see the test alert appear in the NQ Alerts section
- You should hear the corresponding beep pattern

## 📝 What Each Script Does

Each script:
1. Connects to Supabase using your credentials
2. Creates a test alert with the specified priority
3. Sends the alert to the `alerts_nq` table
4. The dashboard detects the new alert (cache refreshes every 1 second)
5. The alert appears in the dashboard
6. If sounds are enabled, you hear the corresponding beep pattern

## ⚠️ Notes

- Each script **replaces** all NQ alerts with just the test alert
- This is for testing only - in production, Deaner's scripts will append alerts
- The dashboard auto-refreshes every 1 second, so alerts appear quickly
- Make sure your dashboard has Alert Sounds enabled in the sidebar

## 🔧 Testing Flow

1. Open dashboard with sounds enabled
2. Run `python scripts/test_high_alert.py`
3. Wait 1-2 seconds
4. Should see alert + hear 3 beeps
5. Run `python scripts/test_medium_alert.py`
6. Should see new alert + hear 2 beeps
7. Run `python scripts/test_low_alert.py`
8. Should see new alert + hear 1 beep

## 🎯 Expected Behavior

- **High Priority (critical)**: Red alert tile, 3 beeps at high pitch
- **Medium Priority (warning)**: Orange alert tile, 2 beeps at medium pitch
- **Low Priority (info)**: Blue alert tile, 1 beep at low pitch
