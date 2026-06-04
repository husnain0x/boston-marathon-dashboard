"""
app.py — Boston Marathon Data Visualization Dashboard
Noon-inspired premium dark theme: Deep black + warm amber/gold/orange glow.
Memory-optimized: charts render to PNG bytes, displayed as images.
"""

import streamlit as st
import pandas as pd
import numpy as np
import gc
from filters import load_and_merge_data, apply_filters
from charts import (
    plot_pie_chart, plot_histogram, plot_line_chart, plot_bar_chart,
    plot_scatter, plot_boxplot, plot_heatmap, plot_area_chart,
    plot_countplot, plot_violin, plot_pairplot, plot_bubble_chart,
    plot_funnel_chart
)

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Boston Marathon Dashboard",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# NOON-INSPIRED PREMIUM CSS + ANIMATIONS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-deep: #08080a;
        --bg-card: #0e0e12;
        --bg-card-hover: #121216;
        --border: #1a1815;
        --border-warm: #2a2318;
        --amber: #e8933a;
        --amber-light: #f0a852;
        --amber-dark: #c47520;
        --gold: #d4a850;
        --gold-light: #e8c86a;
        --orange: #e07830;
        --text-white: #f5f0e8;
        --text-light: #c8c0b0;
        --text-dim: #7a7468;
        --text-muted: #4a4540;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(25px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 12px rgba(232,147,58,0.3); }
        50% { box-shadow: 0 0 20px rgba(232,147,58,0.5); }
    }
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.92); }
        to { opacity: 1; transform: scale(1); }
    }

    .stApp { background: var(--bg-deep) !important; font-family: 'Inter', -apple-system, sans-serif; }
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"] { background: var(--bg-deep) !important; }
    html { scroll-behavior: smooth; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0e 0%, #0e0d10 100%) !important;
        border-right: 1px solid rgba(232, 147, 58, 0.06);
        transition: transform 0.3s ease, opacity 0.3s ease;
    }
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown h4 {
        color: var(--amber) !important; font-weight: 600 !important;
        font-size: 0.7rem !important; letter-spacing: 2px; text-transform: uppercase; opacity: 0.85;
    }
    section[data-testid="stSidebar"] hr { border-color: rgba(232, 147, 58, 0.08) !important; }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(14,14,18,0.98), rgba(18,18,22,0.95));
        border: 1px solid rgba(232, 147, 58, 0.08); border-radius: 16px;
        padding: 24px 22px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4), 0 0 1px rgba(232, 147, 58, 0.1),
                    inset 0 1px 0 rgba(255,255,255,0.02);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative; overflow: hidden;
        animation: scaleIn 0.5s ease-out backwards;
    }
    div[data-testid="stMetric"]:nth-child(1) { animation-delay: 0.1s; }
    div[data-testid="stMetric"]:nth-child(2) { animation-delay: 0.2s; }
    div[data-testid="stMetric"]:nth-child(3) { animation-delay: 0.3s; }
    div[data-testid="stMetric"]::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(232,147,58,0.15), transparent);
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(232, 147, 58, 0.25);
        box-shadow: 0 8px 35px rgba(0,0,0,0.5), 0 0 60px rgba(232, 147, 58, 0.06),
                    inset 0 1px 0 rgba(255,255,255,0.03);
        transform: translateY(-4px) scale(1.02);
    }
    div[data-testid="stMetric"] label {
        color: var(--text-dim) !important; font-size: 0.68rem !important;
        font-weight: 600 !important; letter-spacing: 1.8px; text-transform: uppercase;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--text-white) !important; font-size: 1.4rem !important;
        font-weight: 800 !important; letter-spacing: -0.5px; white-space: nowrap; overflow: visible;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        color: var(--amber) !important; font-size: 0.7rem !important; font-weight: 500 !important;
    }

    .noon-header {
        text-align: center; padding: 50px 0 10px 0; position: relative;
        animation: fadeInUp 0.8s ease-out;
    }
    .noon-header::before {
        content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%);
        width: 300px; height: 200px;
        background: radial-gradient(ellipse, rgba(232,147,58,0.06) 0%, transparent 70%);
        pointer-events: none; animation: fadeIn 1.5s ease-out;
    }
    .noon-badge {
        display: inline-block; background: rgba(232, 147, 58, 0.06);
        border: 1px solid rgba(232, 147, 58, 0.12); color: var(--amber);
        padding: 5px 18px; border-radius: 100px; font-size: 0.65rem;
        font-weight: 600; letter-spacing: 2.5px; text-transform: uppercase;
        margin-bottom: 18px; font-family: 'Inter', sans-serif;
        animation: scaleIn 0.6s ease-out 0.2s backwards;
    }
    .noon-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.8rem !important; font-weight: 700 !important;
        color: var(--text-white) !important; letter-spacing: -1px;
        margin: 0 !important; line-height: 1.15 !important;
    }
    .noon-title span {
        background: linear-gradient(135deg, #f0a852, #e8933a, #d4a850);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-size: 200% auto; animation: shimmer 4s linear infinite;
    }
    .noon-sub {
        text-align: center; color: var(--text-dim); font-size: 0.88rem;
        margin: 12px 0 40px 0; font-weight: 400; line-height: 1.6; letter-spacing: 0.2px;
        animation: fadeIn 1s ease-out 0.4s backwards;
    }

    .noon-section {
        display: flex; align-items: center; gap: 16px;
        margin: 55px 0 28px 0; animation: fadeInUp 0.6s ease-out;
    }
    .noon-section-dot {
        width: 8px; height: 8px; border-radius: 50%; background: var(--amber);
        box-shadow: 0 0 12px rgba(232,147,58,0.3); flex-shrink: 0;
        animation: pulseGlow 2.5s ease-in-out infinite;
    }
    .noon-section-info { flex-shrink: 0; }
    .noon-section-title {
        font-family: 'Playfair Display', serif; font-size: 1.25rem;
        font-weight: 600; color: var(--text-white); margin: 0;
        letter-spacing: -0.3px; line-height: 1.2;
    }
    .noon-section-sub {
        font-size: 0.72rem; color: var(--text-dim); margin: 3px 0 0 0;
        font-weight: 400; letter-spacing: 0.3px;
    }
    .noon-section-line {
        flex-grow: 1; height: 1px;
        background: linear-gradient(90deg, rgba(232,147,58,0.15) 0%, transparent 100%);
    }

    .noon-chart {
        background: linear-gradient(145deg, rgba(12,12,16,0.98), rgba(16,15,18,0.95));
        border: 1px solid rgba(232, 147, 58, 0.05); border-radius: 18px;
        padding: 8px; margin-bottom: 18px;
        box-shadow: 0 4px 25px rgba(0,0,0,0.3);
        transition: all 0.45s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative; overflow: hidden;
        animation: fadeInUp 0.7s ease-out backwards;
    }
    .noon-chart::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(232,147,58,0.08) 50%, transparent 100%);
    }
    .noon-chart:hover {
        border-color: rgba(232, 147, 58, 0.15);
        box-shadow: 0 8px 40px rgba(0,0,0,0.45), 0 0 60px rgba(232, 147, 58, 0.04);
        transform: translateY(-3px);
    }
    .chart-left .noon-chart { animation-delay: 0.1s; }
    .chart-right .noon-chart { animation-delay: 0.25s; }

    .stButton > button {
        background: linear-gradient(135deg, #c47520, #e8933a) !important;
        color: #08080a !important; border: none !important; border-radius: 10px !important;
        font-weight: 700 !important; font-size: 0.8rem !important;
        padding: 8px 22px !important; letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #e8933a, #f0a852) !important;
        box-shadow: 0 0 30px rgba(232, 147, 58, 0.25) !important;
        transform: translateY(-2px) !important;
    }

    .stSlider > div > div > div > div { background: var(--amber) !important; }
    .stSlider label, .stSelectbox label, .stMultiSelect label, .stTextInput label {
        color: var(--text-dim) !important; font-size: 0.78rem !important; font-weight: 500 !important;
    }
    .stSelectbox > div > div, .stMultiSelect > div > div {
        background: rgba(14,14,18,0.95) !important;
        border-color: rgba(232,147,58,0.1) !important;
        color: var(--text-light) !important; border-radius: 10px !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    }
    .stSelectbox > div > div:focus-within, .stMultiSelect > div > div:focus-within {
        border-color: rgba(232,147,58,0.3) !important;
        box-shadow: 0 0 15px rgba(232,147,58,0.08) !important;
    }
    .stTextInput > div > div > input {
        background: rgba(14,14,18,0.95) !important;
        border-color: rgba(232,147,58,0.1) !important;
        color: var(--text-light) !important; border-radius: 10px !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(232,147,58,0.3) !important;
        box-shadow: 0 0 15px rgba(232,147,58,0.08) !important;
    }

    details {
        background: rgba(12,12,16,0.95) !important;
        border: 1px solid rgba(232, 147, 58, 0.06) !important;
        border-radius: 14px !important; transition: all 0.3s ease !important;
    }
    details:hover { border-color: rgba(232, 147, 58, 0.12) !important; }
    details summary { color: var(--amber) !important; font-weight: 600 !important; font-size: 0.9rem !important; }

    .stDataFrame {
        border: 1px solid rgba(232, 147, 58, 0.06) !important;
        border-radius: 14px !important; animation: fadeInUp 0.6s ease-out;
    }

    .noon-footer {
        text-align: center; padding: 35px 0; margin-top: 50px;
        border-top: 1px solid rgba(232, 147, 58, 0.06); animation: fadeIn 0.8s ease-out;
    }
    .noon-footer p { color: var(--text-muted); font-size: 0.75rem; letter-spacing: 0.5px; }
    .noon-footer span.highlight { color: var(--amber); transition: color 0.3s ease; }
    .noon-footer span.highlight:hover { color: var(--amber-light); }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    .stSpinner > div { border-color: var(--amber) !important; }
    [data-testid="stHorizontalBlock"] > div { transition: all 0.3s ease; }

    /* Hide image expand button for chart images */
    button[title="View fullscreen"] { display: none !important; }

    /* Section number badges */
    .section-badge {
        display: inline-flex; align-items: center; justify-content: center;
        width: 28px; height: 28px; border-radius: 50%;
        background: linear-gradient(135deg, #c47520, #e8933a);
        color: #08080a; font-size: 0.75rem; font-weight: 800;
        flex-shrink: 0; box-shadow: 0 0 12px rgba(232,147,58,0.3);
    }

    /* Chart captions */
    .chart-caption {
        background: rgba(232,147,58,0.04);
        border-top: 1px solid rgba(232,147,58,0.08);
        border-radius: 0 0 14px 14px;
        padding: 10px 16px;
        margin-top: -8px;
        margin-bottom: 18px;
    }
    .chart-caption p {
        color: #6a6460; font-size: 0.7rem; line-height: 1.55;
        margin: 0; font-weight: 400;
    }
    .chart-caption p b { color: #a89880; font-weight: 600; }

    /* Overview intro box */
    .overview-box {
        background: linear-gradient(145deg, rgba(14,14,18,0.98), rgba(16,15,20,0.95));
        border: 1px solid rgba(232,147,58,0.08); border-radius: 16px;
        padding: 22px 28px; margin-bottom: 32px; position: relative; overflow: hidden;
    }
    .overview-box::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(232,147,58,0.15), transparent);
    }
    .overview-box h4 {
        color: #e8933a; font-size: 0.65rem; font-weight: 700;
        letter-spacing: 2.5px; text-transform: uppercase; margin: 0 0 10px 0;
    }
    .overview-box p {
        color: #8a8278; font-size: 0.8rem; line-height: 1.7; margin: 0;
    }
    .overview-box p b { color: #c8c0b0; }
    .overview-tag {
        display: inline-block; background: rgba(232,147,58,0.08);
        border: 1px solid rgba(232,147,58,0.15); color: #e8933a;
        padding: 3px 10px; border-radius: 100px; font-size: 0.62rem;
        font-weight: 600; letter-spacing: 1px; margin: 2px 3px 0 0;
    }

    /* Export section */
    .export-box {
        background: linear-gradient(145deg, rgba(14,14,18,0.98), rgba(16,15,20,0.95));
        border: 1px solid rgba(232,147,58,0.08); border-radius: 16px;
        padding: 24px 28px; margin: 12px 0 32px 0;
    }
    .export-box h4 {
        color: #e8933a; font-size: 0.65rem; font-weight: 700;
        letter-spacing: 2.5px; text-transform: uppercase; margin: 0 0 14px 0;
    }

    /* Dashboard info footer card */
    .info-card {
        background: linear-gradient(145deg, rgba(14,14,18,0.98), rgba(16,15,20,0.95));
        border: 1px solid rgba(232,147,58,0.08); border-radius: 16px;
        padding: 24px 28px; margin: 12px 0 32px 0;
    }
    .info-card h4 {
        color: #e8933a; font-size: 0.65rem; font-weight: 700;
        letter-spacing: 2.5px; text-transform: uppercase; margin: 0 0 14px 0;
    }
    .info-grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 12px; margin-top: 10px;
    }
    .info-item { }
    .info-item-label {
        color: #4a4540; font-size: 0.6rem; font-weight: 700;
        letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 3px;
    }
    .info-item-value { color: #c8c0b0; font-size: 0.78rem; font-weight: 500; }

    /* Insight cards */
    /* Insight cards */
    .insight-row {
        display: flex; gap: 14px; margin: 18px 0 32px 0; flex-wrap: wrap;
    }
    .insight-card {
        flex: 1; min-width: 200px;
        background: linear-gradient(145deg, rgba(14,14,18,0.98), rgba(18,17,20,0.95));
        border: 1px solid rgba(232,147,58,0.08); border-radius: 14px;
        padding: 18px 20px; position: relative; overflow: hidden;
        transition: border-color 0.3s ease, transform 0.3s ease;
    }
    .insight-card:hover {
        border-color: rgba(232,147,58,0.2);
        transform: translateY(-2px);
    }
    .insight-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(232,147,58,0.12), transparent);
    }
    .insight-icon { font-size: 1.3rem; margin-bottom: 8px; }
    .insight-label {
        color: #4a4540; font-size: 0.6rem; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px;
    }
    .insight-value {
        color: #e8933a; font-size: 1.15rem; font-weight: 800;
        letter-spacing: -0.3px; margin-bottom: 4px;
    }
    .insight-desc {
        color: #7a7468; font-size: 0.72rem; line-height: 1.5; font-weight: 400;
    }
    .insight-desc b { color: #c8c0b0; font-weight: 600; }

    /* Fun fact banner */
    .fact-banner {
        background: linear-gradient(135deg, rgba(232,147,58,0.04), rgba(212,168,80,0.04));
        border: 1px solid rgba(232,147,58,0.1); border-radius: 14px;
        padding: 16px 22px; margin: 10px 0 30px 0;
        display: flex; align-items: flex-start; gap: 14px;
    }
    .fact-banner-icon { font-size: 1.4rem; flex-shrink: 0; margin-top: 2px; }
    .fact-banner-text { color: #7a7468; font-size: 0.78rem; line-height: 1.6; }
    .fact-banner-text b { color: #e8933a; }
</style>
""", unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════
# LOAD DATA (cached)
# ═══════════════════════════════════════════════════════════════
@st.cache_data
def get_data():
    return load_and_merge_data()

try:
    df = get_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()


# ═══════════════════════════════════════════════════════════════
# CHART CACHE — render once per filter, store as PNG bytes
# ═══════════════════════════════════════════════════════════════
@st.cache_data(max_entries=5, ttl=300)
def render_chart(_chart_func, df_hash, chart_name):
    """Render chart to PNG bytes and cache. df_hash used for cache key."""
    # Reconstruct df from session — we pass the actual df via closure below
    return None  # placeholder — real rendering done in render_chart_real

def get_df_hash(filtered_df):
    """Fast hash of dataframe for cache keys."""
    return hash((len(filtered_df), tuple(filtered_df.columns),
                 filtered_df.iloc[0].values.tobytes() if len(filtered_df) > 0 else b"",
                 filtered_df.iloc[-1].values.tobytes() if len(filtered_df) > 0 else b""))


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
st.sidebar.markdown("""
<div style='text-align:center; padding: 22px 0 14px 0;'>
    <div style='width: 48px; height: 48px; margin: 0 auto 12px auto;
         background: radial-gradient(circle, rgba(232,147,58,0.12), transparent);
         border: 1px solid rgba(232,147,58,0.15); border-radius: 14px;
         display: flex; align-items: center; justify-content: center;'>
        <span style='font-size: 1.5rem;'>🏃</span>
    </div>
    <h2 style='margin:0; font-family: Playfair Display, serif;
        color: #f5f0e8; font-size: 1.15rem; font-weight: 700;
        letter-spacing: -0.3px;'>Boston Marathon</h2>
    <p style='color: #4a4540; font-size: 0.65rem; margin: 5px 0 0 0;
       letter-spacing: 2.5px; text-transform: uppercase; font-weight: 600;'>Analytics Dashboard</p>
</div>
""", unsafe_allow_html=True)

filtered_df = apply_filters(df)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='background: rgba(14,14,18,0.95); border: 1px solid rgba(232,147,58,0.08);
     border-radius: 14px; padding: 16px; text-align: center;
     position: relative; overflow: hidden;'>
    <div style='position:absolute; top:0; left:0; right:0; height:1px;
         background: linear-gradient(90deg, transparent, rgba(232,147,58,0.1), transparent);'></div>
    <span style='color: #4a4540; font-size: 0.62rem; text-transform: uppercase;
           letter-spacing: 2px; font-weight: 600;'>Active Records</span><br>
    <span style='color: #e8933a; font-size: 2rem; font-weight: 800;
           letter-spacing: -1px;'>{len(filtered_df)}</span>
    <span style='color: #3a3530; font-size: 0.85rem; font-weight: 500;'> / {len(df)}</span>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="noon-header">
    <div class="noon-badge">Data Visualization Project</div><br>
    <span class="noon-title">Boston <span>Marathon</span></span><br>
    <span class="noon-title" style="font-size: 2.2rem !important; opacity: 0.7;">Dashboard</span>
</div>
<p class="noon-sub">
    Comprehensive historical analysis of Boston Marathon winners<br>
    <span style="color: #e8933a; font-weight: 500;">Men's (1897-2024)</span> &
    <span style="color: #e86850; font-weight: 500;">Women's (1966-2024)</span> -
    Performance, Trends & Insights
</p>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def mins_to_hms(m):
    try:
        h = int(m // 60)
        mi = int(m % 60)
        s = int((m % 1) * 60)
        return f"{h}:{mi:02d}:{s:02d}"
    except (ValueError, TypeError):
        return "N/A"

_section_counter = [0]
def section(title, subtitle):
    _section_counter[0] += 1
    n = _section_counter[0]
    st.markdown(f"""
    <div class="noon-section">
        <div class="section-badge">{n}</div>
        <div class="noon-section-info">
            <p class="noon-section-title">{title}</p>
            <p class="noon-section-sub">{subtitle}</p>
        </div>
        <div class="noon-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

def show_chart(chart_func, data, chart_name="Chart"):
    """Render chart to bytes and display as image. Memory-safe."""
    try:
        img_bytes = chart_func(data)
        if img_bytes is not None:
            st.image(img_bytes, use_container_width=True)
        else:
            st.info(f"No data available for {chart_name}")
    except Exception as e:
        st.warning(f"Could not render {chart_name}: {str(e)[:100]}")
    finally:
        gc.collect()

if filtered_df.empty:
    st.warning("No data matches the current filters. Adjust the filter criteria.")
    st.stop()

def insight_cards(*cards):
    """Render a row of insight cards. Each card = (icon, label, value, desc)."""
    items = "".join(f"""
        <div class="insight-card">
            <div class="insight-icon">{icon}</div>
            <div class="insight-label">{label}</div>
            <div class="insight-value">{value}</div>
            <div class="insight-desc">{desc}</div>
        </div>""" for icon, label, value, desc in cards)
    st.markdown(f'<div class="insight-row">{items}</div>', unsafe_allow_html=True)

def fact_banner(icon, text):
    st.markdown(f"""
    <div class="fact-banner">
        <div class="fact-banner-icon">{icon}</div>
        <div class="fact-banner-text">{text}</div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# OVERVIEW BOX
# ═══════════════════════════════════════════════════════════════
_men_years = int(df[df["Gender"]=="Male"]["Year"].max()) - int(df[df["Gender"]=="Male"]["Year"].min())
_women_years = int(df[df["Gender"]=="Female"]["Year"].max()) - int(df[df["Gender"]=="Female"]["Year"].min())
_total_countries = df["Country"].nunique()
st.markdown(f'''
<div class="overview-box">
    <h4>📋 Dashboard Overview</h4>
    <p>
        This dashboard explores <b>{len(df)} historical race results</b> from the Boston Marathon —
        the world's oldest annual marathon, held every Patriots' Day since <b>1897</b>.
        The dataset covers <b>Men's records ({int(df[df["Gender"]=="Male"]["Year"].min())}–{int(df[df["Gender"]=="Male"]["Year"].max())})</b>
        and <b>Women's records ({int(df[df["Gender"]=="Female"]["Year"].min())}–{int(df[df["Gender"]=="Female"]["Year"].max())})</b>
        spanning winners from <b>{_total_countries} countries</b> across 6 continents.
        Use the sidebar filters to drill into specific years, genders, countries, or search by winner name.
    </p>
    <div style="margin-top:12px;">
        <span class="overview-tag">🏃 {len(df[df["Gender"]=="Male"])} Men's Records</span>
        <span class="overview-tag">🚺 {len(df[df["Gender"]=="Female"])} Women's Records</span>
        <span class="overview-tag">🌍 {_total_countries} Countries</span>
        <span class="overview-tag">📅 {int(df["Year"].max()) - int(df["Year"].min())} Year Span</span>
        <span class="overview-tag">⏱️ 10 Chart Types</span>
    </div>
</div>
''', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# KPI CARDS
# ═══════════════════════════════════════════════════════════════
time_data = filtered_df["Time_Minutes"].dropna()
avg_time = time_data.mean() if len(time_data) > 0 else 0
fastest_time = time_data.min() if len(time_data) > 0 else 0
fastest_row = filtered_df.loc[filtered_df["Time_Minutes"].idxmin()] if len(time_data) > 0 else None
total_countries = filtered_df["Country"].nunique()
speed_data = filtered_df["Speed_MPH"].dropna()
avg_speed = speed_data.mean() if len(speed_data) > 0 else 0
year_span = f"{int(filtered_df['Year'].min())}-{int(filtered_df['Year'].max())}"

k1, k2, k3 = st.columns(3)
k1.metric("Total Records", f"{len(filtered_df)}", delta=f"{len(filtered_df['Gender'].unique())} categories")
k2.metric("Year Span", year_span)
k3.metric("Avg Finish Time", mins_to_hms(avg_time))

k4, k5, k6 = st.columns(3)
fastest_name = fastest_row['Winner'] if fastest_row is not None else "N/A"
k4.metric("Fastest Record", mins_to_hms(fastest_time), delta=f"{fastest_name}")
k5.metric("Countries", f"{total_countries}")
k6.metric("Avg Speed", f"{avg_speed:.2f} mph")


# ═══════════════════════════════════════════════════════════════
# SECTION 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════
section("Overview & Composition", "Country distribution and time frequency analysis")

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="chart-left"><div class="noon-chart">', unsafe_allow_html=True)
    show_chart(plot_pie_chart, filtered_df, "Pie Chart")
    st.markdown('</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="chart-right"><div class="noon-chart">', unsafe_allow_html=True)
    show_chart(plot_histogram, filtered_df, "Histogram")
    st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('''
<div class="chart-caption"><p>
<b>Winners by Country</b> — The pie chart reveals national dominance patterns.
<b>Histogram</b> — Distribution of winning times shows how elite performance clusters in a tight band,
with the long right tail representing early-era races before modern training methods.
</p></div>''', unsafe_allow_html=True)

gc.collect()

# Section 1 insights
_top_country = filtered_df["Country"].value_counts().index[0] if len(filtered_df) > 0 else "N/A"
_top_count   = filtered_df["Country"].value_counts().iloc[0]  if len(filtered_df) > 0 else 0
_total_c     = filtered_df["Country"].nunique()
_pct_top     = round(_top_count / len(filtered_df) * 100, 1) if len(filtered_df) > 0 else 0
_time_mode_bin = int(filtered_df["Time_Minutes"].dropna().mode().iloc[0]) if len(filtered_df) > 0 else 0

insight_cards(
    ("🌍", "Dominant Nation", _top_country,
     f"Won <b>{_top_count}</b> races — <b>{_pct_top}%</b> of all filtered records. "
     f"A total of <b>{_total_c}</b> nations have won the Boston Marathon."),
    ("⏱️", "Most Common Finish", f"~{_time_mode_bin} min",
     f"The most frequent winning time falls around <b>{_time_mode_bin} minutes</b> "
     f"({_time_mode_bin//60}h {_time_mode_bin%60}m). Times cluster tightly among elite runners."),
    ("📊", "Dataset Snapshot", f"{len(filtered_df)} records",
     f"Showing <b>{len(filtered_df)}</b> race results across "
     f"<b>{filtered_df['Year'].nunique()}</b> years and "
     f"<b>{filtered_df['Gender'].nunique()}</b> gender categor{'y' if filtered_df['Gender'].nunique()==1 else 'ies'}."),
)

# ═══════════════════════════════════════════════════════════════
# SECTION 2 — TRENDS
# ═══════════════════════════════════════════════════════════════
section("Performance Trends", "How winning times have evolved across decades")

st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
show_chart(plot_line_chart, filtered_df, "Line Chart")
st.markdown('</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    st.markdown('<div class="chart-left"><div class="noon-chart">', unsafe_allow_html=True)
    show_chart(plot_scatter, filtered_df, "Scatter Plot")
    st.markdown('</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="chart-right"><div class="noon-chart">', unsafe_allow_html=True)
    show_chart(plot_area_chart, filtered_df, "Area Chart")
    st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('''
<div class="chart-caption"><p>
<b>Line Chart</b> — The downward trend in winning times reflects advances in training, nutrition, and shoe technology.
<b>Scatter</b> — Each dot is one race; the regression line shows the long-term improvement trajectory.
<b>Area Chart</b> — Cumulative view of time trends, highlighting the dramatic improvement post-1970s
when women began competing officially and training science matured.
</p></div>''', unsafe_allow_html=True)

gc.collect()

# Section 2 insights
_earliest = int(filtered_df["Year"].min()) if len(filtered_df) > 0 else "N/A"
_latest   = int(filtered_df["Year"].max()) if len(filtered_df) > 0 else "N/A"
_fastest  = filtered_df["Time_Minutes"].min() if len(filtered_df) > 0 else 0
_slowest  = filtered_df["Time_Minutes"].max() if len(filtered_df) > 0 else 0
_improvement = round(_slowest - _fastest, 1) if len(filtered_df) > 0 else 0
_avg_spd  = round(filtered_df["Speed_MPH"].dropna().mean(), 2) if len(filtered_df) > 0 else 0

def fmt(m):
    try: return f"{int(m//60)}h {int(m%60)}m {int((m%1)*60)}s"
    except: return "N/A"

insight_cards(
    ("🚀", "Fastest Winning Time", fmt(_fastest),
     f"Set in <b>{int(filtered_df.loc[filtered_df['Time_Minutes'].idxmin(),'Year'])}</b> by "
     f"<b>{filtered_df.loc[filtered_df['Time_Minutes'].idxmin(),'Winner']}</b>. "
     f"Elite marathons have seen dramatic speed improvements since {_earliest}."),
    ("📉", "Time Improvement", f"{_improvement:.1f} min",
     f"Winning times dropped by <b>{_improvement:.1f} minutes</b> from the slowest "
     f"to the fastest in this selection — driven by better training, nutrition & shoes."),
    ("💨", "Avg Winning Speed", f"{_avg_spd} mph",
     f"Winners average <b>{_avg_spd} mph</b> across 26.2 miles. "
     f"That's roughly <b>{round(60/_avg_spd*26.2,1)} min total</b> at a relentless pace."),
)

fact_banner("💡",
    f"The Boston Marathon — held every <b>Patriots' Day</b> in April — is the world's oldest "
    f"annual marathon (since <b>1897</b>). The course runs from Hopkinton to Boston, covering "
    f"exactly <b>26.2 miles (42.195 km)</b>. The infamous 'Heartbreak Hill' at mile 20-21 "
    f"has broken many a race strategy.")

# ═══════════════════════════════════════════════════════════════
# SECTION 3 — COMPARISONS
# ═══════════════════════════════════════════════════════════════
section("Comparisons & Rankings", "Country standings and decade-wise breakdowns")

col5, col6 = st.columns(2)
with col5:
    st.markdown('<div class="chart-left"><div class="noon-chart">', unsafe_allow_html=True)
    show_chart(plot_bar_chart, filtered_df, "Bar Chart")
    st.markdown('</div></div>', unsafe_allow_html=True)
with col6:
    st.markdown('<div class="chart-right"><div class="noon-chart">', unsafe_allow_html=True)
    show_chart(plot_countplot, filtered_df, "Count Plot")
    st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('''
<div class="chart-caption"><p>
<b>Bar Chart</b> — Total wins per country; dominance by USA (early era), Japan (mid-era), Kenya and Ethiopia (modern era).
<b>Count Plot</b> — Race counts grouped by decade; shows the expansion of the women's field
from the 1970s onward and the full historical depth of the men's competition since 1897.
</p></div>''', unsafe_allow_html=True)

gc.collect()

# Section 3 insights
_top3 = filtered_df["Country"].value_counts().head(3)
_top3_str = ", ".join([f"<b>{c}</b> ({n})" for c,n in _top3.items()])
_decades = filtered_df["Decade_Label"].value_counts()
_best_decade = _decades.index[0] if len(_decades) > 0 else "N/A"
_best_decade_n = _decades.iloc[0] if len(_decades) > 0 else 0
_unique_winners = filtered_df["Winner"].nunique()

insight_cards(
    ("🏆", "Top 3 Countries", "",
     f"The podium of nations: {_top3_str}. These countries have dominated Boston's finish line for decades."),
    ("📅", "Most Active Decade", _best_decade,
     f"The <b>{_best_decade}</b> had the most winners in this selection (<b>{_best_decade_n} races</b>). "
     f"Decade trends reveal how participation and competition evolved over time."),
    ("🏅", "Unique Champions", f"{_unique_winners}",
     f"<b>{_unique_winners}</b> different athletes won across the filtered records. "
     f"Some legends — like <b>Clarence DeMar</b> (7 wins) — dominated multiple eras."),
)

# ═══════════════════════════════════════════════════════════════
# SECTION 4 — STATISTICAL
# ═══════════════════════════════════════════════════════════════
section("Statistical Distribution", "Spread, density, and correlation analysis")

col7, col8 = st.columns(2)
with col7:
    st.markdown('<div class="chart-left"><div class="noon-chart">', unsafe_allow_html=True)
    show_chart(plot_boxplot, filtered_df, "Box Plot")
    st.markdown('</div></div>', unsafe_allow_html=True)
with col8:
    st.markdown('<div class="chart-right"><div class="noon-chart">', unsafe_allow_html=True)
    show_chart(plot_violin, filtered_df, "Violin Plot")
    st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
show_chart(plot_heatmap, filtered_df, "Heatmap")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('''
<div class="chart-caption"><p>
<b>Box Plot</b> — Interquartile ranges reveal the spread of winning times by gender and decade.
Outliers (dots beyond whiskers) are typically early-era races with longer distances or harsh conditions.
<b>Violin Plot</b> — Adds density information; the wider the violin, the more races at that time.
<b>Heatmap</b> — Correlation matrix shows strong negative correlation between year and time
(times decrease as years increase), confirming the improvement trend seen in Section 2.
</p></div>''', unsafe_allow_html=True)

gc.collect()

# Section 4 insights
_median_t  = round(filtered_df["Time_Minutes"].dropna().median(), 1)
_std_t     = round(filtered_df["Time_Minutes"].dropna().std(), 1)
_male_avg  = round(filtered_df[filtered_df["Gender"]=="Male"]["Time_Minutes"].mean(), 1)   if "Male"   in filtered_df["Gender"].values else None
_female_avg= round(filtered_df[filtered_df["Gender"]=="Female"]["Time_Minutes"].mean(), 1) if "Female" in filtered_df["Gender"].values else None
_gap = round(_female_avg - _male_avg, 1) if (_male_avg and _female_avg) else None

insight_cards(
    ("📐", "Median Finish Time", f"{_median_t} min",
     f"The median winning time is <b>{_median_t} min</b> ({int(_median_t//60)}h {int(_median_t%60)}m). "
     f"The standard deviation of <b>{_std_t} min</b> shows how tightly clustered elite performances are."),
    ("⚖️", "Gender Gap", f"{_gap} min" if _gap else "Single gender",
     (f"Men average <b>{_male_avg} min</b>, Women <b>{_female_avg} min</b> — a gap of <b>{_gap} min</b>. "
      f"The women's gap has narrowed significantly since the 1970s as elite female athletics matured."
      if _gap else "Filter includes only one gender. Select 'All' to see the gender gap comparison.")),
    ("📈", "Spread Analysis", f"σ = {_std_t} min",
     f"A standard deviation of <b>{_std_t} min</b> reflects how consistently elite runners "
     f"perform near peak times. Lower σ in recent decades shows increasing competitive depth."),
)

fact_banner("🧠",
    f"<b>Statistical insight:</b> Box plots reveal outliers — unusually slow times often correspond "
    f"to early marathon years (pre-1920s) when training science was primitive. The violin plot "
    f"shows the full distribution shape: modern winners cluster in a very tight band near peak performance.")

# ═══════════════════════════════════════════════════════════════
# SECTION 5 — BONUS
# ═══════════════════════════════════════════════════════════════
section("Advanced Visualizations", "Bubble chart, funnel analysis, and pair plot")

col9, col10 = st.columns(2)
with col9:
    st.markdown('<div class="chart-left"><div class="noon-chart">', unsafe_allow_html=True)
    show_chart(plot_bubble_chart, filtered_df, "Bubble Chart")
    st.markdown('</div></div>', unsafe_allow_html=True)
with col10:
    st.markdown('<div class="chart-right"><div class="noon-chart">', unsafe_allow_html=True)
    show_chart(plot_funnel_chart, filtered_df, "Funnel Chart")
    st.markdown('</div></div>', unsafe_allow_html=True)

with st.expander("Pair Plot — Multi-Feature Relationship Analysis", expanded=False):
    show_chart(plot_pairplot, filtered_df, "Pair Plot")

st.markdown('''
<div class="chart-caption"><p>
<b>Bubble Chart</b> — Three dimensions at once: Year (x), Finishing Time (y), Speed (bubble size).
Larger bubbles = faster races. <b>Funnel Chart</b> — Shows progression through performance tiers,
from all records down to elite sub-2:10 performances. <b>Pair Plot</b> — Multi-feature correlation
matrix; the diagonal shows each variable's distribution while off-diagonal shows pairwise relationships.
</p></div>''', unsafe_allow_html=True)

gc.collect()

# Section 5 insights
_avg_pace = round(filtered_df["Pace_Per_Mile"].dropna().mean(), 2) if len(filtered_df) > 0 else 0
_best_pace = round(filtered_df["Pace_Per_Mile"].dropna().min(), 2) if len(filtered_df) > 0 else 0
_top_speed_row = filtered_df.loc[filtered_df["Speed_MPH"].idxmax()] if len(filtered_df) > 0 else None
_top_speed_name = _top_speed_row["Winner"] if _top_speed_row is not None else "N/A"
_top_speed_val  = round(_top_speed_row["Speed_MPH"], 2) if _top_speed_row is not None else 0

insight_cards(
    ("🏃", "Avg Pace Per Mile", f"{_avg_pace} min/mi",
     f"Winners average <b>{_avg_pace} min/mile</b> — that's running each mile in under "
     f"<b>{int(_avg_pace)}:{int((_avg_pace%1)*60):02d}</b>. Sustained over 26.2 miles, this is superhuman."),
    ("⚡", "Fastest Ever Speed", f"{_top_speed_val} mph",
     f"<b>{_top_speed_name}</b> holds the highest recorded speed at <b>{_top_speed_val} mph</b> "
     f"in this dataset. Modern marathon winners run faster than most cyclists on flat roads."),
    ("🔬", "Multi-Feature Analysis", "Pair & Bubble",
     f"The bubble chart maps Year vs Time vs Speed together. The pair plot reveals correlations "
     f"between all numeric features — pace, speed, time, and distance interact in revealing ways."),
)

fact_banner("📌",
    f"<b>Did you know?</b> The Boston Marathon is one of the six <b>World Marathon Majors</b> "
    f"alongside Tokyo, London, Berlin, Chicago, and New York. It is the only major with a "
    f"<b>qualifying standard</b> — you must run a sub-3h (men) or sub-3:30h (women) marathon "
    f"just to enter. The 2011 men's record by <b>Geoffrey Mutai</b> (2:03:02) stood for years "
    f"and remains one of the fastest ever run on a point-to-point course.")

# ═══════════════════════════════════════════════════════════════
# DATA TABLE
# ═══════════════════════════════════════════════════════════════
section("Data Explorer", "Browse and inspect the filtered dataset")

display_cols = ["Year", "Winner", "Country", "Gender", "Time", "Distance (Miles)",
                "Distance (KM)", "Time_Minutes", "Pace_Per_Mile", "Speed_MPH", "Decade_Label"]
available_cols = [c for c in display_cols if c in filtered_df.columns]
st.dataframe(
    filtered_df[available_cols].reset_index(drop=True),
    use_container_width=True,
    height=420,
)


# ═══════════════════════════════════════════════════════════════
# EXPORT SECTION
# ═══════════════════════════════════════════════════════════════
section("Data Export", "Download the filtered dataset for your own analysis")

import io
_export_df = filtered_df[[c for c in ["Year","Winner","Country","Gender","Time","Time_Minutes",
    "Speed_MPH","Pace_Per_Mile","Distance (Miles)","Distance (KM)","Decade_Label"]
    if c in filtered_df.columns]].reset_index(drop=True)

_csv_buf = io.StringIO()
_export_df.to_csv(_csv_buf, index=False)
_csv_bytes = _csv_buf.getvalue().encode()

col_exp1, col_exp2, col_exp3 = st.columns(3)
with col_exp1:
    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=_csv_bytes,
        file_name=f"boston_marathon_filtered_{len(_export_df)}_records.csv",
        mime="text/csv",
        use_container_width=True,
    )
with col_exp2:
    st.download_button(
        label="⬇️ Download Full Dataset CSV",
        data=open("data/Mens_Boston_Marathon_Winners_r0l7bV.csv","rb").read(),
        file_name="boston_marathon_mens_full.csv",
        mime="text/csv",
        use_container_width=True,
    )
with col_exp3:
    st.download_button(
        label="⬇️ Download Women's CSV",
        data=open("data/Womens_Boston_Marathon_Winners_8SSnWb.csv","rb").read(),
        file_name="boston_marathon_womens_full.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ── Quick Summary
st.markdown(f'''
<div class="export-box" style="margin-top:16px;">
    <h4>📊 Quick Summary — Current Filter</h4>
    <div class="info-grid">
        <div class="info-item">
            <div class="info-item-label">Total Records</div>
            <div class="info-item-value">{len(_export_df)}</div>
        </div>
        <div class="info-item">
            <div class="info-item-label">Year Range</div>
            <div class="info-item-value">{int(_export_df["Year"].min())} – {int(_export_df["Year"].max())}</div>
        </div>
        <div class="info-item">
            <div class="info-item-label">Unique Winners</div>
            <div class="info-item-value">{_export_df["Winner"].nunique()}</div>
        </div>
        <div class="info-item">
            <div class="info-item-label">Countries</div>
            <div class="info-item-value">{_export_df["Country"].nunique()}</div>
        </div>
        <div class="info-item">
            <div class="info-item-label">Fastest Time</div>
            <div class="info-item-value">{_export_df["Time_Minutes"].min():.1f} min</div>
        </div>
        <div class="info-item">
            <div class="info-item-label">Avg Speed</div>
            <div class="info-item-value">{_export_df["Speed_MPH"].mean():.2f} mph</div>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# DASHBOARD INFO CARD
# ═══════════════════════════════════════════════════════════════
st.markdown(f'''
<div class="info-card">
    <h4>ℹ️ Dashboard Information</h4>
    <div class="info-grid">
        <div class="info-item">
            <div class="info-item-label">Data Sources</div>
            <div class="info-item-value">Men's (1897–2022) · Women's (1966–2022)</div>
        </div>
        <div class="info-item">
            <div class="info-item-label">Total Records Available</div>
            <div class="info-item-value">{len(df)} race results</div>
        </div>
        <div class="info-item">
            <div class="info-item-label">Chart Types</div>
            <div class="info-item-value">10 visualizations + Pair Plot</div>
        </div>
        <div class="info-item">
            <div class="info-item-label">Country Representation</div>
            <div class="info-item-value">{df["Country"].nunique()} nations across 6 continents</div>
        </div>
        <div class="info-item">
            <div class="info-item-label">Built With</div>
            <div class="info-item-value">Streamlit · Pandas · Matplotlib · Seaborn</div>
        </div>
        <div class="info-item">
            <div class="info-item-label">Race Distance</div>
            <div class="info-item-value">26.2 mi / 42.195 km (standardized 1924)</div>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="noon-footer">
    <p>
        Boston Marathon Data Visualization Dashboard<br>
        Built with <span class="highlight">Streamlit</span> ·
        <span class="highlight">Pandas</span> ·
        <span class="highlight">Matplotlib</span> ·
        <span class="highlight">Seaborn</span>
    </p>
</div>
""", unsafe_allow_html=True)
