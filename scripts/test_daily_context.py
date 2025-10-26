"""
Test script to populate Daily Context section with sample data
Run this to see the Daily Context section in action
"""

from supabase import create_client, Client
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample Daily Context data
daily_context_data = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "generated_at": datetime.now().isoformat(),
    "symbol": "NQ",
    "timeframe_analysis": {
        "4hr": {
            "trend": "uptrend",
            "structure": "higher_highs_higher_lows",
            "key_levels": [21050.00, 20850.00],
            "bias": "bullish",
            "context": "4HR uptrend intact. Holding above 20850 keeps bullish structure."
        },
        "30min": {
            "trend": "consolidation",
            "structure": "range_bound",
            "key_levels": [20985.00, 20912.00],
            "bias": "neutral",
            "context": "30MIN consolidating in 20912-20985 range. Awaiting breakout direction."
        },
        "5min": {
            "trend": "sideways",
            "structure": "choppy",
            "bias": "reactive",
            "context": "5MIN choppy. React to Opening Range and IB for intraday direction."
        }
    },
    "overnight_analysis": {
        "gap_type": "gap_up",
        "gap_size": 45.50,
        "gap_pct_atr": 15.9,
        "overnight_high": 20965.00,
        "overnight_low": 20905.00,
        "overnight_range": 60.00,
        "context": "Small gap up, 15.9% of ATR. Moderate fill probability."
    },
    "key_scenarios": [
        {
            "name": "Bullish Continuation",
            "trigger": "Hold above IB high 20985",
            "target": "Yesterday's high 21050",
            "invalidation": "Break below OR low"
        },
        {
            "name": "Range Day",
            "trigger": "Reject IB high, hold IB low",
            "target": "Trade IB range 20912-20985",
            "invalidation": "Break either IB extreme"
        },
        {
            "name": "Reversal Lower",
            "trigger": "Break IB low 20912",
            "target": "Gap fill 20880, then 20850",
            "invalidation": "Reclaim IB low"
        }
    ],
    "critical_levels": {
        "resistance": [21100.00, 21050.00, 20985.00],
        "support": [20912.00, 20880.00, 20850.00],
        "key_level": 20950.00,
        "key_level_context": "Yesterday's POC and overnight consolidation area"
    },
    "market_environment": {
        "rvol": 1.35,
        "vix": 18.45,
        "regime": "normal",
        "expected_range": "285 points (1 ATR)"
    },
    "trading_plan": {
        "primary_focus": "Opening Range reaction and IB development",
        "risk_level": "medium",
        "position_sizing": "50% normal size due to elevated Rvol",
        "key_times": ["09:30 (Open)", "10:00 (OR close)", "10:30 (IB close)", "15:00 (Late session)"]
    }
}

try:
    response = supabase.table('daily_context').upsert({
        'id': 1,
        'data': daily_context_data
    }).execute()

    print("✅ Daily Context data sent to Supabase!")
    print("📊 Check your dashboard - you should see the Daily Context section populated")
    print(f"📅 Date: {daily_context_data['date']}")

except Exception as e:
    print(f"❌ Error sending data: {e}")
