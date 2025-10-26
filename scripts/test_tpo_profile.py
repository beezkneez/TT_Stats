"""
Test script to populate TPO/Market Profile section with sample data
Run this to see the TPO Profile section in action
"""

from supabase import create_client, Client
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample TPO Profile data
tpo_profile_data = {
    "timestamp": datetime.now().isoformat(),
    "symbol": "NQ",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "session": "RTH",
    "profile_type": "Normal",
    "shape": "P-shaped",
    "poc": 20950.00,
    "value_area_high": 20985.00,
    "value_area_low": 20915.00,
    "value_area_pct": 70,
    "high": 21025.50,
    "low": 20875.25,
    "range": 150.25,
    "initial_balance_high": 20985.75,
    "initial_balance_low": 20912.25,
    "tpo_count": {
        "above_value": 8,
        "in_value": 24,
        "below_value": 6
    },
    "structure": {
        "single_prints_above": [],
        "single_prints_below": [20880.00, 20882.50, 20885.00],
        "poor_highs": [],
        "poor_lows": [20875.25]
    },
    "context": "Normal distribution day with P-shape. POC near IB midpoint. Single prints below value suggest unfinished business lower.",
    "trading_implications": [
        "Value established 20915-20985",
        "POC acceptance at 20950 is key",
        "Poor low at 20875 - likely to fill",
        "Single prints 20880-20885 - downside magnet"
    ]
}

try:
    response = supabase.table('tpo_profile').upsert({
        'id': 1,
        'data': tpo_profile_data
    }).execute()

    print("✅ TPO Profile data sent to Supabase!")
    print("📊 Check your dashboard - you should see the TPO Profile section")
    print(f"📈 Profile Type: {tpo_profile_data['profile_type']}")
    print(f"📊 Shape: {tpo_profile_data['shape']}")
    print(f"🎯 POC: {tpo_profile_data['poc']:,.2f}")
    print(f"📍 Value Area: {tpo_profile_data['value_area_low']:,.2f} - {tpo_profile_data['value_area_high']:,.2f}")

except Exception as e:
    print(f"❌ Error sending data: {e}")
