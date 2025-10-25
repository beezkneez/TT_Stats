import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, time, timedelta
import json
from pathlib import Path
import pytz
import base64

# Page config
st.set_page_config(
    page_title="NQ/ES Stats Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    """Initialize Supabase client with credentials from secrets"""
    try:
        from supabase import create_client, Client

        # Check if secrets exist
        if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
            st.warning("⚠️ Supabase credentials not configured. Using local JSON files.")
            return None

        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]

        if not url or not key:
            st.warning("⚠️ Supabase credentials are empty. Using local JSON files.")
            return None

        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Failed to connect to Supabase: {e}")
        return None

supabase = init_supabase()

# Initialize session state for section ordering
if 'section_order' not in st.session_state:
    st.session_state.section_order = ["Alerts", "Environment", "Risk Assessment", "Gap Stats", "Initial Balance", "Single Prints"]

# Initialize session state for dismissed alerts (user-specific, doesn't affect others)
if 'dismissed_alerts' not in st.session_state:
    st.session_state.dismissed_alerts = set()

# Initialize session state for alert sounds
if 'sound_enabled' not in st.session_state:
    st.session_state.sound_enabled = True

if 'seen_alerts' not in st.session_state:
    st.session_state.seen_alerts = set()

# Initialize session state for custom sound uploads
if 'custom_sounds' not in st.session_state:
    st.session_state.custom_sounds = {
        'high': None,
        'medium': None,
        'low': None
    }

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .block-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1f77b4;
    }
    .live-indicator {
        color: #00ff00;
        font-weight: bold;
        animation: blink 2s infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .stat-category {
        font-size: 0.9rem;
        padding: 0.2rem 0.6rem;
        border-radius: 0.3rem;
        font-weight: bold;
        display: inline-block;
    }
    .extreme { background-color: #d32f2f; color: white; }
    .medium { background-color: #f57c00; color: white; }
    .small { background-color: #fbc02d; color: black; }
    .micro { background-color: #388e3c; color: white; }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .alert-critical {
        background-color: rgba(211, 47, 47, 0.2);
        border-color: #d32f2f;
    }
    .alert-warning {
        background-color: rgba(245, 124, 0, 0.2);
        border-color: #f57c00;
    }
    .alert-info {
        background-color: rgba(33, 150, 243, 0.2);
        border-color: #2196f3;
    }
    .coming-soon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 0.5rem;
        text-align: center;
        color: white;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# DATA LOADING FUNCTIONS
# ========================================

@st.cache_data(ttl=5)  # Cache for 5 seconds (real-time data)
def load_gap_data(file_path):
    """Load gap details from Supabase or JSON file"""
    try:
        # Try Supabase first
        if supabase:
            response = supabase.table('gap_details').select('data').eq('id', 1).single().execute()
            data = response.data['data']
            if not data:  # Empty array
                return None
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            return df
    except Exception as e:
        st.warning(f"Supabase error, falling back to JSON: {e}")

    # Fallback to JSON file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if not data:
            return None
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        return None

@st.cache_data(ttl=5)  # Cache for 5 seconds (real-time data)
def load_ib_data(file_path):
    """Load Initial Balance data from Supabase or JSON file"""
    try:
        # Try Supabase first
        if supabase:
            response = supabase.table('ib_details').select('data').eq('id', 1).single().execute()
            data = response.data['data']
            if not data:  # Empty array
                return None
            return pd.DataFrame(data)
    except:
        pass

    # Fallback to JSON file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if not data:
            return None
        return pd.DataFrame(data)
    except:
        return None

@st.cache_data(ttl=5)  # Cache for 5 seconds (real-time data)
def load_single_prints_data(file_path):
    """Load Single Prints data from Supabase or JSON file"""
    try:
        # Try Supabase first
        if supabase:
            response = supabase.table('single_prints').select('data').eq('id', 1).single().execute()
            data = response.data['data']
            if not data:  # Empty array
                return None
            return pd.DataFrame(data)
    except:
        pass

    # Fallback to JSON file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if not data:
            return None
        return pd.DataFrame(data)
    except:
        return None

@st.cache_data(ttl=1)  # Refresh alerts every 1 second
def load_alerts_data(table_name):
    """Load real-time alerts from Supabase or JSON file"""
    try:
        # Try Supabase first
        if supabase:
            response = supabase.table(table_name).select('data').eq('id', 1).single().execute()
            data = response.data['data']
            if not data:  # Empty array
                return None
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
    except:
        pass

    # Fallback to JSON file
    file_path = f"{table_name}.json"
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if not data:
            return None
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except:
        return None

@st.cache_data(ttl=30)  # Refresh every 30 seconds
def load_environment_data(file_path):
    """Load Market Environment data from Supabase or JSON file"""
    try:
        # Try Supabase first
        if supabase:
            response = supabase.table('market_environment').select('data').eq('id', 1).single().execute()
            data = response.data['data']
            if not data:
                return None
            return data
    except:
        pass

    # Fallback to JSON file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data if data else None
    except:
        return None

@st.cache_data(ttl=60)  # Refresh every minute
def load_risk_assessment_data(file_path):
    """Load Risk Assessment data from Supabase or JSON file"""
    try:
        # Try Supabase first
        if supabase:
            response = supabase.table('risk_assessment').select('data').eq('id', 1).single().execute()
            data = response.data['data']
            if not data:
                return None
            return data
    except:
        pass

    # Fallback to JSON file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data if data else None
    except:
        return None

# ========================================
# UTILITY FUNCTIONS
# ========================================

def generate_alert_id(symbol, alert):
    """Generate a consistent unique ID for an alert"""
    # Use timestamp as string, type, and first 50 chars of message
    timestamp_str = str(alert['timestamp'])
    alert_type = alert.get('type', '')
    message = alert.get('message', '')[:50]  # First 50 chars to keep ID reasonable
    return f"{symbol}_{timestamp_str}_{alert_type}_{message}"

def check_and_play_alert_sounds(df, symbol):
    """Check for new alerts and play sounds if enabled"""
    if not st.session_state.sound_enabled or df is None or len(df) == 0:
        return

    # Check each alert to see if it's new
    new_alerts_by_priority = {'critical': 0, 'warning': 0, 'info': 0}

    for idx, alert in df.iterrows():
        alert_id = generate_alert_id(symbol, alert)

        # Skip dismissed alerts
        if alert_id in st.session_state.dismissed_alerts:
            continue

        # Check if this is a new alert
        if alert_id not in st.session_state.seen_alerts:
            st.session_state.seen_alerts.add(alert_id)
            priority = alert.get('priority', 'info')
            new_alerts_by_priority[priority] += 1

    # Play sounds for new alerts (play highest priority only to avoid noise)
    sound_to_play = None
    if new_alerts_by_priority['critical'] > 0:
        sound_to_play = 'critical'
    elif new_alerts_by_priority['warning'] > 0:
        sound_to_play = 'warning'
    elif new_alerts_by_priority['info'] > 0:
        sound_to_play = 'info'

    if sound_to_play:
        # Play sound using self-contained component
        components.html(f"""
            <script>
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();

                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);

                const priority = '{sound_to_play}';

                if (priority === 'critical') {{
                    oscillator.frequency.value = 1200;
                    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);
                    oscillator.start(audioContext.currentTime);
                    oscillator.stop(audioContext.currentTime + 0.15);

                    setTimeout(() => {{
                        const osc2 = audioContext.createOscillator();
                        const gain2 = audioContext.createGain();
                        osc2.connect(gain2);
                        gain2.connect(audioContext.destination);
                        osc2.frequency.value = 1200;
                        gain2.gain.setValueAtTime(0.3, audioContext.currentTime);
                        gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);
                        osc2.start(audioContext.currentTime);
                        osc2.stop(audioContext.currentTime + 0.15);
                    }}, 200);

                    setTimeout(() => {{
                        const osc3 = audioContext.createOscillator();
                        const gain3 = audioContext.createGain();
                        osc3.connect(gain3);
                        gain3.connect(audioContext.destination);
                        osc3.frequency.value = 1200;
                        gain3.gain.setValueAtTime(0.3, audioContext.currentTime);
                        gain3.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);
                        osc3.start(audioContext.currentTime);
                        osc3.stop(audioContext.currentTime + 0.15);
                    }}, 400);

                }} else if (priority === 'warning') {{
                    oscillator.frequency.value = 800;
                    gainNode.gain.setValueAtTime(0.25, audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.12);
                    oscillator.start(audioContext.currentTime);
                    oscillator.stop(audioContext.currentTime + 0.12);

                    setTimeout(() => {{
                        const osc2 = audioContext.createOscillator();
                        const gain2 = audioContext.createGain();
                        osc2.connect(gain2);
                        gain2.connect(audioContext.destination);
                        osc2.frequency.value = 800;
                        gain2.gain.setValueAtTime(0.25, audioContext.currentTime);
                        gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.12);
                        osc2.start(audioContext.currentTime);
                        osc2.stop(audioContext.currentTime + 0.12);
                    }}, 180);

                }} else {{
                    oscillator.frequency.value = 500;
                    gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
                    oscillator.start(audioContext.currentTime);
                    oscillator.stop(audioContext.currentTime + 0.1);
                }}
            </script>
        """, height=0)

def get_current_market_status():
    """Check if market is currently open (9:30 AM - 4:00 PM EST)"""
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)

    market_open = time(9, 30)
    market_close = time(16, 0)

    is_weekday = now.weekday() < 5
    is_market_hours = market_open <= now.time() <= market_close

    return is_weekday and is_market_hours, now

def calculate_gap_stats(df, category=None, direction=None, days=252):
    """Calculate gap fill statistics"""
    filtered_df = df.copy()

    if category:
        filtered_df = filtered_df[filtered_df['category'] == category]
    if direction:
        filtered_df = filtered_df[filtered_df['direction'] == direction]

    if len(filtered_df) > days:
        filtered_df = filtered_df.tail(days)

    if len(filtered_df) == 0:
        return None

    total_gaps = len(filtered_df)
    filled_gaps = filtered_df['filled'].sum()
    fill_rate = (filled_gaps / total_gaps * 100) if total_gaps > 0 else 0

    filled_df = filtered_df[filtered_df['filled'] == True]
    avg_time_to_fill = filled_df['minutes_to_fill'].mean() if len(filled_df) > 0 else None

    return {
        'total_gaps': total_gaps,
        'filled_gaps': filled_gaps,
        'fill_rate': fill_rate,
        'avg_time_to_fill': avg_time_to_fill
    }

# ========================================
# BLOCK 1: RTH GAP STATS
# ========================================

def render_gap_block(df):
    """Render the RTH Gap Statistics block"""
    st.markdown('<div class="block-header">📈 RTH Gap Statistics</div>', unsafe_allow_html=True)

    if df is None or len(df) == 0:
        st.warning("No gap data available")
        return

    # Get today's gap
    latest_date = df['date'].max()
    today_data = df[df['date'] == latest_date].iloc[0]

    # Today's gap metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        direction_color = "🟢" if today_data['direction'] == "Up" else "🔴"
        st.metric(
            "Gap Direction",
            f"{direction_color} {today_data['direction']}",
            delta=f"{today_data['gap_size']:.2f} pts"
        )

    with col2:
        category_class = today_data['category'].lower()
        st.markdown("**Gap Category**")
        st.markdown(f'<span class="stat-category {category_class}">{today_data["category"]}</span>',
                    unsafe_allow_html=True)
        st.caption(f"{today_data['gap_pct_atr']:.1f}% of ATR")

    with col3:
        st.metric("ATR", f"{today_data['atr']:.2f}")

    with col4:
        st.metric("Gap Fill Target", f"{today_data['gap_fill_target']:.2f}")

    with col5:
        fill_status = "✅ Filled" if today_data['filled'] else "⏳ Open"
        fill_time = f"{today_data['minutes_to_fill']} min" if today_data['filled'] and today_data['minutes_to_fill'] else None
        st.metric("Fill Status", fill_status, delta=fill_time)

    st.markdown("---")

    # Historical stats for similar gaps
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Similar Gaps ({today_data['category']} {today_data['direction']})**")
        similar_stats = calculate_gap_stats(
            df[df['date'] < df['date'].max()],
            category=today_data['category'],
            direction=today_data['direction']
        )

        if similar_stats:
            subcol1, subcol2, subcol3 = st.columns(3)
            subcol1.metric("Total", similar_stats['total_gaps'])
            subcol2.metric("Fill Rate", f"{similar_stats['fill_rate']:.1f}%")
            if similar_stats['avg_time_to_fill']:
                subcol3.metric("Avg Time", f"{similar_stats['avg_time_to_fill']:.0f} min")

    with col2:
        st.markdown("**All Gaps (Last 252 Days)**")
        all_stats = calculate_gap_stats(df[df['date'] < df['date'].max()])

        if all_stats:
            subcol1, subcol2, subcol3 = st.columns(3)
            subcol1.metric("Total", all_stats['total_gaps'])
            subcol2.metric("Fill Rate", f"{all_stats['fill_rate']:.1f}%")
            if all_stats['avg_time_to_fill']:
                subcol3.metric("Avg Time", f"{all_stats['avg_time_to_fill']:.0f} min")

    # Mini visualization
    with st.expander("📊 View Gap Analytics"):
        tab1, tab2 = st.tabs(["Fill Rate by Category", "Direction Analysis"])

        with tab1:
            category_stats = df.groupby('category').agg({
                'filled': ['count', 'mean']
            }).reset_index()
            category_stats.columns = ['Category', 'Total', 'Fill_Rate']
            category_stats['Fill_Rate'] = category_stats['Fill_Rate'] * 100

            fig = go.Figure(data=[
                go.Bar(x=category_stats['Category'],
                       y=category_stats['Fill_Rate'],
                       marker_color=['#388e3c', '#fbc02d', '#f57c00', '#d32f2f'],
                       text=category_stats['Fill_Rate'].round(1),
                       texttemplate='%{text}%')
            ])
            fig.update_layout(template="plotly_dark", height=300,
                            title="Fill Rate by Category",
                            yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            direction_stats = df.groupby('direction')['filled'].mean() * 100
            fig = go.Figure(data=[
                go.Bar(x=direction_stats.index,
                       y=direction_stats.values,
                       marker_color=['#ff0000', '#00ff00'],
                       text=direction_stats.values.round(1),
                       texttemplate='%{text}%')
            ])
            fig.update_layout(template="plotly_dark", height=300,
                            title="Fill Rate by Direction",
                            yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)

# ========================================
# BLOCK 2: INITIAL BALANCE STATS
# ========================================

def render_ib_block(df):
    """Render the Initial Balance Statistics block"""
    st.markdown('<div class="block-header">⏰ Initial Balance (9:30-10:30 EST)</div>', unsafe_allow_html=True)

    if df is None or len(df) == 0:
        st.markdown('<div class="coming-soon">🚧 Coming Soon<br><small>Waiting for IB data feed from Sierra Chart</small></div>',
                   unsafe_allow_html=True)
        return

    # Get today's IB data (most recent)
    today_ib = df.iloc[0]

    # Today's IB metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("IB Range", f"{today_ib['ib_range']:.2f} pts",
                 delta=f"{today_ib['ib_pct_atr']:.1f}% of ATR")

    with col2:
        st.metric("IB High", f"{today_ib['ib_high']:.2f}")
        st.caption(f"Low: {today_ib['ib_low']:.2f}")

    with col3:
        extension_pct = today_ib.get('current_extension_pct', 0)
        st.metric("Current Extension", f"{extension_pct:.1f}%")

    with col4:
        direction = today_ib.get('direction', 'N/A')
        direction_emoji = "🟢" if direction == "Up" else "🔴" if direction == "Down" else "⚪"
        st.metric("Direction", f"{direction_emoji} {direction}")

    st.markdown("---")

    # Extension levels
    col1, col2, col3 = st.columns(3)

    with col1:
        reached_30 = "✅" if today_ib.get('reached_30', False) else "⏳"
        st.markdown(f"**30% Extension** {reached_30}")
        st.caption(f"Level: {today_ib.get('extension_30_level', 0):.2f}")
        if today_ib.get('time_to_30'):
            st.caption(f"Time: {today_ib['time_to_30']} min")

    with col2:
        reached_50 = "✅" if today_ib.get('reached_50', False) else "⏳"
        st.markdown(f"**50% Extension** {reached_50}")
        st.caption(f"Level: {today_ib.get('extension_50_level', 0):.2f}")
        if today_ib.get('time_to_50'):
            st.caption(f"Time: {today_ib['time_to_50']} min")

    with col3:
        reached_100 = "✅" if today_ib.get('reached_100', False) else "⏳"
        st.markdown(f"**100% Extension** {reached_100}")
        st.caption(f"Level: {today_ib.get('extension_100_level', 0):.2f}")

    # Historical data
    with st.expander("📊 View Historical IB Data"):
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)

# ========================================
# BLOCK 3: SINGLE PRINTS
# ========================================

def render_single_prints_block(df):
    """Render the Single Prints Statistics block"""
    st.markdown('<div class="block-header">📍 Single Prints Analysis</div>', unsafe_allow_html=True)

    if df is None or len(df) == 0:
        st.markdown('<div class="coming-soon">🚧 Coming Soon<br><small>Waiting for single prints data feed</small></div>',
                   unsafe_allow_html=True)
        return

    # Filter active (unfilled) single prints
    active_prints = df[df['filled'] == False].copy()
    filled_prints = df[df['filled'] == True].copy()

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Active Single Prints", len(active_prints))

    with col2:
        st.metric("Filled (Recent)", len(filled_prints))

    with col3:
        if len(active_prints) > 0:
            avg_age = active_prints['age_days'].mean()
            st.metric("Avg Age", f"{avg_age:.1f} days")

    st.markdown("---")

    # Active single prints table
    if len(active_prints) > 0:
        st.markdown("### 🎯 Active Single Prints")

        # Format for display - sort BEFORE renaming columns
        display_df = active_prints[['symbol', 'price_level', 'age_days', 'distance_from_current', 'direction_from_current']].copy()
        display_df = display_df.sort_values('distance_from_current').head(10)
        display_df.columns = ['Symbol', 'Price Level', 'Age (days)', 'Distance', 'Direction']

        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No active single prints")

    # Recently filled prints
    if len(filled_prints) > 0:
        with st.expander("✅ Recently Filled Single Prints"):
            filled_df = filled_prints[['symbol', 'price_level', 'fill_date', 'fill_time_minutes']].copy()
            filled_df.columns = ['Symbol', 'Price Level', 'Fill Date', 'Time to Fill (min)']
            st.dataframe(filled_df.head(10), use_container_width=True, hide_index=True)

# ========================================
# BLOCK 4: MARKET ENVIRONMENT
# ========================================

def render_environment_block(data):
    """Render the Market Environment block"""
    st.markdown('<div class="block-header">🌡️ Market Environment</div>', unsafe_allow_html=True)

    if data is None:
        st.warning("No environment data available")
        return

    # Display timestamp
    est = pytz.timezone('US/Eastern')
    timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    if timestamp.tzinfo is None:
        timestamp = est.localize(timestamp)
    st.caption(f"Last updated: {timestamp.strftime('%I:%M:%S %p')} EST | Symbol: {data.get('symbol', 'NQ')}")

    # Volatility Metrics
    st.markdown("### 📊 Volatility Metrics")
    vol = data.get('volatility', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        rvol = vol.get('rvol', 0)
        rvol_pct = vol.get('rvol_percentile', 0)
        delta_color = "normal" if rvol < 1.2 else "inverse"
        st.metric(
            "Realized Vol (Rvol)",
            f"{rvol:.2f}",
            delta=f"{rvol_pct}th percentile",
            delta_color=delta_color
        )

    with col2:
        atr_daily = vol.get('atr_daily', 0)
        st.metric("ATR (Daily)", f"{atr_daily:.1f} pts")

    with col3:
        vix = vol.get('vix', 0)
        vix_trend = vol.get('vix_trend', 'stable')
        trend_emoji = "📈" if vix_trend == "rising" else "📉" if vix_trend == "falling" else "➡️"
        st.metric("VIX", f"{vix:.2f}", delta=f"{trend_emoji} {vix_trend}")

    with col4:
        atr_weekly = vol.get('atr_weekly', 0)
        st.metric("ATR (Weekly)", f"{atr_weekly:.1f} pts")

    st.markdown("---")

    # Range Metrics
    st.markdown("### 📏 Range Metrics")
    range_data = data.get('range_metrics', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        weekly_range = range_data.get('weekly_range', 0)
        weekly_pct = range_data.get('weekly_range_pct_atr', 0)
        st.metric(
            "Weekly Range",
            f"{weekly_range:.1f} pts",
            delta=f"{weekly_pct:.1f}x ATR"
        )

    with col2:
        daily_avg = range_data.get('daily_range_avg_5d', 0)
        st.metric("5-Day Avg Range", f"{daily_avg:.1f} pts")

    with col3:
        current_range = range_data.get('current_day_range', 0)
        st.metric("Today's Range", f"{current_range:.1f} pts")

    with col4:
        expansion = range_data.get('range_expansion', False)
        status = "✅ Expanding" if expansion else "📊 Normal"
        st.metric("Range Status", status)

    st.markdown("---")

    # Market Conditions
    st.markdown("### 🎯 Market Conditions")
    conditions = data.get('market_conditions', {})

    col1, col2, col3 = st.columns(3)

    with col1:
        regime = conditions.get('regime', 'unknown')
        regime_emoji = {"normal": "📊", "high_vol": "⚡", "low_vol": "😴"}.get(regime, "❓")
        st.markdown(f"**Regime:** {regime_emoji} {regime.title()}")

    with col2:
        trend = conditions.get('trend', 'unknown')
        trend_emoji = {"trending": "📈", "choppy": "〰️", "ranging": "↔️"}.get(trend, "❓")
        st.markdown(f"**Trend:** {trend_emoji} {trend.title()}")

    with col3:
        volume = conditions.get('volume_profile', 'unknown')
        vol_emoji = {"high": "🔊", "average": "🔉", "low": "🔈"}.get(volume, "❓")
        st.markdown(f"**Volume:** {vol_emoji} {volume.title()}")

# ========================================
# BLOCK 5: RISK ASSESSMENT
# ========================================

def render_risk_assessment_block(data):
    """Render the Risk Assessment block"""
    st.markdown('<div class="block-header">⚠️ Risk Assessment</div>', unsafe_allow_html=True)

    if data is None:
        st.warning("No risk assessment data available")
        return

    # Display timestamp
    est = pytz.timezone('US/Eastern')
    timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    if timestamp.tzinfo is None:
        timestamp = est.localize(timestamp)
    st.caption(f"Last updated: {timestamp.strftime('%I:%M:%S %p')} EST")

    # Overall Risk Level
    risk_level = data.get('overall_risk_level', 'unknown')
    risk_score = data.get('risk_score', 0)

    # Color coding
    risk_colors = {
        'low': ('#388e3c', '🟢'),
        'medium': ('#f57c00', '🟡'),
        'medium-high': ('#ff6f00', '🟠'),
        'high': ('#d32f2f', '🔴'),
        'extreme': ('#b71c1c', '🔴🔴')
    }
    color, emoji = risk_colors.get(risk_level, ('#757575', '⚪'))

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"""
            <div style="background: {color}; padding: 20px; border-radius: 10px; text-align: center;">
                <h2 style="color: white; margin: 0;">{emoji} {risk_level.upper()}</h2>
                <p style="color: white; margin: 5px 0 0 0; font-size: 24px;">{risk_score}/10</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        recommended_size = data.get('recommended_position_size', 'N/A')
        st.markdown(f"### Recommended Position Size: **{recommended_size}**")
        st.caption("Based on current market conditions and volatility")

    st.markdown("---")

    # Risk Factors
    st.markdown("### 📋 Risk Factors")
    factors = data.get('factors', {})

    for factor_name, factor_data in factors.items():
        level = factor_data.get('level', 'unknown')
        score = factor_data.get('score', 0)
        reason = factor_data.get('reason', '')

        # Progress bar color based on score
        progress_color = "#388e3c" if score <= 3 else "#f57c00" if score <= 6 else "#d32f2f"

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**{factor_name.replace('_', ' ').title()}**")
            st.progress(score / 10)
        with col2:
            st.markdown(f"*{level.upper()}* ({score}/10)")
            st.caption(reason)

    st.markdown("---")

    # Recommendations
    st.markdown("### 💡 Recommendations")
    recommendations = data.get('recommendations', [])

    for rec in recommendations:
        st.markdown(f"• {rec}")

    # Suggested Strategies
    if 'suggested_strategies' in data:
        st.markdown("### 🎯 Suggested Strategies")
        strategies = data.get('suggested_strategies', [])
        cols = st.columns(len(strategies))
        for idx, strategy in enumerate(strategies):
            with cols[idx]:
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                padding: 10px; border-radius: 5px; text-align: center; color: white;">
                        {strategy}
                    </div>
                """, unsafe_allow_html=True)

# ========================================
# BLOCK 6: REAL-TIME ALERTS
# ========================================

def render_alerts_block():
    """Render the Real-Time Alerts block from Sierra Chart studies with NQ/ES side-by-side"""
    st.markdown('<div class="block-header">🚨 Real-Time Alerts</div>', unsafe_allow_html=True)

    # Current time display
    is_live, current_time = get_current_market_status()
    st.caption(f"Last updated: {current_time.strftime('%I:%M:%S %p')} EST")

    # Side-by-side columns for NQ and ES
    col_nq, col_es = st.columns(2)

    # NQ Column (Left)
    with col_nq:
        # Header with Clear All button
        col_header, col_btn = st.columns([3, 1])
        with col_header:
            st.markdown("### 📊 NQ Alerts")
        with col_btn:
            if st.button("🗑️ Clear All", key="clear_nq", help="Clear all NQ alerts (only for you)", use_container_width=True):
                # Mark all current NQ alerts as dismissed
                nq_data = load_alerts_data("alerts_nq")
                if nq_data is not None:
                    for idx, alert in nq_data.iterrows():
                        alert_id = generate_alert_id("NQ", alert)
                        st.session_state.dismissed_alerts.add(alert_id)
                st.rerun()

        nq_alerts = load_alerts_data("alerts_nq")
        check_and_play_alert_sounds(nq_alerts, "NQ")
        render_alert_feed(nq_alerts, "NQ")

    # ES Column (Right)
    with col_es:
        # Header with Clear All button
        col_header, col_btn = st.columns([3, 1])
        with col_header:
            st.markdown("### 📊 ES Alerts")
        with col_btn:
            if st.button("🗑️ Clear All", key="clear_es", help="Clear all ES alerts (only for you)", use_container_width=True):
                # Mark all current ES alerts as dismissed
                es_data = load_alerts_data("alerts_es")
                if es_data is not None:
                    for idx, alert in es_data.iterrows():
                        alert_id = generate_alert_id("ES", alert)
                        st.session_state.dismissed_alerts.add(alert_id)
                st.rerun()

        es_alerts = load_alerts_data("alerts_es")
        check_and_play_alert_sounds(es_alerts, "ES")
        render_alert_feed(es_alerts, "ES")

def render_alert_feed(df, symbol):
    """Render alert feed for a specific symbol"""
    if df is None:
        st.info(f"⏳ Waiting for {symbol} alerts")
        return

    # Make timestamp timezone-aware if it isn't already
    est = pytz.timezone('US/Eastern')
    if df['timestamp'].dt.tz is None:
        df['timestamp'] = df['timestamp'].dt.tz_localize(est)

    # Filter to recent alerts (last 2 hours), or show all if none recent
    two_hours_ago = datetime.now(est) - timedelta(hours=2)
    recent_alerts = df[df['timestamp'] > two_hours_ago].sort_values('timestamp', ascending=False)

    # If no recent alerts, show last 15 alerts anyway (for demo/testing)
    if len(recent_alerts) == 0:
        recent_alerts = df.sort_values('timestamp', ascending=False).head(15)
        st.caption(f"ℹ️ No alerts in last 2 hours - showing most recent {len(recent_alerts)}")

    # Filter out dismissed alerts (user-specific)
    filtered_alerts = []
    for idx, alert in recent_alerts.iterrows():
        alert_id = generate_alert_id(symbol, alert)
        if alert_id not in st.session_state.dismissed_alerts:
            filtered_alerts.append((alert_id, alert))

    recent_alerts = pd.DataFrame([alert for _, alert in filtered_alerts])

    if len(recent_alerts) == 0:
        st.info(f"No {symbol} alerts available")
        return

    # Alert count metrics - more compact for side-by-side (count only non-dismissed)
    critical_count = 0
    warning_count = 0
    info_count = 0

    for _, alert in filtered_alerts:
        priority = alert.get('priority', 'info')
        if priority == 'critical':
            critical_count += 1
        elif priority == 'warning':
            warning_count += 1
        else:
            info_count += 1

    st.caption(f"🔴 {critical_count} | 🟡 {warning_count} | 🔵 {info_count} | Total: {len(filtered_alerts)}")
    st.markdown("---")

    # Display alerts - more compact with X button
    for alert_id, alert in filtered_alerts[:15]:
        alert_class = {
            'critical': 'alert-critical',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }.get(alert.get('priority', 'info'), 'alert-info')

        price_info = f" @ ${alert['price']:.2f}" if 'price' in alert else ""

        # Use columns for alert content and dismiss button
        col_alert, col_dismiss = st.columns([10, 1])

        with col_alert:
            st.markdown(f"""
            <div class="alert-box {alert_class}">
                <strong>{alert['timestamp'].strftime('%I:%M:%S')}</strong> - {alert.get('type', 'Alert')}{price_info}<br>
                <small>{alert.get('message', 'No message')}</small>
            </div>
            """, unsafe_allow_html=True)

        with col_dismiss:
            # Small X button to dismiss individual alert
            if st.button("×", key=f"dismiss_{alert_id}", help="Dismiss this alert"):
                st.session_state.dismissed_alerts.add(alert_id)
                st.rerun()

    # Show alert count
    if len(filtered_alerts) > 15:
        st.caption(f"Showing 15 of {len(filtered_alerts)} alerts (last 2 hrs)")

# ========================================
# MAIN APP
# ========================================

def main():
    st.markdown('<h1 class="main-header">NQ/ES Trading Stats Dashboard</h1>', unsafe_allow_html=True)

    # Top status bar
    col1, col2, col3 = st.columns([2, 1, 1])
    is_live, current_time = get_current_market_status()

    with col1:
        st.markdown(f"### 📅 {current_time.strftime('%A, %B %d, %Y')}")
    with col2:
        if is_live:
            st.markdown('<span class="live-indicator">🔴 MARKET OPEN</span>', unsafe_allow_html=True)
        else:
            st.markdown("⚪ **Market Closed**")
    with col3:
        st.markdown(f"**{current_time.strftime('%I:%M:%S %p')} EST**")

    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")

        # Sound toggle
        st.session_state.sound_enabled = st.checkbox(
            "🔊 Alert Sounds",
            value=st.session_state.sound_enabled,
            help="Play sounds when new alerts arrive (different tones for each priority)"
        )

        # Test sound buttons
        if st.session_state.sound_enabled:
            st.caption("Test Sounds:")

            # Self-contained HTML component with sounds
            # Inject custom sounds as base64 data
            custom_sounds_js = f"""
                const customSounds = {{
                    high: {'`data:audio/mp3;base64,' + st.session_state.custom_sounds['high'] + '`' if st.session_state.custom_sounds['high'] else 'null'},
                    medium: {'`data:audio/mp3;base64,' + st.session_state.custom_sounds['medium'] + '`' if st.session_state.custom_sounds['medium'] else 'null'},
                    low: {'`data:audio/mp3;base64,' + st.session_state.custom_sounds['low'] + '`' if st.session_state.custom_sounds['low'] else 'null'}
                }};
            """

            components.html(f"""
                <style>
                    .sound-btn {
                        border: none;
                        padding: 10px;
                        border-radius: 4px;
                        cursor: pointer;
                        width: 32%;
                        font-size: 11px;
                        color: white;
                        margin: 1px;
                        font-weight: bold;
                    }
                    .btn-high { background: #d32f2f; }
                    .btn-medium { background: #ff9800; }
                    .btn-low { background: #2196f3; }
                </style>

                <div style="text-align: center; display: flex; gap: 2px; justify-content: space-between;">
                    <button class="sound-btn btn-high" onclick="playSound('critical')">🔴 High</button>
                    <button class="sound-btn btn-medium" onclick="playSound('warning')">🟠 Medium</button>
                    <button class="sound-btn btn-low" onclick="playSound('info')">🔵 Low</button>
                </div>

                <script>
                    {custom_sounds_js}

                    function playSound(priority) {{
                        // Check if custom sound exists
                        const priorityMap = {{'critical': 'high', 'warning': 'medium', 'info': 'low'}};
                        const soundKey = priorityMap[priority];
                        const customSound = customSounds[soundKey];

                        if (customSound) {{
                            // Play custom sound
                            const audio = new Audio(customSound);
                            audio.volume = 0.7;
                            audio.play().catch(e => console.log('Audio play failed:', e));
                            return;
                        }}

                        // Fallback to beeps
                        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                        const oscillator = audioContext.createOscillator();
                        const gainNode = audioContext.createGain();

                        oscillator.connect(gainNode);
                        gainNode.connect(audioContext.destination);

                        if (priority === 'critical') {{
                            // High priority: High pitch, triple beep
                            oscillator.frequency.value = 1200;
                            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);
                            oscillator.start(audioContext.currentTime);
                            oscillator.stop(audioContext.currentTime + 0.15);

                            // Second beep
                            setTimeout(() => {{
                                const osc2 = audioContext.createOscillator();
                                const gain2 = audioContext.createGain();
                                osc2.connect(gain2);
                                gain2.connect(audioContext.destination);
                                osc2.frequency.value = 1200;
                                gain2.gain.setValueAtTime(0.3, audioContext.currentTime);
                                gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);
                                osc2.start(audioContext.currentTime);
                                osc2.stop(audioContext.currentTime + 0.15);
                            }}, 200);

                            // Third beep
                            setTimeout(() => {{
                                const osc3 = audioContext.createOscillator();
                                const gain3 = audioContext.createGain();
                                osc3.connect(gain3);
                                gain3.connect(audioContext.destination);
                                osc3.frequency.value = 1200;
                                gain3.gain.setValueAtTime(0.3, audioContext.currentTime);
                                gain3.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);
                                osc3.start(audioContext.currentTime);
                                osc3.stop(audioContext.currentTime + 0.15);
                            }}, 400);

                        }} else if (priority === 'warning') {{
                            // Medium priority: Medium pitch, double beep
                            oscillator.frequency.value = 800;
                            gainNode.gain.setValueAtTime(0.25, audioContext.currentTime);
                            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.12);
                            oscillator.start(audioContext.currentTime);
                            oscillator.stop(audioContext.currentTime + 0.12);

                            // Second beep
                            setTimeout(() => {{
                                const osc2 = audioContext.createOscillator();
                                const gain2 = audioContext.createGain();
                                osc2.connect(gain2);
                                gain2.connect(audioContext.destination);
                                osc2.frequency.value = 800;
                                gain2.gain.setValueAtTime(0.25, audioContext.currentTime);
                                gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.12);
                                osc2.start(audioContext.currentTime);
                                osc2.stop(audioContext.currentTime + 0.12);
                            }}, 180);

                        }} else {{
                            // Low priority (info): Lower pitch, single beep
                            oscillator.frequency.value = 500;
                            gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
                            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
                            oscillator.start(audioContext.currentTime);
                            oscillator.stop(audioContext.currentTime + 0.1);
                        }}

                        // Make function available globally for auto-alerts
                        window.parent.playAlertSound = playSound;
                    }}
                </script>
            """, height=50)

            st.markdown("---")
            st.caption("Custom Sounds (MP3/WAV):")

            # File uploaders for custom sounds
            high_sound = st.file_uploader("🔴 High Priority", type=["mp3", "wav"], key="upload_high")
            medium_sound = st.file_uploader("🟠 Medium Priority", type=["mp3", "wav"], key="upload_medium")
            low_sound = st.file_uploader("🔵 Low Priority", type=["mp3", "wav"], key="upload_low")

            # Store uploaded sounds in session state
            if high_sound:
                st.session_state.custom_sounds['high'] = base64.b64encode(high_sound.read()).decode()
            if medium_sound:
                st.session_state.custom_sounds['medium'] = base64.b64encode(medium_sound.read()).decode()
            if low_sound:
                st.session_state.custom_sounds['low'] = base64.b64encode(low_sound.read()).decode()

            # Reset button
            if any(st.session_state.custom_sounds.values()):
                if st.button("🔄 Reset to Default Beeps", use_container_width=True):
                    st.session_state.custom_sounds = {'high': None, 'medium': None, 'low': None}
                    st.rerun()

        st.markdown("---")

        # Data file paths
        st.markdown("### 📁 Data Sources")
        gap_file = st.text_input("Gap Data", value="data/gap_details.json")
        ib_file = st.text_input("IB Data", value="data/ib_details.json")
        sp_file = st.text_input("Single Prints", value="data/single_prints.json")
        st.caption("Alerts: data/alerts_nq.json & data/alerts_es.json")

        st.markdown("---")

        # Refresh settings
        st.markdown("### 🔄 Refresh")
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        enable_auto_refresh = st.checkbox("Enable Auto-Refresh", value=False)

        if enable_auto_refresh:
            refresh_interval = st.selectbox(
                "Refresh interval",
                options=[5, 10, 30],
                format_func=lambda x: f"{x} seconds",
                index=0
            )
            st.caption(f"⏱️ Will refresh every {refresh_interval} sec")

        st.markdown("---")

        # Visibility toggles
        st.markdown("### 👁️ Show/Hide Sections")
        show_alerts = st.checkbox("Alerts", value=True, key="show_alerts")
        show_environment = st.checkbox("Environment", value=True, key="show_environment")
        show_risk = st.checkbox("Risk Assessment", value=True, key="show_risk")
        show_gap = st.checkbox("Gap Stats", value=True, key="show_gap")
        show_ib = st.checkbox("Initial Balance", value=True, key="show_ib")
        show_sp = st.checkbox("Single Prints", value=True, key="show_sp")

        st.markdown("---")

        # Section ordering
        st.markdown("### 📐 Reorder Sections")
        st.caption("Click arrows to move sections")

        for idx, section_name in enumerate(st.session_state.section_order):
            col1, col2, col3 = st.columns([1, 1, 4])

            with col1:
                if idx > 0:
                    if st.button("⬆️", key=f"up_{section_name}", use_container_width=True):
                        st.session_state.section_order[idx], st.session_state.section_order[idx-1] = \
                            st.session_state.section_order[idx-1], st.session_state.section_order[idx]
                        st.rerun()

            with col2:
                if idx < len(st.session_state.section_order) - 1:
                    if st.button("⬇️", key=f"down_{section_name}", use_container_width=True):
                        st.session_state.section_order[idx], st.session_state.section_order[idx+1] = \
                            st.session_state.section_order[idx+1], st.session_state.section_order[idx]
                        st.rerun()

            with col3:
                st.markdown(f"**{section_name}**")

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.caption("Live NQ/ES trading statistics dashboard")
        st.caption("Built with Streamlit")

    # Load data files
    gap_df = load_gap_data(Path(__file__).parent / gap_file)
    ib_df = load_ib_data(Path(__file__).parent / ib_file)
    sp_df = load_single_prints_data(Path(__file__).parent / sp_file)
    environment_data = load_environment_data(Path(__file__).parent / "data/market_environment.json")
    risk_data = load_risk_assessment_data(Path(__file__).parent / "data/risk_assessment.json")

    # Section mapping with visibility
    section_config = {
        "Alerts": (show_alerts, lambda: render_alerts_block()),
        "Environment": (show_environment, lambda: render_environment_block(environment_data)),
        "Risk Assessment": (show_risk, lambda: render_risk_assessment_block(risk_data)),
        "Gap Stats": (show_gap, lambda: render_gap_block(gap_df)),
        "Initial Balance": (show_ib, lambda: render_ib_block(ib_df)),
        "Single Prints": (show_sp, lambda: render_single_prints_block(sp_df))
    }

    # Render sections in order - only render visible sections once
    visible_sections = [s for s in st.session_state.section_order
                       if s in section_config and section_config[s][0]]

    for idx, section_name in enumerate(visible_sections):
        _, render_func = section_config[section_name]
        render_func()

        # Only add spacing between sections, not after the last one
        if idx < len(visible_sections) - 1:
            st.markdown("<br>", unsafe_allow_html=True)

    # Auto-refresh ONLY if enabled
    if enable_auto_refresh:
        import time
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
