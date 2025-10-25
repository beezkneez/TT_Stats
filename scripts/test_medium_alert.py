"""
Test script to send a MEDIUM priority alert to Supabase
This will trigger the dashboard to show the alert and play 2 beeps
"""

from supabase import create_client, Client
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create MEDIUM priority test alert
medium_alert = [
    {
        "timestamp": datetime.now().isoformat(),
        "symbol": "NQ",
        "type": "TEST - Medium Priority",
        "priority": "warning",
        "message": "🟠 MEDIUM PRIORITY TEST - You should hear 2 beeps!",
        "price": 20925.00
    }
]

try:
    response = supabase.table('alerts_nq').upsert({
        'id': 1,
        'data': medium_alert
    }).execute()

    print("✅ MEDIUM priority alert sent to Supabase!")
    print("📊 Check your dashboard - you should see the alert and hear 2 beeps")
    print(f"⏰ Timestamp: {medium_alert[0]['timestamp']}")

except Exception as e:
    print(f"❌ Error sending alert: {e}")
