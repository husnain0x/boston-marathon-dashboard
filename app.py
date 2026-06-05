"""
app.py — Boston Marathon Elite Dashboard
Cinematic dark theme: deep black + amber/gold glow
Race-themed: route banner, milestones, Hall of Fame, tab nav
"""

import streamlit as st
import pandas as pd
import numpy as np
import gc
import io
from filters import load_and_merge_data, apply_filters
from charts import (
    plot_pie_chart, plot_histogram, plot_line_chart, plot_bar_chart,
    plot_scatter, plot_boxplot, plot_heatmap, plot_area_chart,
    plot_countplot, plot_violin, plot_pairplot, plot_bubble_chart,
    plot_funnel_chart
)

st.set_page_config(
    page_title="Boston Marathon Dashboard",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&display=swap');

:root {
    --bg:      #07070a;
    --bg1:     #0b0b0f;
    --bg2:     #0f0e13;
    --bg3:     #141318;
    --border:  rgba(232,147,58,0.07);
    --border2: rgba(232,147,58,0.15);
    --amber:   #e8933a;
    --amber2:  #f0a852;
    --gold:    #d4a850;
    --orange:  #e07830;
    --tw:      #f5f0e8;
    --tl:      #c8c0b0;
    --td:      #7a7468;
    --tm:      #4a4540;
}

/* ── Base ───────────────────────────────── */
.stApp, html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif;
}
html { scroll-behavior: smooth; }

/* ── Sidebar ─────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #09090d 0%, #0d0c11 100%) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] hr { border-color: var(--border) !important; }
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown h4 {
    color: var(--amber) !important; font-weight: 700 !important;
    font-size: 0.65rem !important; letter-spacing: 2.5px; text-transform: uppercase;
}

/* ── KPI Metrics ─────────────────────────── */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, var(--bg2), var(--bg3));
    border: 1px solid var(--border); border-radius: 16px;
    padding: 22px 20px; transition: all 0.35s ease;
    position: relative; overflow: hidden;
}
div[data-testid="stMetric"]::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(232,147,58,0.18), transparent);
}
div[data-testid="stMetric"]:hover {
    border-color: var(--border2);
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5), 0 0 40px rgba(232,147,58,0.05);
}
div[data-testid="stMetric"] label {
    color: var(--td) !important; font-size: 0.63rem !important;
    font-weight: 700 !important; letter-spacing: 2px; text-transform: uppercase;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--tw) !important; font-size: 1.45rem !important;
    font-weight: 800 !important; letter-spacing: -0.5px;
}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
    color: var(--amber) !important; font-size: 0.68rem !important;
}

/* ── Buttons ─────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #b86a18, var(--amber)) !important;
    color: #07070a !important; border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; font-size: 0.78rem !important;
    letter-spacing: 0.5px !important; transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, var(--amber), var(--amber2)) !important;
    box-shadow: 0 0 28px rgba(232,147,58,0.22) !important;
    transform: translateY(-2px) !important;
}

/* ── Form inputs ─────────────────────────── */
.stSlider > div > div > div > div { background: var(--amber) !important; }
.stSlider label, .stSelectbox label,
.stMultiSelect label, .stTextInput label {
    color: var(--td) !important; font-size: 0.77rem !important; font-weight: 500 !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--bg2) !important; border-color: var(--border) !important;
    color: var(--tl) !important; border-radius: 10px !important;
}
.stTextInput > div > div > input {
    background: var(--bg2) !important; border-color: var(--border) !important;
    color: var(--tl) !important; border-radius: 10px !important;
}

/* ── Charts / Cards ──────────────────────── */
.noon-chart {
    background: linear-gradient(145deg, var(--bg2), var(--bg3));
    border: 1px solid var(--border); border-radius: 18px;
    padding: 8px; margin-bottom: 16px;
    transition: all 0.4s ease; position: relative; overflow: hidden;
}
.noon-chart::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(232,147,58,0.1), transparent);
}
.noon-chart:hover {
    border-color: var(--border2);
    transform: translateY(-2px);
    box-shadow: 0 10px 40px rgba(0,0,0,0.4), 0 0 40px rgba(232,147,58,0.04);
}

/* ── Section headers ─────────────────────── */
.sec-wrap {
    display: flex; align-items: center; gap: 16px;
    margin: 52px 0 26px 0;
}
.sec-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 30px; height: 30px; border-radius: 50%;
    background: linear-gradient(135deg, #b86a18, var(--amber));
    color: #07070a; font-size: 0.72rem; font-weight: 900;
    flex-shrink: 0; box-shadow: 0 0 16px rgba(232,147,58,0.28);
}
.sec-title {
    font-family: 'Playfair Display', serif; font-size: 1.2rem;
    font-weight: 600; color: var(--tw); margin: 0; letter-spacing: -0.3px;
}
.sec-sub { font-size: 0.7rem; color: var(--td); margin: 2px 0 0 0; }
.sec-line {
    flex-grow: 1; height: 1px;
    background: linear-gradient(90deg, rgba(232,147,58,0.14) 0%, transparent 100%);
}

