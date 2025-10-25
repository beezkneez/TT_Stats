import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, time, timedelta
import json
from pathlib import Path
import pytz

# Page config
st.set_page_config(
    page_title="NQ/ES Stats Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for section ordering
if 'section_order' not in st.session_state:
    st.session_state.section_order = ["Alerts", "Gap Stats", "Initial Balance", "Single Prints"]

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

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_gap_data(file_path):
    """Load gap details from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def load_ib_data(file_path):
    """Load Initial Balance data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def load_single_prints_data(file_path):
    """Load Single Prints data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=5)  # Refresh alerts every 5 seconds
def load_alerts_data(file_path):
    """Load real-time alerts from Sierra Chart studies"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

# ========================================
# UTILITY FUNCTIONS
# ========================================

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

    if df is None:
        st.markdown('<div class="coming-soon">🚧 Coming Soon<br><small>Waiting for IB data feed from Sierra Chart</small></div>',
                   unsafe_allow_html=True)
        return

    st.info("IB data loaded - rendering statistics...")

# ========================================
# BLOCK 3: SINGLE PRINTS
# ========================================

def render_single_prints_block(df):
    """Render the Single Prints Statistics block"""
    st.markdown('<div class="block-header">📍 Single Prints Analysis</div>', unsafe_allow_html=True)

    if df is None:
        st.markdown('<div class="coming-soon">🚧 Coming Soon<br><small>Waiting for single prints data feed</small></div>',
                   unsafe_allow_html=True)
        return

    st.info("Single prints data loaded - rendering statistics...")

# ========================================
# BLOCK 4: REAL-TIME ALERTS
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
        st.markdown("### 📊 NQ Alerts")
        nq_alerts = load_alerts_data(Path(__file__).parent / "alerts_nq.json")
        render_alert_feed(nq_alerts, "NQ")

    # ES Column (Right)
    with col_es:
        st.markdown("### 📊 ES Alerts")
        es_alerts = load_alerts_data(Path(__file__).parent / "alerts_es.json")
        render_alert_feed(es_alerts, "ES")

def render_alert_feed(df, symbol):
    """Render alert feed for a specific symbol"""
    if df is None:
        st.info(f"⏳ Waiting for {symbol} alerts")
        return

    # Filter to recent alerts (last 2 hours)
    two_hours_ago = datetime.now(pytz.timezone('US/Eastern')) - timedelta(hours=2)
    recent_alerts = df[df['timestamp'] > two_hours_ago].sort_values('timestamp', ascending=False)

    if len(recent_alerts) == 0:
        st.info(f"No recent {symbol} alerts")
        return

    # Alert count metrics - more compact for side-by-side
    if 'priority' in recent_alerts.columns:
        critical_count = len(recent_alerts[recent_alerts['priority'] == 'critical'])
        warning_count = len(recent_alerts[recent_alerts['priority'] == 'warning'])
        info_count = len(recent_alerts[recent_alerts['priority'] == 'info'])
    else:
        critical_count = 0
        warning_count = 0
        info_count = len(recent_alerts)

    st.caption(f"🔴 {critical_count} | 🟡 {warning_count} | 🔵 {info_count} | Total: {len(recent_alerts)}")
    st.markdown("---")

    # Display alerts - more compact
    for _, alert in recent_alerts.head(15).iterrows():
        alert_class = {
            'critical': 'alert-critical',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }.get(alert.get('priority', 'info'), 'alert-info')

        price_info = f" @ ${alert['price']:.2f}" if 'price' in alert else ""

        st.markdown(f"""
        <div class="alert-box {alert_class}">
            <strong>{alert['timestamp'].strftime('%I:%M:%S')}</strong> - {alert.get('type', 'Alert')}{price_info}<br>
            <small>{alert.get('message', 'No message')}</small>
        </div>
        """, unsafe_allow_html=True)

    # Show alert count
    if len(recent_alerts) > 15:
        st.caption(f"Showing 15 of {len(recent_alerts)} alerts (last 2 hrs)")

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

        # Data file paths
        st.markdown("### 📁 Data Sources")
        gap_file = st.text_input("Gap Data", value="gap_details.json")
        ib_file = st.text_input("IB Data", value="ib_details.json")
        sp_file = st.text_input("Single Prints", value="single_prints.json")
        st.caption("Alerts: alerts_nq.json & alerts_es.json")

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
        show_gap = st.checkbox("Gap Stats", value=True, key="show_gap")
        show_ib = st.checkbox("Initial Balance", value=False, key="show_ib")
        show_sp = st.checkbox("Single Prints", value=False, key="show_sp")

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

    # Section mapping with visibility
    section_config = {
        "Alerts": (show_alerts, lambda: render_alerts_block()),
        "Gap Stats": (show_gap, lambda: render_gap_block(gap_df)),
        "Initial Balance": (show_ib, lambda: render_ib_block(ib_df)),
        "Single Prints": (show_sp, lambda: render_single_prints_block(sp_df))
    }

    # Render sections in order
    for section_name in st.session_state.section_order:
        if section_name in section_config:
            is_visible, render_func = section_config[section_name]
            if is_visible:
                render_func()
                st.markdown("<br>", unsafe_allow_html=True)

    # Auto-refresh ONLY if enabled
    if enable_auto_refresh:
        import time
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
