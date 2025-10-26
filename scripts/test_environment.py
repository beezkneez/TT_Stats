"""
Test script to populate Market Environment section with sample data
Run this to see the Market Environment section in action
"""

from supabase import create_client, Client
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample Market Environment data
environment_data = {
    "timestamp": datetime.now().isoformat(),
    "symbol": "NQ",
    "volatility": {
        "rvol": 1.35,
        "rvol_percentile": 72,
        "atr_daily": 285.5,
        "atr_weekly": 412.3,
        "vix": 18.45,
        "vix_trend": "rising"
    },
    "range_metrics": {
        "weekly_range": 1250.75,
        "weekly_range_pct_atr": 3.03,
        "daily_range_avg_5d": 245.8,
        "current_day_range": 125.25,
        "range_expansion": False
    },
    "market_conditions": {
        "regime": "normal",
        "trend": "choppy",
        "volume_profile": "average"
    }
}

try:
    response = supabase.table('market_environment').upsert({
        'id': 1,
        'data': environment_data
    }).execute()

    print("✅ Market Environment data sent to Supabase!")
    print("📊 Check your dashboard - you should see the Environment section")
    print(f"📈 Rvol: {environment_data['volatility']['rvol']} ({environment_data['volatility']['rvol_percentile']}th percentile)")
    print(f"📊 VIX: {environment_data['volatility']['vix']} ({environment_data['volatility']['vix_trend']})")
    print(f"🎯 ATR Daily: {environment_data['volatility']['atr_daily']:,.1f}")

except Exception as e:
    print(f"❌ Error sending data: {e}")