/* ── Caption bars ────────────────────────── */
.cap {
    background: rgba(232,147,58,0.03);
    border: 1px solid rgba(232,147,58,0.06);
    border-radius: 12px; padding: 10px 16px; margin: -8px 0 22px 0;
    font-size: 0.7rem; color: var(--td); line-height: 1.6;
}
.cap b { color: #a89070; }

/* ── Insight cards ───────────────────────── */
.ic-row { display: flex; gap: 12px; margin: 16px 0 28px 0; flex-wrap: wrap; }
.ic {
    flex: 1; min-width: 190px;
    background: linear-gradient(145deg, var(--bg2), var(--bg3));
    border: 1px solid var(--border); border-radius: 14px;
    padding: 16px 18px; position: relative; overflow: hidden;
    transition: border-color 0.3s ease, transform 0.3s ease;
}
.ic:hover { border-color: var(--border2); transform: translateY(-2px); }
.ic::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(232,147,58,0.1), transparent);
}
.ic-lbl { color: var(--tm); font-size: 0.58rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px; }
.ic-val { color: var(--amber); font-size: 1.1rem; font-weight: 800; letter-spacing: -0.3px; margin-bottom: 4px; }
.ic-desc { color: var(--td); font-size: 0.7rem; line-height: 1.5; }
.ic-desc b { color: var(--tl); font-weight: 600; }

/* ── Fact banners ────────────────────────── */
.fb {
    background: linear-gradient(135deg, rgba(232,147,58,0.04), rgba(212,168,80,0.03));
    border: 1px solid rgba(232,147,58,0.09); border-radius: 14px;
    padding: 14px 20px; margin: 8px 0 28px 0;
    display: flex; align-items: flex-start; gap: 12px;
}
.fb-icon { font-size: 1.3rem; flex-shrink: 0; margin-top: 1px; }
.fb-text { color: var(--td); font-size: 0.76rem; line-height: 1.6; }
.fb-text b { color: var(--amber); }

/* ── Hall of Fame ────────────────────────── */
.hof-wrap { display: flex; gap: 10px; flex-wrap: wrap; margin: 0 0 30px 0; }
.hof-card {
    flex: 1; min-width: 130px;
    background: linear-gradient(145deg, var(--bg2), var(--bg3));
    border: 1px solid var(--border); border-radius: 14px;
    padding: 16px 14px; text-align: center;
    position: relative; overflow: hidden;
    transition: border-color 0.3s ease, transform 0.3s ease;
}
.hof-card:hover { border-color: var(--border2); transform: translateY(-3px); }
.hof-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(232,147,58,0.2), transparent);
}
.hof-rank { font-size: 0.58rem; color: var(--tm); font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px; }
.hof-medal { font-size: 1.5rem; margin-bottom: 6px; }
.hof-name { color: var(--tw); font-size: 0.78rem; font-weight: 700; margin-bottom: 3px; line-height: 1.3; }
.hof-country { color: var(--td); font-size: 0.65rem; margin-bottom: 8px; }
.hof-wins { color: var(--amber); font-size: 1.4rem; font-weight: 900; letter-spacing: -1px; }
.hof-wins-lbl { color: var(--tm); font-size: 0.58rem; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; }

