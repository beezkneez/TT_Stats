"""
Test script to populate Single Prints section with sample data
Run this to see the Single Prints Analysis in action
"""

from supabase import create_client, Client
from datetime import datetime, timedelta

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample Single Prints data
single_prints_data = [
    # NQ Single Prints
    {
        "date_formed": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "price_level": 20880.00,
        "session": "RTH",
        "age_days": 0,
        "current_price": 20995.75,
        "distance_from_current": 115.75,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Below"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "price_level": 20882.50,
        "session": "RTH",
        "age_days": 0,
        "current_price": 20995.75,
        "distance_from_current": 113.25,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Below"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "price_level": 20885.00,
        "session": "RTH",
        "age_days": 0,
        "current_price": 20995.75,
        "distance_from_current": 110.75,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Below"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "price_level": 21085.25,
        "session": "RTH",
        "age_days": 1,
        "current_price": 20995.75,
        "distance_from_current": 89.50,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Above"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "price_level": 20750.50,
        "session": "RTH",
        "age_days": 2,
        "current_price": 20995.75,
        "distance_from_current": 245.25,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Below"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "price_level": 20950.00,
        "session": "RTH",
        "age_days": 3,
        "current_price": 20995.75,
        "distance_from_current": 45.75,
        "filled": True,
        "fill_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "fill_time_minutes": 2880,  # 2 days
        "direction_from_current": "Below"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "price_level": 20650.75,
        "session": "RTH",
        "age_days": 5,
        "current_price": 20995.75,
        "distance_from_current": 345.00,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Below"
    },
    # ES Single Prints
    {
        "date_formed": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "price_level": 5915.50,
        "session": "RTH",
        "age_days": 0,
        "current_price": 5952.75,
        "distance_from_current": 37.25,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Below"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "price_level": 5968.00,
        "session": "RTH",
        "age_days": 1,
        "current_price": 5952.75,
        "distance_from_current": 15.25,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Above"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "price_level": 5905.25,
        "session": "RTH",
        "age_days": 2,
        "current_price": 5952.75,
        "distance_from_current": 47.50,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Below"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "price_level": 5940.00,
        "session": "RTH",
        "age_days": 4,
        "current_price": 5952.75,
        "distance_from_current": 12.75,
        "filled": True,
        "fill_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "fill_time_minutes": 4320,  # 3 days
        "direction_from_current": "Below"
    }
]

try:
    response = supabase.table('single_prints').upsert({
        'id': 1,
        'data': single_prints_data
    }).execute()

    print("✅ Single Prints data sent to Supabase!")
    print(f"📊 Check your dashboard - you should see {len(single_prints_data)} single print entries")

    # Count unfilled prints
    unfilled = [sp for sp in single_prints_data if not sp['filled']]
    filled = [sp for sp in single_prints_data if sp['filled']]

    print(f"\n📈 Single Prints Summary:")
    print(f"   • Total: {len(single_prints_data)} prints")
    print(f"   • Unfilled: {len(unfilled)} prints (active)")
    print(f"   • Filled: {len(filled)} prints")

    print(f"\n🎯 Recent Unfilled Prints:")
    for sp in unfilled[:5]:
        direction = "↑" if sp['direction_from_current'] == "Above" else "↓"
        print(f"   {direction} {sp['symbol']} {sp['price_level']:,.2f} - Age: {sp['age_days']}d, Distance: {sp['distance_from_current']:.2f} pts")

except Exception as e:
    print(f"❌ Error sending data: {e}")
