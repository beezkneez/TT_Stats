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
# Force reset section order to remove "Alerts" if it exists from old sessions
if 'section_order' not in st.session_state or 'Alerts' in st.session_state.section_order:
    st.session_state.section_order = [
        "Daily Context",
        "Environment",
        "Risk Assessment",
        "Opening Range",
        "Initial Balance",
        "3-Stage Progression",
        "TPO Profile",
        "Single Prints",
        "Gap Stats"
    ]

# Initialize session state for dismissed alerts (user-specific, doesn't affect others)
if 'dismissed_alerts' not in st.session_state:
    st.session_state.dismissed_alerts = set()

# Initialize session state for expanded alerts view
if 'expanded_nq_alerts' not in st.session_state:
    st.session_state.expanded_nq_alerts = False
if 'expanded_es_alerts' not in st.session_state:
    st.session_state.expanded_es_alerts = False

# Initialize session state for alert sounds
if 'sound_enabled' not in st.session_state:
    st.session_state.sound_enabled = True

if 'seen_alerts' not in st.session_state:
    st.session_state.seen_alerts = set()

# Initialize session state for toast notifications
if 'toast_alerts' not in st.session_state:
    st.session_state.toast_alerts = set()

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
    /* Toast notifications */
    .toast {
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        animation: slideIn 0.3s ease-out, fadeOut 0.3s ease-in 4.7s;
        backdrop-filter: blur(10px);
        border-left: 4px solid;
    }
    .toast-critical {
        border-color: #d32f2f;
        background: linear-gradient(135deg, rgba(211, 47, 47, 0.95), rgba(183, 28, 28, 0.95));
    }
    .toast-warning {
        border-color: #f57c00;
        background: linear-gradient(135deg, rgba(245, 124, 0, 0.95), rgba(230, 81, 0, 0.95));
    }
    .toast-info {
        border-color: #2196f3;
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.95), rgba(25, 118, 210, 0.95));
    }
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes fadeOut {
        from {
            opacity: 1;
        }
        to {
            opacity: 0;
        }
    }
    .toast-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    .toast-content {
        display: flex;
        align-items: center;
        color: white;
    }
    .toast-text {
        flex: 1;
    }
    .toast-time {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.8);
    }
    .toast-message {
        font-size: 0.9rem;
        margin-top: 0.25rem;
        color: rgba(255, 255, 255, 0.95);
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

@st.cache_data(ttl=300)  # Refresh every 5 minutes (static after 6 AM generation)
def load_daily_context_data(file_path):
    """Load Daily Market Context data from Supabase or JSON file"""
    try:
        if supabase:
            response = supabase.table('daily_context').select('data').eq('id', 1).single().execute()
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

@st.cache_data(ttl=5)  # Refresh every 5 seconds (updates until 10:00 AM, then static)
def load_opening_range_data(file_path):
    """Load Opening Range data from Supabase or JSON file"""
    try:
        if supabase:
            response = supabase.table('opening_range').select('data').eq('id', 1).single().execute()
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

@st.cache_data(ttl=5)  # Refresh every 5 seconds (real-time)
def load_stage_progression_data(file_path):
    """Load 3-Stage Progression data from Supabase or JSON file"""
    try:
        if supabase:
            response = supabase.table('stage_progression').select('data').eq('id', 1).single().execute()
            data = response.data['data']
            if not data or len(data) == 0:
                return []
            return data
    except:
        pass

    # Fallback to JSON file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data if (data and len(data) > 0) else []
    except:
        return []

@st.cache_data(ttl=30)  # Refresh every 30 seconds (updates throughout session)
def load_tpo_profile_data(file_path):
    """Load TPO/Market Profile data from Supabase or JSON file"""
    try:
        if supabase:
            response = supabase.table('tpo_profile').select('data').eq('id', 1).single().execute()
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
        # Determine beep count and frequency based on priority
        beep_config = {
            'critical': (3, 1200),  # 3 beeps at 1200Hz
            'warning': (2, 800),    # 2 beeps at 800Hz
            'info': (1, 500)        # 1 beep at 500Hz
        }
        count, freq = beep_config.get(sound_to_play, (1, 500))

        # Play beeps using the same logic as test buttons
        components.html(f"""
            <script>
                const count = {count};
                const freq = {freq};
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                for (let i = 0; i < count; i++) {{
                    setTimeout(() => {{
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.connect(gain);
                        gain.connect(ctx.destination);
                        osc.frequency.value = freq;
                        gain.gain.setValueAtTime(0.3, ctx.currentTime);
                        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
                        osc.start(ctx.currentTime);
                        osc.stop(ctx.currentTime + 0.15);
                    }}, i * 200);
                }}
            </script>
        """, height=0)

def show_toast_notifications():
    """Show toast notifications for new alerts"""
    # Load recent alerts from both symbols
    nq_alerts = load_alerts_data("alerts_nq")
    es_alerts = load_alerts_data("alerts_es")

    toasts_html = []
    max_toasts = 3  # Only show up to 3 toasts at once
    toast_count = 0

    # Check NQ alerts
    if nq_alerts is not None and len(nq_alerts) > 0:
        for idx, alert in nq_alerts.head(5).iterrows():  # Check most recent 5
            if toast_count >= max_toasts:
                break

            alert_id = generate_alert_id("NQ", alert)

            # Skip dismissed or already toasted alerts
            if alert_id in st.session_state.dismissed_alerts or alert_id in st.session_state.toast_alerts:
                continue

            # Mark as toasted
            st.session_state.toast_alerts.add(alert_id)

            # Create toast HTML
            priority = alert.get('priority', 'info')
            toast_class = f'toast-{priority}'
            icon = '🔴' if priority == 'critical' else '🟡' if priority == 'warning' else '🔵'

            price_info = f" @ ${alert['price']:.2f}" if 'price' in alert else ""
            timestamp_str = alert['timestamp'].strftime('%I:%M:%S %p') if hasattr(alert['timestamp'], 'strftime') else str(alert['timestamp'])
            alert_type = alert.get('type', 'Alert')
            message = alert.get('message', 'No message')

            toasts_html.append(f'''
            <div class="toast {toast_class}">
                <div class="toast-content">
                    <span class="toast-icon">{icon}</span>
                    <div class="toast-text">
                        <div><strong>NQ - {alert_type}</strong>{price_info}</div>
                        <div class="toast-time">{timestamp_str}</div>
                        <div class="toast-message">{message}</div>
                    </div>
                </div>
            </div>
            ''')
            toast_count += 1

    # Check ES alerts
    if es_alerts is not None and len(es_alerts) > 0:
        for idx, alert in es_alerts.head(5).iterrows():  # Check most recent 5
            if toast_count >= max_toasts:
                break

            alert_id = generate_alert_id("ES", alert)

            # Skip dismissed or already toasted alerts
            if alert_id in st.session_state.dismissed_alerts or alert_id in st.session_state.toast_alerts:
                continue

            # Mark as toasted
            st.session_state.toast_alerts.add(alert_id)

            # Create toast HTML
            priority = alert.get('priority', 'info')
            toast_class = f'toast-{priority}'
            icon = '🔴' if priority == 'critical' else '🟡' if priority == 'warning' else '🔵'

            price_info = f" @ ${alert['price']:.2f}" if 'price' in alert else ""
            timestamp_str = alert['timestamp'].strftime('%I:%M:%S %p') if hasattr(alert['timestamp'], 'strftime') else str(alert['timestamp'])
            alert_type = alert.get('type', 'Alert')
            message = alert.get('message', 'No message')

            toasts_html.append(f'''
            <div class="toast {toast_class}">
                <div class="toast-content">
                    <span class="toast-icon">{icon}</span>
                    <div class="toast-text">
                        <div><strong>ES - {alert_type}</strong>{price_info}</div>
                        <div class="toast-time">{timestamp_str}</div>
                        <div class="toast-message">{message}</div>
                    </div>
                </div>
            </div>
            ''')
            toast_count += 1

    # Display toasts if any
    if toasts_html:
        # Escape quotes in HTML for JavaScript
        toasts_escaped = ''.join(toasts_html).replace("'", "\\'").replace('\n', '')

        toast_script = f'''
        <script>
        (function() {{
            // Remove old toast container if exists
            const oldContainer = window.parent.document.getElementById('toast-container-custom');
            if (oldContainer) {{
                oldContainer.remove();
            }}

            // Create toast container
            const container = window.parent.document.createElement('div');
            container.id = 'toast-container-custom';
            container.innerHTML = `{toasts_escaped}`;

            // Apply styles directly
            container.style.position = 'fixed';
            container.style.top = '4rem';
            container.style.right = '1rem';
            container.style.zIndex = '999999';
            container.style.maxWidth = '400px';

            window.parent.document.body.appendChild(container);

            // Auto-remove after 5.5 seconds
            setTimeout(() => {{
                if (container && container.parentNode) {{
                    container.remove();
                }}
            }}, 5500);
        }})();
        </script>
        '''
        components.html(toast_script, height=0)

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
# BLOCK 6: DAILY MARKET CONTEXT
# ========================================

def render_daily_context_block(data):
    """Render the Daily Market Context block (pre-market analysis)"""
    if data is None:
        st.info("⏳ No daily context data available")
        return

    st.markdown('<div class="block-header">📋 Daily Market Context</div>', unsafe_allow_html=True)

    st.caption(f"Generated: {data.get('generated_at', 'N/A')} | Date: {data.get('date', 'N/A')}")

    # Timeframe Analysis
    st.markdown("### 📊 Timeframe Analysis")
    tf_analysis = data.get('timeframe_analysis', {})

    col1, col2, col3 = st.columns(3)

    with col1:
        tf_4hr = tf_analysis.get('4hr', {})
        st.markdown("**4HR**")
        st.markdown(f"**Trend:** {tf_4hr.get('trend', 'N/A').replace('_', ' ').title()}")
        st.markdown(f"**Bias:** {tf_4hr.get('bias', 'N/A').title()}")
        st.caption(tf_4hr.get('context', ''))

    with col2:
        tf_30min = tf_analysis.get('30min', {})
        st.markdown("**30MIN**")
        st.markdown(f"**Trend:** {tf_30min.get('trend', 'N/A').replace('_', ' ').title()}")
        st.markdown(f"**Bias:** {tf_30min.get('bias', 'N/A').title()}")
        st.caption(tf_30min.get('context', ''))

    with col3:
        tf_5min = tf_analysis.get('5min', {})
        st.markdown("**5MIN**")
        st.markdown(f"**Trend:** {tf_5min.get('trend', 'N/A').replace('_', ' ').title()}")
        st.markdown(f"**Bias:** {tf_5min.get('bias', 'N/A').title()}")
        st.caption(tf_5min.get('context', ''))

    st.markdown("---")

    # Key Scenarios
    st.markdown("### 🎯 Key Scenarios")
    scenarios = data.get('key_scenarios', [])

    for scenario in scenarios:
        with st.expander(f"{scenario.get('name', 'Scenario')}"):
            st.markdown(f"**Trigger:** {scenario.get('trigger', 'N/A')}")
            st.markdown(f"**Target:** {scenario.get('target', 'N/A')}")
            st.markdown(f"**Invalidation:** {scenario.get('invalidation', 'N/A')}")

    st.markdown("---")

    # Critical Levels
    st.markdown("### 🎯 Critical Levels")
    levels = data.get('critical_levels', {})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Resistance:**")
        for level in levels.get('resistance', []):
            st.markdown(f"• {level:,.2f}")

    with col2:
        st.markdown("**Support:**")
        for level in levels.get('support', []):
            st.markdown(f"• {level:,.2f}")

    if 'key_level' in levels:
        st.info(f"🔑 **Key Level: {levels['key_level']:,.2f}** - {levels.get('key_level_context', '')}")

# ========================================
# BLOCK 7: OPENING RANGE
# ========================================

def render_opening_range_block(data):
    """Render the Opening Range block (9:30-10:00 EST)"""
    if data is None:
        st.info("⏳ Opening Range data not available yet")
        return

    st.markdown('<div class="block-header">⏰ Opening Range (9:30-10:00 EST)</div>', unsafe_allow_html=True)

    status = data.get('status', 'pending')
    if status == 'pending':
        st.warning("⏳ Waiting for market open at 9:30 AM EST")
        return
    elif status == 'in_progress':
        st.info("📊 Opening Range in progress...")
    else:
        st.success("✅ Opening Range complete")

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        or_high = data.get('high', 0)
        st.metric("OR High", f"{or_high:,.2f}")

    with col2:
        or_low = data.get('low', 0)
        st.metric("OR Low", f"{or_low:,.2f}")

    with col3:
        or_range = data.get('range', 0)
        st.metric("Range", f"{or_range:,.2f}")

    with col4:
        range_pct_atr = data.get('range_pct_atr', 0)
        delta_color = "normal" if range_pct_atr < 30 else "inverse"
        st.metric("% of ATR", f"{range_pct_atr:.1f}%", delta_color=delta_color)

    # Context
    context = data.get('context', '')
    if context:
        st.info(f"💡 {context}")

# ========================================
# BLOCK 8: 3-STAGE PROGRESSION
# ========================================

def render_stage_progression_block(data):
    """Render the 3-Stage Progression Tracker block"""
    if data is None or len(data) == 0:
        st.info("⏳ No levels being tracked")
        return

    st.markdown('<div class="block-header">📈 3-Stage Progression Tracker</div>', unsafe_allow_html=True)

    for level in data:
        level_name = level.get('level_name', 'Unknown Level')
        price = level.get('price', 0)
        current_stage = level.get('current_stage', 0)
        status = level.get('status', 'active')
        direction = level.get('direction', '')
        context = level.get('context', '')

        # Color coding based on stage
        if current_stage == 1:
            stage_color = "#2196f3"  # Blue
            stage_emoji = "1️⃣"
        elif current_stage == 2:
            stage_color = "#ff9800"  # Orange
            stage_emoji = "2️⃣"
        else:
            stage_color = "#4caf50"  # Green
            stage_emoji = "3️⃣"

        # Status emoji
        if status == 'completed':
            status_emoji = "✅"
        else:
            status_emoji = "🔄"

        with st.expander(f"{status_emoji} {level_name} @ {price:,.2f} - Stage {current_stage}", expanded=(current_stage >= 2)):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**Stage:** {stage_emoji} {current_stage}/3")
            with col2:
                st.markdown(f"**Direction:** {direction.replace('_', ' ').title()}")
            with col3:
                st.markdown(f"**Timeframe:** {level.get('timeframe', 'N/A')}")

            # Stage timeline
            st.markdown("**Timeline:**")
            if level.get('stage_1_time'):
                st.caption(f"Stage 1: {level['stage_1_time']}")
            if level.get('stage_2_time'):
                st.caption(f"Stage 2: {level['stage_2_time']}")
            if level.get('stage_3_time'):
                st.caption(f"Stage 3: {level['stage_3_time']}")

            if context:
                st.info(f"💡 {context}")

# ========================================
# BLOCK 9: TPO/MARKET PROFILE
# ========================================

def render_tpo_profile_block(data):
    """Render the TPO/Market Profile block"""
    if data is None:
        st.info("⏳ TPO Profile data not available")
        return

    st.markdown('<div class="block-header">📊 TPO / Market Profile</div>', unsafe_allow_html=True)

    st.caption(f"Session: {data.get('session', 'RTH')} | Date: {data.get('date', 'N/A')}")

    # Profile Overview
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**Type:** {data.get('profile_type', 'N/A')}")
        st.markdown(f"**Shape:** {data.get('shape', 'N/A')}")

    with col2:
        st.metric("POC", f"{data.get('poc', 0):,.2f}")

    with col3:
        st.metric("Range", f"{data.get('range', 0):,.2f}")

    st.markdown("---")

    # Value Area
    st.markdown("### 📍 Value Area")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("VAH", f"{data.get('value_area_high', 0):,.2f}")

    with col2:
        va_pct = data.get('value_area_pct', 70)
        st.metric("VA %", f"{va_pct}%")

    with col3:
        st.metric("VAL", f"{data.get('value_area_low', 0):,.2f}")

    st.markdown("---")

    # Structure
    structure = data.get('structure', {})
    st.markdown("### 🏗️ Structure")

    col1, col2 = st.columns(2)

    with col1:
        single_prints_above = structure.get('single_prints_above', [])
        if single_prints_above:
            st.markdown("**Single Prints Above:**")
            for sp in single_prints_above:
                st.caption(f"• {sp:,.2f}")

        poor_highs = structure.get('poor_highs', [])
        if poor_highs:
            st.markdown("**Poor Highs:**")
            for ph in poor_highs:
                st.caption(f"• {ph:,.2f}")

    with col2:
        single_prints_below = structure.get('single_prints_below', [])
        if single_prints_below:
            st.markdown("**Single Prints Below:**")
            for sp in single_prints_below:
                st.caption(f"• {sp:,.2f}")

        poor_lows = structure.get('poor_lows', [])
        if poor_lows:
            st.markdown("**Poor Lows:**")
            for pl in poor_lows:
                st.caption(f"• {pl:,.2f}")

    # Context
    context = data.get('context', '')
    if context:
        st.info(f"💡 {context}")

    # Trading Implications
    implications = data.get('trading_implications', [])
    if implications:
        st.markdown("### 💡 Trading Implications")
        for implication in implications:
            st.markdown(f"• {implication}")

# ========================================
# BLOCK 10: REAL-TIME ALERTS
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

def render_alert_feed_compact(df, symbol):
    """Render compact alert feed for sidebar"""
    if df is None:
        st.caption(f"⏳ No alerts")
        return

    # Make timestamp timezone-aware if it isn't already
    est = pytz.timezone('US/Eastern')
    if df['timestamp'].dt.tz is None:
        df['timestamp'] = df['timestamp'].dt.tz_localize(est)

    # Sort all alerts by timestamp (most recent first)
    all_alerts = df.sort_values('timestamp', ascending=False)

    # Filter out dismissed alerts (user-specific)
    filtered_alerts = []
    for idx, alert in all_alerts.iterrows():
        alert_id = generate_alert_id(symbol, alert)
        if alert_id not in st.session_state.dismissed_alerts:
            filtered_alerts.append((alert_id, alert))

    if len(filtered_alerts) == 0:
        st.caption(f"No {symbol} alerts")
        return

    # Show count by priority - compact
    critical_count = sum(1 for _, a in filtered_alerts if a.get('priority') == 'critical')
    warning_count = sum(1 for _, a in filtered_alerts if a.get('priority') == 'warning')
    info_count = sum(1 for _, a in filtered_alerts if a.get('priority') == 'info')

    st.caption(f"🔴 {critical_count} 🟡 {warning_count} 🔵 {info_count}")

    # Check if expanded
    is_expanded = st.session_state.get(f'expanded_{symbol.lower()}_alerts', False)

    # Determine how many alerts to show
    alerts_to_show = filtered_alerts if is_expanded else filtered_alerts[:5]

    # Display alerts - very compact
    for alert_id, alert in alerts_to_show:
        priority = alert.get('priority', 'info')
        icon = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}.get(priority, '🔵')

        price_info = f" ${alert['price']:.2f}" if 'price' in alert else ""

        # Very compact alert display
        alert_text = f"{icon} {alert['timestamp'].strftime('%H:%M')} {alert.get('type', 'Alert')}{price_info}"

        # Checkbox for dismissal
        if st.checkbox(alert_text, key=f"dismiss_compact_{alert_id}", value=False, label_visibility="visible"):
            st.session_state.dismissed_alerts.add(alert_id)
            st.rerun()

    # Show expand/collapse button if more than 5 alerts
    if len(filtered_alerts) > 5:
        if is_expanded:
            if st.button("▲ Show less", key=f"collapse_{symbol.lower()}", use_container_width=True):
                st.session_state[f'expanded_{symbol.lower()}_alerts'] = False
                st.rerun()
        else:
            if st.button(f"▼ Show {len(filtered_alerts) - 5} more", key=f"expand_{symbol.lower()}", use_container_width=True):
                st.session_state[f'expanded_{symbol.lower()}_alerts'] = True
                st.rerun()