/* ── Route Banner ────────────────────────── */
.route-banner {
    background: linear-gradient(135deg, var(--bg1) 0%, #0d0b10 50%, var(--bg1) 100%);
    border: 1px solid var(--border); border-radius: 20px;
    padding: 28px 32px; margin: 0 0 10px 0; position: relative; overflow: hidden;
}
.route-banner::before {
    content: '26.2'; position: absolute; right: 24px; top: 50%; transform: translateY(-50%);
    font-size: 6rem; font-weight: 900; color: rgba(232,147,58,0.04);
    letter-spacing: -4px; line-height: 1; pointer-events: none;
}
.route-eyebrow {
    font-size: 0.6rem; font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; color: var(--amber); margin-bottom: 8px;
}
.route-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.9rem; font-weight: 800; color: var(--tw);
    letter-spacing: -0.5px; margin: 0 0 4px 0; line-height: 1.1;
}
.route-title span { color: var(--amber); }
.route-subtitle { color: var(--td); font-size: 0.78rem; margin: 0 0 20px 0; }
.route-line-wrap { display: flex; align-items: center; gap: 0; margin-bottom: 8px; }
.route-dot-s {
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--amber); flex-shrink: 0;
    box-shadow: 0 0 10px rgba(232,147,58,0.5);
}
.route-path { flex: 1; position: relative; height: 3px; margin: 0 4px; }
.route-path-line {
    width: 100%; height: 100%;
    background: linear-gradient(90deg, var(--amber) 0%, #c47520 40%, #6a3a0a 70%, rgba(232,147,58,0.15) 100%);
    border-radius: 2px;
}
.route-hill-marker {
    position: absolute; top: -22px; left: 72%;
    transform: translateX(-50%); text-align: center;
}
.route-hill-label {
    background: rgba(232,70,50,0.12); border: 1px solid rgba(232,70,50,0.2);
    color: #e84632; font-size: 0.5rem; font-weight: 700; letter-spacing: 1px;
    padding: 2px 6px; border-radius: 4px; white-space: nowrap; text-transform: uppercase;
}
.route-dot-e {
    width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
    border: 2px solid rgba(232,147,58,0.35); background: rgba(232,147,58,0.08);
}
.route-stops { display: flex; justify-content: space-between; margin-top: 4px; }
.route-stop { font-size: 0.6rem; color: var(--tm); }
.route-stop.active { color: var(--amber); }

/* ── Milestone strip ─────────────────────── */
.ms-strip { display: flex; gap: 8px; margin: 18px 0 32px 0; flex-wrap: wrap; }
.ms {
    flex: 1; min-width: 140px;
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 12px; padding: 14px; position: relative; overflow: hidden;
}
.ms::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 2px;
    background: linear-gradient(180deg, var(--amber), transparent);
}
.ms-year { color: var(--amber); font-size: 0.72rem; font-weight: 800; margin-bottom: 4px; }
.ms-text { color: var(--td); font-size: 0.67rem; line-height: 1.5; }
.ms-text b { color: var(--tl); }

/* ── Overview card ───────────────────────── */
.ov-card {
    background: linear-gradient(145deg, var(--bg2), var(--bg3));
    border: 1px solid var(--border); border-radius: 16px;
    padding: 22px 26px; margin-bottom: 28px; position: relative; overflow: hidden;
}
.ov-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(232,147,58,0.14), transparent);
}
.ov-lbl { color: var(--amber); font-size: 0.6rem; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 10px; }
.ov-text { color: #8a8278; font-size: 0.79rem; line-height: 1.72; margin: 0; }
.ov-text b { color: var(--tl); }
.ov-tags { margin-top: 14px; }
.ov-tag {
    display: inline-block; background: rgba(232,147,58,0.07);
    border: 1px solid rgba(232,147,58,0.13); color: var(--amber);
    padding: 3px 10px; border-radius: 100px; font-size: 0.6rem;
    font-weight: 600; letter-spacing: 1px; margin: 2px 3px 0 0;
}

/* ── Info / Export cards ─────────────────── */
.info-card, .export-card {
    background: linear-gradient(145deg, var(--bg2), var(--bg3));
    border: 1px solid var(--border); border-radius: 16px;
    padding: 22px 26px; margin: 10px 0 28px 0;
}
.info-card h4, .export-card h4 {
    color: var(--amber); font-size: 0.6rem; font-weight: 700;
    letter-spacing: 2.5px; text-transform: uppercase; margin: 0 0 16px 0;
}
.info-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 14px;
}
.ig-lbl { color: var(--tm); font-size: 0.58rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 3px; }
.ig-val { color: var(--tl); font-size: 0.77rem; font-weight: 500; }

/* ── Footer ──────────────────────────────── */
.footer {
    text-align: center; padding: 36px 0; margin-top: 40px;
    border-top: 1px solid var(--border);
}
.footer p { color: var(--tm); font-size: 0.73rem; letter-spacing: 0.4px; line-height: 1.7; }
.footer b { color: var(--amber); font-weight: 600; }

/* ── Misc ────────────────────────────────── */
#MainMenu, footer, .stDeployButton { visibility: hidden; display: none; }
button[title="View fullscreen"] { display: none !important; }
.stSpinner > div { border-color: var(--amber) !important; }
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 14px !important; }
details {
    background: var(--bg2) !important; border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}
details summary { color: var(--amber) !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)


# ── Data ─────────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_and_merge_data()

try:
    df = get_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='text-align:center;padding:24px 0 16px 0;'>
    <div style='width:52px;height:52px;margin:0 auto 12px;
         background:rgba(232,147,58,0.08);border:1px solid rgba(232,147,58,0.18);
         border-radius:14px;display:flex;align-items:center;justify-content:center;'>
        <span style='font-size:1.6rem;line-height:1;'>🏃</span>
    </div>
    <h2 style='margin:0;font-family:Playfair Display,serif;color:#f5f0e8;
        font-size:1.1rem;font-weight:700;letter-spacing:-0.3px;'>Boston Marathon</h2>
    <p style='color:#4a4540;font-size:0.6rem;margin:5px 0 0;
       letter-spacing:2.5px;text-transform:uppercase;font-weight:700;'>Elite Dashboard</p>
