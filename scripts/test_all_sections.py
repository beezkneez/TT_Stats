"""
Master test script to populate ALL dashboard sections with sample data
Run this to see the entire dashboard populated at once
"""

from supabase import create_client, Client
from datetime import datetime, timedelta

# Supabase Configuration
SUPABASE_URL = "https://tgphfdxcpstfqqxmeagh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRncGhmZHhjcHN0ZnFxeG1lYWdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTU2MDIsImV4cCI6MjA3Njk5MTYwMn0.Bz4JyDHHh7cB6SZIyyZpKE4gABIdJ6Am8VeRqtLW7A0"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🚀 Populating ALL dashboard sections with test data...\n")

# 1. Daily Context
daily_context_data = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "generated_at": datetime.now().isoformat(),
    "symbol": "NQ",
    "timeframe_analysis": {
        "4hr": {
            "trend": "uptrend",
            "structure": "higher_highs_higher_lows",
            "key_levels": [21050.00, 20850.00],
            "bias": "bullish",
            "context": "4HR uptrend intact. Holding above 20850 keeps bullish structure."
        },
        "30min": {
            "trend": "consolidation",
            "structure": "range_bound",
            "key_levels": [20985.00, 20912.00],
            "bias": "neutral",
            "context": "30MIN consolidating in 20912-20985 range. Awaiting breakout direction."
        },
        "5min": {
            "trend": "sideways",
            "structure": "choppy",
            "bias": "reactive",
            "context": "5MIN choppy. React to Opening Range and IB for intraday direction."
        }
    },
    "key_scenarios": [
        {
            "name": "Bullish Continuation",
            "trigger": "Hold above IB high 20985",
            "target": "Yesterday's high 21050",
            "invalidation": "Break below OR low"
        },
        {
            "name": "Range Day",
            "trigger": "Reject IB high, hold IB low",
            "target": "Trade IB range 20912-20985",
            "invalidation": "Break either IB extreme"
        }
    ],
    "critical_levels": {
        "resistance": [21100.00, 21050.00, 20985.00],
        "support": [20912.00, 20880.00, 20850.00],
        "key_level": 20950.00,
        "key_level_context": "Yesterday's POC and overnight consolidation area"
    },
    "market_environment": {
        "rvol": 1.35,
        "vix": 18.45,
        "regime": "normal",
        "expected_range": "285 points (1 ATR)"
    },
    "trading_plan": {
        "primary_focus": "Opening Range reaction and IB development",
        "risk_level": "medium",
        "position_sizing": "50% normal size",
        "key_times": ["09:30", "10:00", "10:30", "15:00"]
    }
}

try:
    supabase.table('daily_context').upsert({'id': 1, 'data': daily_context_data}).execute()
    print("✅ Daily Context")
except Exception as e:
    print(f"❌ Daily Context: {e}")

# 2. Market Environment
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
    supabase.table('market_environment').upsert({'id': 1, 'data': environment_data}).execute()
    print("✅ Market Environment")
except Exception as e:
    print(f"❌ Market Environment: {e}")

# 3. Risk Assessment
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
        "Use wider stops to accommodate volatility"
    ],
    "suggested_strategies": [
        "Range trading",
        "Fade extremes",
        "Reduce directional bias"
    ]
}

try:
    supabase.table('risk_assessment').upsert({'id': 1, 'data': risk_data}).execute()
    print("✅ Risk Assessment")
except Exception as e:
    print(f"❌ Risk Assessment: {e}")

# 4. Opening Range
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
    supabase.table('opening_range').upsert({'id': 1, 'data': opening_range_data}).execute()
    print("✅ Opening Range")
except Exception as e:
    print(f"❌ Opening Range: {e}")

# 5. 3-Stage Progression
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
    }
]

try:
    supabase.table('stage_progression').upsert({'id': 1, 'data': stage_progression_data}).execute()
    print("✅ 3-Stage Progression")
except Exception as e:
    print(f"❌ 3-Stage Progression: {e}")

# 6. TPO Profile
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
    "structure": {
        "single_prints_above": [],
        "single_prints_below": [20880.00, 20882.50, 20885.00],
        "poor_highs": [],
        "poor_lows": [20875.25]
    },
    "context": "Normal distribution day with P-shape. POC near IB midpoint.",
    "trading_implications": [
        "Value established 20915-20985",
        "POC acceptance at 20950 is key",
        "Poor low at 20875 - likely to fill"
    ]
}

