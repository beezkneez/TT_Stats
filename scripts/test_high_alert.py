"""
Test script to send a HIGH priority alert to Supabase
This will trigger the dashboard to show the alert and play 3 beeps
"""

from supabase import create_client, Client
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create HIGH priority test alert
high_alert = [
    {
        "timestamp": datetime.now().isoformat(),
        "symbol": "NQ",
        "type": "TEST - High Priority",
        "priority": "critical",
        "message": "🔴 HIGH PRIORITY TEST - You should hear 3 beeps!",
        "price": 20950.00
    }
]

try:
    response = supabase.table('alerts_nq').upsert({
        'id': 1,
        'data': high_alert
    }).execute()

    print("✅ HIGH priority alert sent to Supabase!")
    print("📊 Check your dashboard - you should see the alert and hear 3 beeps")
    print(f"⏰ Timestamp: {high_alert[0]['timestamp']}")

except Exception as e:
    print(f"❌ Error sending alert: {e}")