</div>
""", unsafe_allow_html=True)

filtered_df = apply_filters(df)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='background:var(--bg2,#0f0e13);border:1px solid rgba(232,147,58,0.08);
     border-radius:14px;padding:16px;text-align:center;position:relative;overflow:hidden;'>
    <div style='position:absolute;top:0;left:0;right:0;height:1px;
         background:linear-gradient(90deg,transparent,rgba(232,147,58,0.12),transparent);'></div>
    <span style='color:#4a4540;font-size:0.58rem;text-transform:uppercase;
           letter-spacing:2px;font-weight:700;'>Active Records</span><br>
    <span style='color:#e8933a;font-size:2.1rem;font-weight:900;
           letter-spacing:-1px;'>{len(filtered_df)}</span>
    <span style='color:#2a2520;font-size:0.9rem;font-weight:500;'> / {len(df)}</span>
    <br><span style='color:#3a3530;font-size:0.6rem;'>of total dataset</span>
</div>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def mins_to_hms(m):
    try:
        h, mi, s = int(m//60), int(m%60), int((m%1)*60)
        return f"{h}:{mi:02d}:{s:02d}"
    except:
        return "N/A"

_sec_n = [0]
def section(title, subtitle):
    _sec_n[0] += 1
    st.markdown(f"""
    <div class="sec-wrap">
        <div class="sec-badge">{_sec_n[0]}</div>
        <div>
            <p class="sec-title">{title}</p>
            <p class="sec-sub">{subtitle}</p>
        </div>
        <div class="sec-line"></div>
    </div>""", unsafe_allow_html=True)

def chart(fn, data, name="Chart"):
    try:
        b = fn(data)
        if b: st.image(b, use_container_width=True)
        else: st.info(f"No data for {name}")
    except Exception as e:
        st.warning(f"Could not render {name}: {str(e)[:80]}")
    finally:
        gc.collect()

def ics(*cards):
    rows = "".join(f"""<div class="ic">
        <div class="ic-lbl">{lbl}</div>
        <div class="ic-val">{val}</div>
        <div class="ic-desc">{desc}</div>
    </div>""" for lbl, val, desc in cards)
    st.markdown(f'<div class="ic-row">{rows}</div>', unsafe_allow_html=True)

def fb(icon, text):
    st.markdown(f"""<div class="fb">
        <div class="fb-icon">{icon}</div>
        <div class="fb-text">{text}</div>
    </div>""", unsafe_allow_html=True)

def cap(text):
    st.markdown(f'<div class="cap">{text}</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No data matches the current filters. Adjust the filter criteria.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# RACE ROUTE HERO BANNER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="route-banner">
    <div class="route-eyebrow">Est. 1897 · Patriots Day · Every April · Boston, MA</div>
    <h1 class="route-title">Boston <span>Marathon</span> Analytics</h1>
    <p class="route-subtitle">127 years of champions — from Hopkinton to the Boylston Street finish line</p>
    <div class="route-line-wrap">
        <div class="route-dot-s"></div>
        <div class="route-path">
            <div class="route-path-line"></div>
            <div class="route-hill-marker">
                <div class="route-hill-label">⚡ Heartbreak Hill · Mile 20</div>
            </div>
        </div>
        <div class="route-dot-e"></div>
    </div>
    <div class="route-stops">
        <span class="route-stop active">START · Hopkinton</span>
        <span class="route-stop">· · · 26.2 miles · · ·</span>
        <span class="route-stop">FINISH · Boylston St, Boston</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MILESTONE TIMELINE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="ms-strip">
    <div class="ms">
        <div class="ms-year">1897</div>
        <div class="ms-text"><b>First Boston Marathon.</b> 15 runners. John McDermott wins in 2:55:10 — a legend is born.</div>
    </div>
    <div class="ms">
        <div class="ms-year">1924</div>
        <div class="ms-text"><b>Standard distance set</b> at 26.2 miles (42.195 km) after Olympic standardization.</div>
    </div>
    <div class="ms">
        <div class="ms-year">1967</div>
        <div class="ms-text"><b>Kathrine Switzer</b> runs as the first numbered woman, RD tries to remove her mid-race.</div>
    </div>
    <div class="ms">
        <div class="ms-year">1972</div>
        <div class="ms-text"><b>Women officially allowed.</b> Nina Kuscsik wins the first official women's division.</div>
    </div>
    <div class="ms">
        <div class="ms-year">1990s</div>
        <div class="ms-text"><b>Kenyan dominance begins.</b> East African runners redefine what's possible in distance running.</div>
    </div>
    <div class="ms">
        <div class="ms-year">2011</div>
        <div class="ms-text"><b>Geoffrey Mutai</b> sets course record of 2:03:02 — one of the fastest marathons ever run.</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW CARD
# ══════════════════════════════════════════════════════════════════════════════
_tc = df["Country"].nunique()
st.markdown(f"""
<div class="ov-card">
    <div class="ov-lbl">📋 Dashboard Overview</div>
    <p class="ov-text">
        This dashboard explores <b>{len(df)} historical race results</b> from the world's oldest annual marathon,
        held every <b>Patriots' Day</b> since <b>1897</b>. Covering
        <b>Men's records ({int(df[df['Gender']=='Male']['Year'].min())}–{int(df[df['Gender']=='Male']['Year'].max())})</b> and
        <b>Women's records ({int(df[df['Gender']=='Female']['Year'].min())}–{int(df[df['Gender']=='Female']['Year'].max())})</b>,
        spanning <b>{_tc} nations</b> across 6 continents.
        Use the sidebar to filter by year, gender, finishing time, country, or winner name.
    </p>
    <div class="ov-tags">
        <span class="ov-tag">🏃 {len(df[df['Gender']=='Male'])} Men's Records</span>
        <span class="ov-tag">🚺 {len(df[df['Gender']=='Female'])} Women's Records</span>
        <span class="ov-tag">🌍 {_tc} Nations</span>
        <span class="ov-tag">📅 {int(df['Year'].max()) - int(df['Year'].min())} Year Span</span>
        <span class="ov-tag">📊 10 Chart Types</span>
        <span class="ov-tag">⚡ Live Filters</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════
