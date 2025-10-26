"""
Test script to populate Initial Balance (IB) Details section with sample data
Run this to see the IB Extension Statistics in action
"""

from supabase import create_client, Client
from datetime import datetime, timedelta

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample IB Details data
ib_details_data = [
    # NQ IB Data
    {
        "date": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "ib_high": 20975.50,
        "ib_low": 20912.25,
        "ib_range": 63.25,
        "atr": 285.5,
        "ib_pct_atr": 22.15,
        "current_price": 20995.75,
        "extension_30_level": 20994.48,
        "extension_50_level": 21007.13,
        "extension_100_level": 21038.75,
        "current_extension_pct": 32.0,
        "reached_30": True,
        "reached_50": False,
        "reached_100": False,
        "time_to_30": 25,
        "time_to_50": None,
        "direction": "Up"
    },
    {
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "ib_high": 20850.00,
        "ib_low": 20795.75,
        "ib_range": 54.25,
        "atr": 280.3,
        "ib_pct_atr": 19.35,
        "current_price": 20928.50,
        "extension_30_level": 20866.28,
        "extension_50_level": 20877.13,
        "extension_100_level": 20904.25,
        "current_extension_pct": 145.2,
        "reached_30": True,
        "reached_50": True,
        "reached_100": True,
        "time_to_30": 18,
        "time_to_50": 42,
        "direction": "Up"
    },
    {
        "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "ib_high": 20725.50,
        "ib_low": 20682.25,
        "ib_range": 43.25,
        "atr": 275.8,
        "ib_pct_atr": 15.68,
        "current_price": 20715.00,
        "extension_30_level": 20738.48,
        "extension_50_level": 20747.13,
        "extension_100_level": 20768.75,
        "current_extension_pct": 0,
        "reached_30": False,
        "reached_50": False,
        "reached_100": False,
        "time_to_30": None,
        "time_to_50": None,
        "direction": "Contained"
    },
    {
        "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "ib_high": 20665.75,
        "ib_low": 20598.50,
        "ib_range": 67.25,
        "atr": 268.4,
        "ib_pct_atr": 25.06,
        "current_price": 20550.25,
        "extension_30_level": 20685.93,
        "extension_50_level": 20699.38,
        "extension_100_level": 20733.00,
        "current_extension_pct": 72.5,
        "reached_30": True,
        "reached_50": True,
        "reached_100": False,
        "time_to_30": 32,
        "time_to_50": 78,
        "direction": "Down"
    },
    # ES IB Data
    {
        "date": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "ib_high": 5945.50,
        "ib_low": 5930.25,
        "ib_range": 15.25,
        "atr": 45.35,
        "ib_pct_atr": 33.63,
        "current_price": 5952.75,
        "extension_30_level": 5950.08,
        "extension_50_level": 5953.13,
        "extension_100_level": 5960.75,
        "current_extension_pct": 47.5,
        "reached_30": True,
        "reached_50": False,
        "reached_100": False,
        "time_to_30": 22,
        "time_to_50": None,
        "direction": "Up"
    },
    {
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "ib_high": 5935.75,
        "ib_low": 5922.50,
        "ib_range": 13.25,
        "atr": 42.8,
        "ib_pct_atr": 30.96,
        "current_price": 5940.25,
        "extension_30_level": 5939.73,
        "extension_50_level": 5942.38,
        "extension_100_level": 5949.00,
        "current_extension_pct": 34.2,
        "reached_30": True,
        "reached_50": False,
        "reached_100": False,
        "time_to_30": 28,
        "time_to_50": None,
        "direction": "Up"
    },
    {
        "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "ib_high": 5920.25,
        "ib_low": 5908.75,
        "ib_range": 11.50,
        "atr": 41.2,
        "ib_pct_atr": 27.91,
        "current_price": 5916.50,
        "extension_30_level": 5923.70,
        "extension_50_level": 5926.00,
        "extension_100_level": 5931.75,
        "current_extension_pct": 0,
        "reached_30": False,
        "reached_50": False,
        "reached_100": False,
        "time_to_30": None,
        "time_to_50": None,
        "direction": "Contained"
    }
]

try:
    response = supabase.table('ib_details').upsert({
        'id': 1,
        'data': ib_details_data
    }).execute()

    print("✅ IB Details data sent to Supabase!")
    print(f"📊 Check your dashboard - you should see {len(ib_details_data)} IB entries")
    print("\n📈 Recent IB Data:")
    for ib in ib_details_data[:3]:
        ext_status = f"Reached {ib['current_extension_pct']:.0f}%" if ib['current_extension_pct'] > 0 else "Contained"
        print(f"   • {ib['symbol']} {ib['date']}: {ib['ib_range']:.2f} pts ({ib['ib_pct_atr']:.1f}% ATR) - {ext_status}")

except Exception as e:
    print(f"❌ Error sending data: {e}")
