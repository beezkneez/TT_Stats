"""
Test script to populate 3-Stage Progression section with sample data
Run this to see the 3-Stage Progression Tracker in action
"""

from supabase import create_client, Client
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample 3-Stage Progression data
stage_progression_data = [
    {
        "level_name": "Yesterday's High",
        "price": 21050.00,
        "current_stage": 2,
        "stage_1_time": "2025-10-25T09:45:00",
        "stage_2_time": "2025-10-25T10:15:00",
        "stage_3_time": None,
        "status": "active",
        "direction": "testing_above",
        "distance_to_price": 75.50,
        "timeframe": "30MIN",
        "context": "Second test of yesterday's high. Watching for acceptance above."
    },
    {
        "level_name": "IB High",
        "price": 20985.75,
        "current_stage": 3,
        "stage_1_time": "2025-10-25T10:30:00",
        "stage_2_time": "2025-10-25T11:00:00",
        "stage_3_time": "2025-10-25T11:25:00",
        "status": "completed",
        "direction": "accepted_above",
        "distance_to_price": -9.75,
        "timeframe": "5MIN",
        "context": "IB high accepted. Now acting as support."
    },
    {
        "level_name": "Weekly VPOC",
        "price": 20900.00,
        "current_stage": 1,
        "stage_1_time": "2025-10-25T12:00:00",
        "stage_2_time": None,
        "stage_3_time": None,
        "status": "active",
        "direction": "testing_below",
        "distance_to_price": -75.50,
        "timeframe": "4HR",
        "context": "First touch of weekly VPOC from above. Key support level."
    }
]

try:
    response = supabase.table('stage_progression').upsert({
        'id': 1,
        'data': stage_progression_data
    }).execute()

    print("✅ 3-Stage Progression data sent to Supabase!")
    print("📊 Check your dashboard - you should see 3 levels being tracked")
    print(f"📈 Tracking {len(stage_progression_data)} levels:")
    for level in stage_progression_data:
        print(f"   • {level['level_name']} @ {level['price']:,.2f} - Stage {level['current_stage']}/3")

except Exception as e:
    print(f"❌ Error sending data: {e}")