def render_alert_feed(df, symbol):
    """Render alert feed for a specific symbol"""
    if df is None:
        st.info(f"⏳ Waiting for {symbol} alerts")
        return

    # Make timestamp timezone-aware if it isn't already
    est = pytz.timezone('US/Eastern')
    if df['timestamp'].dt.tz is None:
        df['timestamp'] = df['timestamp'].dt.tz_localize(est)

    # Sort all alerts by timestamp (most recent first)
    all_alerts = df.sort_values('timestamp', ascending=False)

    # Filter out dismissed alerts (user-specific)
    filtered_alerts = []
    for idx, alert in all_alerts.iterrows():
        alert_id = generate_alert_id(symbol, alert)
        if alert_id not in st.session_state.dismissed_alerts:
            filtered_alerts.append((alert_id, alert))

    # Convert back to DataFrame
    alerts_to_show = pd.DataFrame([alert for _, alert in filtered_alerts])

    if len(alerts_to_show) == 0:
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

    # Display alerts - compact with dismiss button
    for alert_id, alert in filtered_alerts[:15]:
        alert_class = {
            'critical': 'alert-critical',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }.get(alert.get('priority', 'info'), 'alert-info')

        price_info = f" @ ${alert['price']:.2f}" if 'price' in alert else ""

        # Use columns for alert content and dismiss button
        col_alert, col_dismiss = st.columns([9, 1])

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
        st.caption(f"Showing 15 of {len(filtered_alerts)} alerts")