td = filtered_df["Time_Minutes"].dropna()
avg_t = td.mean() if len(td) else 0
fast_t = td.min() if len(td) else 0
fast_row = filtered_df.loc[filtered_df["Time_Minutes"].idxmin()] if len(td) else None
avg_spd = filtered_df["Speed_MPH"].dropna().mean() if len(filtered_df) else 0
yr_span = f"{int(filtered_df['Year'].min())}–{int(filtered_df['Year'].max())}"

k1, k2, k3 = st.columns(3)
k1.metric("Total Records", f"{len(filtered_df)}", delta=f"{filtered_df['Gender'].nunique()} gender categories")
k2.metric("Year Span", yr_span)
k3.metric("Avg Finish Time", mins_to_hms(avg_t))

k4, k5, k6 = st.columns(3)
k4.metric("Course Record", mins_to_hms(fast_t), delta=fast_row["Winner"] if fast_row is not None else "")
k5.metric("Nations Represented", f"{filtered_df['Country'].nunique()}")
k6.metric("Avg Winning Speed", f"{avg_spd:.2f} mph")


# ══════════════════════════════════════════════════════════════════════════════
# HALL OF FAME
# ══════════════════════════════════════════════════════════════════════════════
section("Hall of Fame", "Most decorated champions in Boston Marathon history")

_wins = filtered_df.groupby("Winner").agg(
    wins=("Year", "count"),
    country=("Country", "first"),
    first=("Year", "min"),
    last=("Year", "max")
).sort_values("wins", ascending=False).head(5).reset_index()

medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]
rank_lbl = ["1ST", "2ND", "3RD", "4TH", "5TH"]

hof_cards = "".join(f"""
<div class="hof-card">
    <div class="hof-rank">{rank_lbl[i]}</div>
    <div class="hof-medal">{medals[i]}</div>
    <div class="hof-name">{row['Winner']}</div>
    <div class="hof-country">{row['country']} · {int(row['first'])}–{int(row['last'])}</div>
    <div class="hof-wins">{row['wins']}</div>
    <div class="hof-wins-lbl">Wins</div>
</div>""" for i, row in _wins.iterrows() if i < 5)

st.markdown(f'<div class="hof-wrap">{hof_cards}</div>', unsafe_allow_html=True)

fb("🏆",
   "<b>Clarence DeMar</b> won Boston 7 times (1911–1930) — a record that stood for nearly a century. "
   "Modern Kenyan runners like <b>Robert Kipkoech Cheruiyot</b> (4 wins) dominate the modern era. "
   "The Hall of Fame updates dynamically with your current filters.")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — OVERVIEW & COMPOSITION
# ══════════════════════════════════════════════════════════════════════════════
section("Overview & Composition", "National dominance patterns and finishing time distribution")

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
    chart(plot_pie_chart, filtered_df, "Pie Chart")
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
    chart(plot_histogram, filtered_df, "Histogram")
    st.markdown('</div>', unsafe_allow_html=True)

cap("<b>Winners by Country</b> — Donut chart reveals national dominance at a glance. "
    "<b>Finishing Time Distribution</b> — Histogram shows elite performance clustering; "
    "the long right tail represents early-era races before modern training science and carbon-fiber shoe technology.")

_tc2 = filtered_df["Country"].value_counts()
_top_c = _tc2.index[0] if len(_tc2) else "N/A"
_top_n = _tc2.iloc[0] if len(_tc2) else 0
_pct = round(_top_n / len(filtered_df) * 100, 1) if len(filtered_df) else 0
_mode_t = int(filtered_df["Time_Minutes"].dropna().mode().iloc[0]) if len(filtered_df) else 0