try:
    supabase.table('tpo_profile').upsert({'id': 1, 'data': tpo_profile_data}).execute()
    print("✅ TPO Profile")
except Exception as e:
    print(f"❌ TPO Profile: {e}")

# 7. Gap Details
gap_details_data = [
    {
        "date": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "prior_day_high": 21050.00,
        "prior_day_low": 20875.25,
        "current_open": 20912.50,
        "gap_size": 37.25,
        "gap_fill_target": 21050.00,
        "atr": 285.5,
        "gap_pct_atr": 13.04,
        "category": "Small",
        "direction": "Down",
        "filled": False,
        "fill_time": None,
        "minutes_to_fill": None
    },
    {
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "prior_day_high": 20985.50,
        "prior_day_low": 20750.25,
        "current_open": 21025.75,
        "gap_size": 40.25,
        "gap_fill_target": 20985.50,
        "atr": 280.3,
        "gap_pct_atr": 14.36,
        "category": "Small",
        "direction": "Up",
        "filled": True,
        "fill_time": "09:45:00",
        "minutes_to_fill": 15
    },
    {
        "date": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "prior_day_high": 5950.50,
        "prior_day_low": 5910.25,
        "current_open": 5925.75,
        "gap_size": 15.25,
        "gap_fill_target": 5950.50,
        "atr": 45.35,
        "gap_pct_atr": 33.63,
        "category": "Medium",
        "direction": "Down",
        "filled": False,
        "fill_time": None,
        "minutes_to_fill": None
    }
]

try:
    supabase.table('gap_details').upsert({'id': 1, 'data': gap_details_data}).execute()
    print("✅ Gap Details")
except Exception as e:
    print(f"❌ Gap Details: {e}")

# 8. IB Details
ib_details_data = [
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
        "current_extension_pct": 145.2,
        "reached_30": True,
        "reached_50": True,
        "reached_100": True,
        "time_to_30": 18,
        "time_to_50": 42,
        "direction": "Up"
    },
    {
        "date": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "ib_high": 5945.50,
        "ib_low": 5930.25,
        "ib_range": 15.25,
        "atr": 45.35,
        "ib_pct_atr": 33.63,
        "current_price": 5952.75,
        "current_extension_pct": 47.5,
        "reached_30": True,
        "reached_50": False,
        "reached_100": False,
        "time_to_30": 22,
        "time_to_50": None,
        "direction": "Up"
    }
]

try:
    supabase.table('ib_details').upsert({'id': 1, 'data': ib_details_data}).execute()
    print("✅ IB Details")
except Exception as e:
    print(f"❌ IB Details: {e}")

# 9. Single Prints
single_prints_data = [
    {
        "date_formed": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "price_level": 20880.00,
        "session": "RTH",
        "age_days": 0,
        "current_price": 20995.75,
        "distance_from_current": 115.75,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Below"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "price_level": 21085.25,
        "session": "RTH",
        "age_days": 1,
        "current_price": 20995.75,
        "distance_from_current": 89.50,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Above"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "symbol": "NQ",
        "price_level": 20950.00,
        "session": "RTH",
        "age_days": 3,
        "current_price": 20995.75,
        "distance_from_current": 45.75,
        "filled": True,
        "fill_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "fill_time_minutes": 2880,
        "direction_from_current": "Below"
    },
    {
        "date_formed": (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d"),
        "symbol": "ES",
        "price_level": 5915.50,
        "session": "RTH",
        "age_days": 0,
        "current_price": 5952.75,
        "distance_from_current": 37.25,
        "filled": False,
        "fill_date": None,
        "fill_time_minutes": None,
        "direction_from_current": "Below"
    }
]

try:
    supabase.table('single_prints').upsert({'id': 1, 'data': single_prints_data}).execute()
    print("✅ Single Prints")
except Exception as e:
    print(f"❌ Single Prints: {e}")

print("\n" + "="*60)
print("🎉 All sections populated!")
print("📊 Check your dashboard - all 9 sections should now be visible")
print("="*60)