# ========================================
# MAIN APP
# ========================================

def main():
    st.markdown('<h1 class="main-header">NQ/ES Trading Stats Dashboard</h1>', unsafe_allow_html=True)

    # Show toast notifications for new alerts
    show_toast_notifications()

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
        # ALERTS SECTION AT TOP
        st.markdown("### 🚨 Alerts")

        # Current time display
        is_live_alerts, current_time_alerts = get_current_market_status()
        st.caption(f"Updated: {current_time_alerts.strftime('%I:%M:%S %p')}")

        # NQ Alerts (Top)
        st.markdown("**📊 NQ Alerts**")
        if st.button("🗑️ Clear NQ", key="clear_nq_sidebar", use_container_width=True):
            nq_data = load_alerts_data("alerts_nq")
            if nq_data is not None:
                for idx, alert in nq_data.iterrows():
                    alert_id = generate_alert_id("NQ", alert)
                    st.session_state.dismissed_alerts.add(alert_id)
            st.rerun()

        nq_alerts = load_alerts_data("alerts_nq")
        check_and_play_alert_sounds(nq_alerts, "NQ")
        render_alert_feed_compact(nq_alerts, "NQ")

        # ES Alerts (Bottom) - no separator, just below NQ
        st.markdown("")  # Small space
        st.markdown("**📊 ES Alerts**")
        if st.button("🗑️ Clear ES", key="clear_es_sidebar", use_container_width=True):
            es_data = load_alerts_data("alerts_es")
            if es_data is not None:
                for idx, alert in es_data.iterrows():
                    alert_id = generate_alert_id("ES", alert)
                    st.session_state.dismissed_alerts.add(alert_id)
            st.rerun()

        es_alerts = load_alerts_data("alerts_es")
        check_and_play_alert_sounds(es_alerts, "ES")
        render_alert_feed_compact(es_alerts, "ES")

        st.markdown("---")

        # Settings section
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

            # Simple HTML buttons with beep sounds
            components.html("""
                <style>
                    .test-btn {
                        border: none;
                        padding: 12px;
                        border-radius: 6px;
                        cursor: pointer;
                        width: 32%;
                        font-size: 13px;
                        color: white;
                        font-weight: bold;
                    }
                    .btn-h { background: #d32f2f; }
                    .btn-m { background: #ff9800; }
                    .btn-l { background: #2196f3; }
                </style>
                <div style="display: flex; gap: 4px; justify-content: space-between;">
                    <button class="test-btn btn-h" onclick="playBeeps(3, 1200)">🔴 High (3x)</button>
                    <button class="test-btn btn-m" onclick="playBeeps(2, 800)">🟠 Medium (2x)</button>
                    <button class="test-btn btn-l" onclick="playBeeps(1, 500)">🔵 Low (1x)</button>
                </div>
                <script>
                    function playBeeps(count, freq) {
                        const ctx = new (window.AudioContext || window.webkitAudioContext)();
                        for (let i = 0; i < count; i++) {
                            setTimeout(() => {
                                const osc = ctx.createOscillator();
                                const gain = ctx.createGain();
                                osc.connect(gain);
                                gain.connect(ctx.destination);
                                osc.frequency.value = freq;
                                gain.gain.setValueAtTime(0.3, ctx.currentTime);
                                gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
                                osc.start(ctx.currentTime);
                                osc.stop(ctx.currentTime + 0.15);
                            }, i * 200);
                        }
                    }
                </script>
            """, height=60)

        st.markdown("---")

        # Data file paths (hidden in session state, using defaults)
        gap_file = "data/gap_details.json"
        ib_file = "data/ib_details.json"
        sp_file = "data/single_prints.json"

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
        show_daily_context = st.checkbox("Daily Context", value=True, key="show_daily_context")
        show_environment = st.checkbox("Environment", value=True, key="show_environment")
        show_risk = st.checkbox("Risk Assessment", value=True, key="show_risk")
        show_opening_range = st.checkbox("Opening Range", value=True, key="show_opening_range")
        show_ib = st.checkbox("Initial Balance", value=True, key="show_ib")
        show_stage_progression = st.checkbox("3-Stage Progression", value=True, key="show_stage_progression")
        show_tpo_profile = st.checkbox("TPO Profile", value=True, key="show_tpo_profile")
        show_sp = st.checkbox("Single Prints", value=True, key="show_sp")
        show_gap = st.checkbox("Gap Stats", value=True, key="show_gap")

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
        st.caption("🔧 Version: 2.2 - Expandable Alerts")

    # Load data files
    gap_df = load_gap_data(Path(__file__).parent / gap_file)
    ib_df = load_ib_data(Path(__file__).parent / ib_file)
    sp_df = load_single_prints_data(Path(__file__).parent / sp_file)
    environment_data = load_environment_data(Path(__file__).parent / "data/market_environment.json")
    risk_data = load_risk_assessment_data(Path(__file__).parent / "data/risk_assessment.json")
    daily_context_data = load_daily_context_data(Path(__file__).parent / "data/daily_context.json")
    opening_range_data = load_opening_range_data(Path(__file__).parent / "data/opening_range.json")
    stage_progression_data = load_stage_progression_data(Path(__file__).parent / "data/stage_progression.json")
    tpo_profile_data = load_tpo_profile_data(Path(__file__).parent / "data/tpo_profile.json")

    # Section mapping with visibility
    section_config = {
        "Daily Context": (show_daily_context, lambda: render_daily_context_block(daily_context_data)),
        "Environment": (show_environment, lambda: render_environment_block(environment_data)),
        "Risk Assessment": (show_risk, lambda: render_risk_assessment_block(risk_data)),
        "Opening Range": (show_opening_range, lambda: render_opening_range_block(opening_range_data)),
        "Initial Balance": (show_ib, lambda: render_ib_block(ib_df)),
        "3-Stage Progression": (show_stage_progression, lambda: render_stage_progression_block(stage_progression_data)),
        "TPO Profile": (show_tpo_profile, lambda: render_tpo_profile_block(tpo_profile_data)),
        "Single Prints": (show_sp, lambda: render_single_prints_block(sp_df)),
        "Gap Stats": (show_gap, lambda: render_gap_block(gap_df))
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
