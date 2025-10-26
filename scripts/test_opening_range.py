"""
Test script to populate Opening Range section with sample data
Run this to see the Opening Range section in action
"""

from supabase import create_client, Client
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample Opening Range data
opening_range_data = {
    "timestamp": datetime.now().isoformat(),
    "symbol": "NQ",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "start_time": "09:30:00",
    "end_time": "10:00:00",
    "high": 20975.50,
    "low": 20912.25,
    "range": 63.25,
    "atr_daily": 285.5,
    "range_pct_atr": 22.1,
    "open": 20925.00,
    "close_10am": 20965.75,
    "direction": "bullish",
    "status": "complete",
    "key_levels": {
        "or_high": 20975.50,
        "or_low": 20912.25,
        "or_mid": 20943.88
    },
    "context": "Narrow 30-min opening range at 22% of ATR. Bias: Test OR high for continuation."
}

try:
    response = supabase.table('opening_range').upsert({
        'id': 1,
        'data': opening_range_data
    }).execute()

    print("✅ Opening Range data sent to Supabase!")
    print("📊 Check your dashboard - you should see the Opening Range section")
    print(f"📈 OR High: {opening_range_data['high']:,.2f}")
    print(f"📉 OR Low: {opening_range_data['low']:,.2f}")
    print(f"📏 Range: {opening_range_data['range']:,.2f} ({opening_range_data['range_pct_atr']:.1f}% of ATR)")

except Exception as e:
    print(f"❌ Error sending data: {e}")
