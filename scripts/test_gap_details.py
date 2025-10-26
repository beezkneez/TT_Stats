"""
Test script to populate Gap Details section with sample data
Run this to see the RTH Gap Statistics in action
"""

from supabase import create_client, Client
from datetime import datetime, timedelta

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample Gap Details data
gap_details_data = [
    # NQ Gaps
    {
        "date": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "prior_day_high": 21050.00,
        "prior_day_low": 20875.25,
        "current_open": 20912.50,
        "gap_size": 37.25,
        "gap_fill_target": 21050.00,
        "atr": 285.5,
        "gap_pct_atr": 13.04,
        "category": "Small",
        "direction": "Down",
        "pivot_high": 21050.00,
        "pivot_low": 20875.25,
        "range_position": "Within",
        "filled": False,
        "fill_time": None,
        "minutes_to_fill": None,
        "fill_bar_index": None
    },
    {
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "prior_day_high": 20985.50,
        "prior_day_low": 20750.25,
        "current_open": 21025.75,
        "gap_size": 40.25,
        "gap_fill_target": 20985.50,
        "atr": 280.3,
        "gap_pct_atr": 14.36,
        "category": "Small",
        "direction": "Up",
        "pivot_high": 20985.50,
        "pivot_low": 20750.25,
        "range_position": "Above",
        "filled": True,
        "fill_time": "09:45:00",
        "minutes_to_fill": 15,
        "fill_bar_index": 3
    },
    {
        "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "prior_day_high": 20850.00,
        "prior_day_low": 20650.75,
        "current_open": 21100.50,
        "gap_size": 250.50,
        "gap_fill_target": 20850.00,
        "atr": 275.8,
        "gap_pct_atr": 90.83,
        "category": "Extreme",
        "direction": "Up",
        "pivot_high": 20850.00,
        "pivot_low": 20650.75,
        "range_position": "Above",
        "filled": False,
        "fill_time": None,
        "minutes_to_fill": None,
        "fill_bar_index": None
    },
    {
        "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "prior_day_high": 20725.25,
        "prior_day_low": 20585.50,
        "current_open": 20775.00,
        "gap_size": 49.75,
        "gap_fill_target": 20725.25,
        "atr": 268.4,
        "gap_pct_atr": 18.54,
        "category": "Medium",
        "direction": "Up",
        "pivot_high": 20725.25,
        "pivot_low": 20585.50,
        "range_position": "Above",
        "filled": True,
        "fill_time": "10:15:00",
        "minutes_to_fill": 45,
        "fill_bar_index": 9
    },
    # ES Gaps
    {
        "date": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "prior_day_high": 5950.50,
        "prior_day_low": 5910.25,
        "current_open": 5925.75,
        "gap_size": 15.25,
        "gap_fill_target": 5950.50,
        "atr": 45.35,
        "gap_pct_atr": 33.63,
        "category": "Medium",
        "direction": "Down",
        "pivot_high": 5950.50,
        "pivot_low": 5910.25,
        "range_position": "Within",
        "filled": False,
        "fill_time": None,
        "minutes_to_fill": None,
        "fill_bar_index": None
    },
    {
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "prior_day_high": 5935.25,
        "prior_day_low": 5895.50,
        "current_open": 5945.00,
        "gap_size": 9.75,
        "gap_fill_target": 5935.25,
        "atr": 42.8,
        "gap_pct_atr": 22.78,
        "category": "Small",
        "direction": "Up",
        "pivot_high": 5935.25,
        "pivot_low": 5895.50,
        "range_position": "Above",
        "filled": True,
        "fill_time": "09:50:00",
        "minutes_to_fill": 20,
        "fill_bar_index": 4
    }
]

try:
    response = supabase.table('gap_details').upsert({
        'id': 1,
        'data': gap_details_data
    }).execute()

    print("✅ Gap Details data sent to Supabase!")
    print(f"📊 Check your dashboard - you should see {len(gap_details_data)} gap entries")
    print("\n📈 Recent Gaps:")
    for gap in gap_details_data[:3]:
        fill_status = "✓ Filled" if gap['filled'] else "○ Not Filled"
        print(f"   • {gap['symbol']} {gap['date']}: {gap['direction']} gap {gap['gap_size']:.2f} pts ({gap['category']}) - {fill_status}")

except Exception as e:
    print(f"❌ Error sending data: {e}")
