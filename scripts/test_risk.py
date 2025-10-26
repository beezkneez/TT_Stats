"""
Test script to populate Risk Assessment section with sample data
Run this to see the Risk Assessment section in action
"""

from supabase import create_client, Client
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample Risk Assessment data
risk_data = {
    "timestamp": datetime.now().isoformat(),
    "overall_risk_level": "medium",
    "risk_score": 6.5,
    "recommended_position_size": "50%",
    "factors": {
        "volatility_risk": {
            "level": "medium-high",
            "score": 7,
            "reason": "Rvol at 1.35 (72nd percentile) - elevated volatility"
        },
        "range_risk": {
            "level": "low",
            "score": 3,
            "reason": "Weekly range 303% of ATR - normal expansion"
        },
        "vix_risk": {
            "level": "medium",
            "score": 6,
            "reason": "VIX at 18.45 and rising - moderate fear"
        },
        "trend_risk": {
            "level": "high",
            "score": 8,
            "reason": "Choppy market - no clear trend"
        }
    },
    "recommendations": [
        "Consider smaller position sizes due to elevated Rvol",
        "Wait for clearer trend before increasing risk",
        "Use wider stops to accommodate volatility",
        "Focus on mean reversion strategies in choppy conditions"
    ],
    "suggested_strategies": [
        "Range trading",
        "Fade extremes",
        "Reduce directional bias"
    ]
}

try:
    response = supabase.table('risk_assessment').upsert({
        'id': 1,
        'data': risk_data
    }).execute()

    print("✅ Risk Assessment data sent to Supabase!")
    print("📊 Check your dashboard - you should see the Risk Assessment section")
    print(f"⚠️ Risk Level: {risk_data['overall_risk_level'].upper()}")
    print(f"📊 Risk Score: {risk_data['risk_score']}/10")
    print(f"💼 Recommended Position Size: {risk_data['recommended_position_size']}")

except Exception as e:
    print(f"❌ Error sending data: {e}")