ics(
    ("Dominant Nation", _top_c,
     f"Won <b>{_top_n}</b> races — <b>{_pct}%</b> of all filtered records. "
     f"<b>{filtered_df['Country'].nunique()}</b> nations have claimed the Boston finish line."),
    ("Most Common Finish", f"~{_mode_t} min",
     f"Elite times cluster tightly near <b>{_mode_t} min</b> ({_mode_t//60}h {_mode_t%60}m). "
     f"Modern winners are within 5–10 minutes of the all-time record."),
    ("Dataset Snapshot", f"{len(filtered_df)} records",
     f"<b>{len(filtered_df)}</b> results across <b>{filtered_df['Year'].nunique()}</b> years "
     f"and <b>{filtered_df['Gender'].nunique()}</b> gender categor{'y' if filtered_df['Gender'].nunique()==1 else 'ies'}."),
)
gc.collect()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — PERFORMANCE TRENDS
# ══════════════════════════════════════════════════════════════════════════════
section("Performance Trends", "How winning times evolved — and why the decline accelerated post-1970")

st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
chart(plot_line_chart, filtered_df, "Line Chart")
st.markdown('</div>', unsafe_allow_html=True)

c3, c4 = st.columns(2)
with c3:
    st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
    chart(plot_scatter, filtered_df, "Scatter")
    st.markdown('</div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
    chart(plot_area_chart, filtered_df, "Area Chart")
    st.markdown('</div>', unsafe_allow_html=True)

cap("<b>Line Chart</b> — Amber = Men, Red = Women. The steady decline reflects advances in training, nutrition, "
    "altitude prep, and super-shoes. <b>Scatter + Regression</b> — Dashed line is a polynomial best-fit showing "
    "the long-term trajectory. <b>Area Chart</b> — Cumulative wins; the women's curve only starts in 1966.")

_fast = filtered_df["Time_Minutes"].min() if len(td) else 0
_slow = filtered_df["Time_Minutes"].max() if len(td) else 0
_imp = round(_slow - _fast, 1)
_aspd = round(filtered_df["Speed_MPH"].dropna().mean(), 2) if len(filtered_df) else 0
_fast_row = filtered_df.loc[filtered_df["Time_Minutes"].idxmin()] if len(td) else None

def fmt(m):
    try: return f"{int(m//60)}h {int(m%60)}m {int((m%1)*60)}s"
    except: return "N/A"

ics(
    ("Course Record", fmt(_fast),
     f"Set in <b>{int(_fast_row['Year'])}</b> by <b>{_fast_row['Winner']}</b>. "
     f"Marathon records are driven by optimal conditions, pacing, and competition."),
    ("Total Improvement", f"{_imp:.1f} min",
     f"Winning times improved by <b>{_imp:.1f} minutes</b> across the dataset. "
     f"Better training, nutrition science, and race-day technology fuel this decline."),
    ("Avg Winning Speed", f"{_aspd} mph",
     f"Winners average <b>{_aspd} mph</b> across 26.2 miles — "
     f"roughly <b>{round(60/_aspd*26.2,1) if _aspd else 'N/A'} min total</b> at a relentless pace."),
)

fb("💡",
   "The Boston Marathon is held every <b>Patriots' Day</b> in April. "
   "The infamous <b>Heartbreak Hill</b> (miles 20–21) is a series of four hills in Newton — "
   "coming when runners are already fatigued, it has crushed more race strategies than any single factor. "
   "Elite runners specifically train for this section; pacing at Heartbreak Hill often decides the race.")

gc.collect()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — COMPARISONS & RANKINGS
# ══════════════════════════════════════════════════════════════════════════════
section("Comparisons & Rankings", "National standings, decade-by-decade breakdowns, and era analysis")

c5, c6 = st.columns(2)
with c5:
    st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
    chart(plot_bar_chart, filtered_df, "Bar Chart")
    st.markdown('</div>', unsafe_allow_html=True)
with c6:
    st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
    chart(plot_countplot, filtered_df, "Count Plot")
    st.markdown('</div>', unsafe_allow_html=True)

cap("<b>Country Rankings</b> — USA dominated early eras; Japan surged mid-century; Kenya and Ethiopia "
    "have dominated since the 1990s with East African runners pioneering altitude training. "
    "<b>Wins Per Decade</b> — Grouped by gender; the women's field only appears from the 1960s onward.")

_t3 = filtered_df["Country"].value_counts().head(3)
_t3s = ", ".join([f"<b>{c}</b> ({n})" for c, n in _t3.items()])
_bd = filtered_df["Decade_Label"].value_counts()
_bdn, _bdc = (_bd.index[0], _bd.iloc[0]) if len(_bd) else ("N/A", 0)
_uw = filtered_df["Winner"].nunique()

ics(
    ("Top 3 Nations", "",
     f"The podium: {_t3s}. These nations have shaped every era of Boston history."),
    ("Most Active Decade", _bdn,
     f"The <b>{_bdn}</b> had the most winners in this selection (<b>{_bdc} races</b>). "
     f"Decade trends reveal how competition depth evolved over 127 years."),
    ("Unique Champions", f"{_uw}",
     f"<b>{_uw}</b> different athletes won across filtered records. "
     f"<b>Clarence DeMar</b> leads all-time with 7 wins (1911–1930)."),
)
gc.collect()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — STATISTICAL DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════════
section("Statistical Distribution", "Spread, density, outlier analysis, and feature correlations")

c7, c8 = st.columns(2)
with c7:
    st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
    chart(plot_boxplot, filtered_df, "Box Plot")
    st.markdown('</div>', unsafe_allow_html=True)
with c8:
    st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
    chart(plot_violin, filtered_df, "Violin")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
chart(plot_heatmap, filtered_df, "Heatmap")
st.markdown('</div>', unsafe_allow_html=True)

cap("<b>Box Plot</b> — IQR reveals spread per gender; outliers (dots beyond whiskers) are often early-era races. "
    "<b>Violin Plot</b> — Adds full density shape; wider = more races at that time. Modern winners cluster tightly. "
    "<b>Correlation Heatmap</b> — Strong negative Year↔Time correlation: as years increase, times decrease. "
    "Speed and Pace are perfectly inverse by definition.")

_med = round(filtered_df["Time_Minutes"].dropna().median(), 1)
_std = round(filtered_df["Time_Minutes"].dropna().std(), 1)
_ma = round(filtered_df[filtered_df["Gender"]=="Male"]["Time_Minutes"].mean(), 1) if "Male" in filtered_df["Gender"].values else None
_fa = round(filtered_df[filtered_df["Gender"]=="Female"]["Time_Minutes"].mean(), 1) if "Female" in filtered_df["Gender"].values else None
_gap = round(_fa - _ma, 1) if (_ma and _fa) else None

ics(
    ("Median Finish", f"{_med} min",
     f"Median of <b>{_med} min</b> ({int(_med//60)}h {int(_med%60)}m). "
     f"Standard deviation of <b>{_std} min</b> shows how tightly elite performances cluster."),
    ("Gender Gap", f"{_gap} min" if _gap else "Single gender",
     (f"Men avg <b>{_ma} min</b>, Women avg <b>{_fa} min</b> — gap of <b>{_gap} min</b>. "
      f"This gap has narrowed dramatically since the 1970s as women's athletics matured."
      if _gap else "Select 'All' in gender filter to see the gap comparison.")),
    ("Spread (σ)", f"{_std} min",
     f"σ = <b>{_std} min</b> reflects competitive consistency. "
     f"Lower σ in recent decades proves the field is getting deeper and faster simultaneously."),
)

fb("🧠",
   "<b>Statistical note:</b> Outliers in the box plot are typically pre-1924 races when the official distance "
   "hadn't yet been standardized at 26.2 miles. Early races used varying distances, making direct comparisons "
   "tricky — the data includes distance columns so you can filter accordingly.")

gc.collect()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — ADVANCED VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════════════
section("Advanced Visualizations", "Multi-dimensional analysis — speed, pace, time, and performance tiers")

c9, c10 = st.columns(2)
with c9:
    st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
    chart(plot_bubble_chart, filtered_df, "Bubble")
    st.markdown('</div>', unsafe_allow_html=True)
with c10:
    st.markdown('<div class="noon-chart">', unsafe_allow_html=True)
    chart(plot_funnel_chart, filtered_df, "Funnel")
    st.markdown('</div>', unsafe_allow_html=True)

with st.expander("🔬 Pair Plot — Multi-Feature Relationship Matrix", expanded=False):
    chart(plot_pairplot, filtered_df, "Pair Plot")

cap("<b>Bubble Chart</b> — Year (x), Time (y), bubble size = Speed. Larger = faster. "
    "<b>Funnel / Bracket</b> — Performance tiers from slowest to fastest. Most winners cluster in 2:20–2:50. "
    "<b>Pair Plot</b> — Every feature vs every other feature. The Year↔Time diagonal trend is the clearest signal.")

_ap = round(filtered_df["Pace_Per_Mile"].dropna().mean(), 2) if len(filtered_df) else 0
_tsrow = filtered_df.loc[filtered_df["Speed_MPH"].idxmax()] if len(filtered_df) else None
_tsn = _tsrow["Winner"] if _tsrow is not None else "N/A"
_tsv = round(_tsrow["Speed_MPH"], 2) if _tsrow is not None else 0

ics(
    ("Avg Pace / Mile", f"{_ap} min/mi",
     f"Winners average <b>{_ap} min/mile</b> — each mile in under "
     f"<b>{int(_ap)}:{int((_ap%1)*60):02d}</b>. Sustained over 26.2 miles, it's superhuman."),
    ("Top Speed on Record", f"{_tsv} mph",
     f"<b>{_tsn}</b> holds the highest recorded speed at <b>{_tsv} mph</b>. "
     f"Modern supershoes (Nike Vaporfly, Adidas Adizero) add ~4 min to a marathon."),
    ("Dimensional Analysis", "3D insight",
     f"Bubble chart maps 3 variables simultaneously — year, time, speed. "
     f"The funnel shows only <b>{len(filtered_df[filtered_df['Time_Minutes'] < 130])}</b> sub-2:10 performances exist."),
)

fb("📌",
   "<b>Did you know?</b> Boston is one of six <b>World Marathon Majors</b> (Tokyo, London, Berlin, Chicago, NYC). "
   "It's the only major with a <b>qualifying standard</b> — you must run sub-3h (men) or sub-3:30h (women) first. "
   "The race attracts ~30,000 runners annually with ~500,000 spectators lining the route.")

gc.collect()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — DATA EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
section("Data Explorer", "Browse, inspect, and download the filtered dataset")

disp = [c for c in ["Year","Winner","Country","Gender","Time","Distance (Miles)",
                     "Distance (KM)","Time_Minutes","Pace_Per_Mile","Speed_MPH","Decade_Label"]
        if c in filtered_df.columns]
st.dataframe(filtered_df[disp].reset_index(drop=True), use_container_width=True, height=400)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — EXPORT
# ══════════════════════════════════════════════════════════════════════════════
section("Data Export", "Download filtered or full datasets for your own analysis")

_edf = filtered_df[[c for c in ["Year","Winner","Country","Gender","Time","Time_Minutes",
    "Speed_MPH","Pace_Per_Mile","Distance (Miles)","Distance (KM)","Decade_Label"]
    if c in filtered_df.columns]].reset_index(drop=True)
_cbuf = io.StringIO()
_edf.to_csv(_cbuf, index=False)
_cbytes = _cbuf.getvalue().encode()

ex1, ex2, ex3 = st.columns(3)
with ex1:
    st.download_button("⬇️ Download Filtered CSV", _cbytes,
        f"boston_filtered_{len(_edf)}_records.csv", "text/csv", use_container_width=True)
with ex2:
    st.download_button("⬇️ Download Men's Full CSV",
        open("data/Mens_Boston_Marathon_Winners_r0l7bV.csv","rb").read(),
        "boston_mens_full.csv", "text/csv", use_container_width=True)
with ex3:
    st.download_button("⬇️ Download Women's Full CSV",
        open("data/Womens_Boston_Marathon_Winners_8SSnWb.csv","rb").read(),
        "boston_womens_full.csv", "text/csv", use_container_width=True)

st.markdown(f"""
<div class="export-card" style="margin-top:16px;">
    <h4>📊 Quick Summary — Current Filter</h4>
    <div class="info-grid">
        <div><div class="ig-lbl">Total Records</div><div class="ig-val">{len(_edf)}</div></div>
        <div><div class="ig-lbl">Year Range</div><div class="ig-val">{int(_edf['Year'].min())} – {int(_edf['Year'].max())}</div></div>
        <div><div class="ig-lbl">Unique Winners</div><div class="ig-val">{_edf['Winner'].nunique()}</div></div>
        <div><div class="ig-lbl">Countries</div><div class="ig-val">{_edf['Country'].nunique()}</div></div>
        <div><div class="ig-lbl">Fastest Time</div><div class="ig-val">{_edf['Time_Minutes'].min():.1f} min</div></div>
        <div><div class="ig-lbl">Avg Speed</div><div class="ig-val">{_edf['Speed_MPH'].mean():.2f} mph</div></div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD INFO CARD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="info-card">
    <h4>ℹ️ Dashboard Information</h4>
    <div class="info-grid">
        <div><div class="ig-lbl">Data Sources</div><div class="ig-val">Men's (1897–2022) · Women's (1966–2022)</div></div>
        <div><div class="ig-lbl">Total Records</div><div class="ig-val">{len(df)} race results</div></div>
        <div><div class="ig-lbl">Visualizations</div><div class="ig-val">13 chart types across 7 sections</div></div>
        <div><div class="ig-lbl">Nations</div><div class="ig-val">{df['Country'].nunique()} countries across 6 continents</div></div>
        <div><div class="ig-lbl">Race Distance</div><div class="ig-val">26.2 mi / 42.195 km (standard since 1924)</div></div>
        <div><div class="ig-lbl">Built With</div><div class="ig-val">Streamlit · Pandas · Matplotlib · Seaborn</div></div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
    <p>
        <b>Boston Marathon</b> Elite Analytics Dashboard<br>
        Built with <b>Streamlit</b> · <b>Pandas</b> · <b>Matplotlib</b> · <b>Seaborn</b><br>
        Data covers <b>1897–2022</b> · Patriots Day · Hopkinton → Boylston Street · 26.2 Miles
    </p>
</div>
""", unsafe_allow_html=True)
