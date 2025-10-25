"""
Example Python script for writing data to Supabase from Sierra Chart
This can be called from Sierra Chart ACSIL studies or run standalone
"""

from supabase import create_client, Client
import json
from datetime import datetime

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "your-anon-key-here"  # Replace with your actual anon key from Supabase Dashboard → Settings → API

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

        print(f"✅ Updated NQ alerts: {len(alerts_list)} alerts")
        return True
    except Exception as e:
        print(f"❌ Error updating NQ alerts: {e}")
        return False


def update_es_alerts(alerts_list):
    """Update ES alerts in Supabase"""
    try:
        response = supabase.table('alerts_es').upsert({
            'id': 1,
            'data': alerts_list
        }).execute()

        print(f"✅ Updated ES alerts: {len(alerts_list)} alerts")
        return True
    except Exception as e:
        print(f"❌ Error updating ES alerts: {e}")
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

        print(f"✅ Updated gap details: {len(gap_data_list)} records")
        return True
    except Exception as e:
        print(f"❌ Error updating gap details: {e}")
        return False


def update_ib_details(ib_data_list):
    """Update Initial Balance details in Supabase"""
    try:
        response = supabase.table('ib_details').upsert({
            'id': 1,
            'data': ib_data_list
        }).execute()

        print(f"✅ Updated IB details: {len(ib_data_list)} records")
        return True
    except Exception as e:
        print(f"❌ Error updating IB details: {e}")
        return False


def update_single_prints(single_prints_list):
    """Update single prints in Supabase"""
    try:
        response = supabase.table('single_prints').upsert({
            'id': 1,
            'data': single_prints_list
        }).execute()

        print(f"✅ Updated single prints: {len(single_prints_list)} records")
        return True
    except Exception as e:
        print(f"❌ Error updating single prints: {e}")
        return False


# Example usage
if __name__ == "__main__":
    # Example: Update NQ alerts
    sample_alerts = [
        {
            "timestamp": datetime.now().isoformat(),
            "symbol": "NQ",
            "type": "Test Alert",
            "priority": "info",
            "message": "This is a test alert from Python",
            "price": 20500.00
        }
    ]

    update_nq_alerts(sample_alerts)

    print("\n✅ Test complete! Check your Streamlit dashboard to see the alert.")
    print("💡 Tip: Run this script every second/minute from Sierra Chart to update in real-time")
