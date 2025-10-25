"""
Example Python script for writing data to Supabase from Sierra Chart
This can be called from Sierra Chart ACSIL studies or run standalone
"""

from supabase import create_client, Client
import json
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"  # Replace with your actual anon key from Supabase Dashboard → Settings → API

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def update_nq_alerts(alerts_list):
    """
    Update NQ alerts in Supabase

    Args:
        alerts_list: List of alert dictionaries

    Example alert format:
    {
        "timestamp": "2025-10-25T14:35:22",
        "symbol": "NQ",
        "type": "IB Extension",
        "priority": "critical",
        "message": "30% IB extension reached",
        "price": 20565.00
    }
    """
    try:
        # Update the alerts (upsert = insert or update)
        response = supabase.table('alerts_nq').upsert({
            'id': 1,  # Always use ID 1 to update the same record
            'data': alerts_list
        }).execute()

        print(f"[OK] Updated NQ alerts: {len(alerts_list)} alerts")
        return True
    except Exception as e:
        print(f"[ERROR] Error updating NQ alerts: {e}")
        return False


def update_es_alerts(alerts_list):
    """Update ES alerts in Supabase"""
    try:
        response = supabase.table('alerts_es').upsert({
            'id': 1,
            'data': alerts_list
        }).execute()

        print(f"[OK] Updated ES alerts: {len(alerts_list)} alerts")
        return True
    except Exception as e:
        print(f"[ERROR] Error updating ES alerts: {e}")
        return False


def update_gap_details(gap_data_list):
    """
    Update gap details in Supabase

    Args:
        gap_data_list: List of gap data dictionaries
    """
    try:
        response = supabase.table('gap_details').upsert({
            'id': 1,
            'data': gap_data_list
        }).execute()

        print(f"[OK] Updated gap details: {len(gap_data_list)} records")
        return True
    except Exception as e:
        print(f"[ERROR] Error updating gap details: {e}")
        return False


def update_ib_details(ib_data_list):
    """Update Initial Balance details in Supabase"""
    try:
        response = supabase.table('ib_details').upsert({
            'id': 1,
            'data': ib_data_list
        }).execute()

        print(f"[OK] Updated IB details: {len(ib_data_list)} records")
        return True
    except Exception as e:
        print(f"[ERROR] Error updating IB details: {e}")
        return False


def update_single_prints(single_prints_list):
    """Update single prints in Supabase"""
    try:
        response = supabase.table('single_prints').upsert({
            'id': 1,
            'data': single_prints_list
        }).execute()

        print(f"[OK] Updated single prints: {len(single_prints_list)} records")
        return True
    except Exception as e:
        print(f"[ERROR] Error updating single prints: {e}")
        return False


# Example usage
if __name__ == "__main__":
    # Example: Update NQ alerts with multiple test alerts
    sample_alerts = [
        {
            "timestamp": datetime.now().isoformat(),
            "symbol": "NQ",
            "type": "Test Alert",
            "priority": "info",
            "message": "This is a test alert from Python",
            "price": 20500.00
        },
        {
            "timestamp": datetime.now().isoformat(),
            "symbol": "NQ",
            "type": "Prior Month High",
            "priority": "critical",
            "message": "NQ reached prior month high - potential resistance",
            "price": 21450.75
        },
        {
            "timestamp": datetime.now().isoformat(),
            "symbol": "NQ",
            "type": "IB Extension",
            "priority": "warning",
            "message": "30% IB extension reached - watch for reversal",
            "price": 20565.50
        }
    ]

    update_nq_alerts(sample_alerts)

    print("\n[OK] Test complete! Added 3 alerts to NQ feed.")
    print("[TIP] Run this script every second/minute from Sierra Chart to update in real-time")
