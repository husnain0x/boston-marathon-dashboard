"""
app.py — Boston Marathon Elite Dashboard
Architecture: Streamlit passes live data → injected HTML/JS renders cinematic UI
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import gc
from filters import load_and_merge_data, apply_filters
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Boston Marathon",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Minimal Streamlit chrome CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
:root{--amber:#e8933a;--bg:#07070a;}
.stApp,html,body,[data-testid="stAppViewContainer"],[data-testid="stAppViewBlockContainer"]{
    background:#07070a!important;font-family:'Inter',sans-serif;}
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#09090d,#0d0c11)!important;
    border-right:1px solid rgba(232,147,58,0.08);}
section[data-testid="stSidebar"] hr{border-color:rgba(232,147,58,0.08)!important;}
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown h4{
    color:#e8933a!important;font-weight:700!important;
    font-size:0.63rem!important;letter-spacing:2.5px;text-transform:uppercase;}
div[data-testid="stMetric"]{
    background:linear-gradient(145deg,#0f0e13,#141318);
    border:1px solid rgba(232,147,58,0.08);border-radius:16px;
    padding:20px 18px;transition:all 0.35s ease;position:relative;overflow:hidden;}
div[data-testid="stMetric"]::before{
    content:'';position:absolute;top:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,rgba(232,147,58,0.2),transparent);}
div[data-testid="stMetric"]:hover{
    border-color:rgba(232,147,58,0.2);transform:translateY(-3px);
    box-shadow:0 12px 40px rgba(0,0,0,0.5),0 0 30px rgba(232,147,58,0.05);}
div[data-testid="stMetric"] label{
    color:#7a7468!important;font-size:0.6rem!important;
    font-weight:700!important;letter-spacing:2px;text-transform:uppercase;}
div[data-testid="stMetric"] div[data-testid="stMetricValue"]{
    color:#f5f0e8!important;font-size:1.4rem!important;
    font-weight:800!important;letter-spacing:-0.5px;}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"]{
    color:#e8933a!important;font-size:0.65rem!important;}
.stButton>button{
    background:linear-gradient(135deg,#b86a18,#e8933a)!important;
    color:#07070a!important;border:none!important;border-radius:10px!important;
    font-weight:700!important;font-size:0.78rem!important;letter-spacing:0.5px!important;}
.stButton>button:hover{
    background:linear-gradient(135deg,#e8933a,#f0a852)!important;
    box-shadow:0 0 25px rgba(232,147,58,0.2)!important;transform:translateY(-2px)!important;}
.stSlider>div>div>div>div{background:#e8933a!important;}
.stSelectbox>div>div,.stMultiSelect>div>div{
    background:#0f0e13!important;border-color:rgba(232,147,58,0.1)!important;
    color:#c8c0b0!important;border-radius:10px!important;}
.stTextInput>div>div>input{
    background:#0f0e13!important;border-color:rgba(232,147,58,0.1)!important;
    color:#c8c0b0!important;border-radius:10px!important;}
#MainMenu,footer,.stDeployButton{visibility:hidden;display:none;}
button[title="View fullscreen"]{display:none!important;}
.stDataFrame{border:1px solid rgba(232,147,58,0.07)!important;border-radius:14px!important;}
details{background:#0f0e13!important;border:1px solid rgba(232,147,58,0.07)!important;border-radius:14px!important;}
details summary{color:#e8933a!important;font-weight:600!important;}
.stSpinner>div{border-color:#e8933a!important;}
.block-container{padding-top:1rem!important;}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_and_merge_data()

try:
    df = get_data()
except Exception as e:
    st.error(f"Data load error: {e}")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='text-align:center;padding:22px 0 14px;'>
    <div style='width:50px;height:50px;margin:0 auto 10px;background:rgba(232,147,58,0.08);
         border:1px solid rgba(232,147,58,0.2);border-radius:14px;
         display:flex;align-items:center;justify-content:center;font-size:1.5rem;'>🏃</div>
    <h2 style='margin:0;font-family:Georgia,serif;color:#f5f0e8;font-size:1.05rem;font-weight:700;'>Boston Marathon</h2>
    <p style='color:#4a4540;font-size:0.58rem;margin:4px 0 0;letter-spacing:2.5px;text-transform:uppercase;font-weight:700;'>Elite Dashboard</p>
</div>
""", unsafe_allow_html=True)

filtered_df = apply_filters(df)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='background:#0f0e13;border:1px solid rgba(232,147,58,0.08);border-radius:14px;
     padding:14px;text-align:center;position:relative;overflow:hidden;'>
    <div style='position:absolute;top:0;left:0;right:0;height:1px;
         background:linear-gradient(90deg,transparent,rgba(232,147,58,0.14),transparent);'></div>
    <span style='color:#4a4540;font-size:0.56rem;text-transform:uppercase;letter-spacing:2px;font-weight:700;'>Active Records</span><br>
    <span style='color:#e8933a;font-size:2rem;font-weight:900;letter-spacing:-1px;'>{len(filtered_df)}</span>
    <span style='color:#2a2520;font-size:0.85rem;'> / {len(df)}</span>
</div>
""", unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No data matches your filters.")
    st.stop()

# ── Helpers ───────────────────────────────────────────────────────────────────
def mins_to_hms(m):
    try: return f"{int(m//60)}:{int(m%60):02d}:{int((m%1)*60):02d}"
    except: return "N/A"

def safe_val(x, fallback="N/A"):
    try: return x if pd.notna(x) else fallback
    except: return fallback

# ── Compute stats for JS ──────────────────────────────────────────────────────
td = filtered_df["Time_Minutes"].dropna()
avg_t   = float(td.mean()) if len(td) else 0
fast_t  = float(td.min())  if len(td) else 0
slow_t  = float(td.max())  if len(td) else 0
fast_row = filtered_df.loc[filtered_df["Time_Minutes"].idxmin()] if len(td) else None
avg_spd = float(filtered_df["Speed_MPH"].dropna().mean()) if len(filtered_df) else 0
med_t   = float(td.median()) if len(td) else 0

# Trend line data (year vs avg time)
trend = filtered_df.dropna(subset=["Time_Minutes"]).groupby("Year")["Time_Minutes"].mean().reset_index()
trend_years  = trend["Year"].astype(int).tolist()
trend_men    = filtered_df[filtered_df["Gender"]=="Male"].dropna(subset=["Time_Minutes"]).sort_values("Year")
trend_women  = filtered_df[filtered_df["Gender"]=="Female"].dropna(subset=["Time_Minutes"]).sort_values("Year")
men_years    = trend_men["Year"].astype(int).tolist()
men_times    = [round(x,1) for x in trend_men["Time_Minutes"].tolist()]
women_years  = trend_women["Year"].astype(int).tolist()
women_times  = [round(x,1) for x in trend_women["Time_Minutes"].tolist()]

# Country data
country_counts = filtered_df["Country"].value_counts().head(8)
country_labels = country_counts.index.tolist()
country_vals   = country_counts.values.tolist()

# Decade data
filtered_df2 = filtered_df.copy()
filtered_df2["Decade"] = (filtered_df2["Year"]//10)*10
dec_m = filtered_df2[filtered_df2["Gender"]=="Male"].groupby("Decade").size()
dec_f = filtered_df2[filtered_df2["Gender"]=="Female"].groupby("Decade").size()
all_decades = sorted(set(dec_m.index.tolist() + dec_f.index.tolist()))
dec_labels  = [f"{int(d)}s" for d in all_decades]
dec_men_v   = [int(dec_m.get(d, 0)) for d in all_decades]
dec_women_v = [int(dec_f.get(d, 0)) for d in all_decades]

# Hall of fame
hof = filtered_df.groupby("Winner").agg(
    wins=("Year","count"), country=("Country","first"),
    first=("Year","min"), last=("Year","max")
).sort_values("wins", ascending=False).head(5).reset_index()
hof_data = [{"name": r.Winner, "country": r.country,
             "wins": int(r.wins), "first": int(r.first), "last": int(r.last)}
            for r in hof.itertuples()]

# Scatter data (sampled for perf)
scatter_df = filtered_df.dropna(subset=["Time_Minutes","Speed_MPH"]).copy()
scatter_sample = scatter_df.sample(min(150, len(scatter_df)), random_state=42)
scatter_data = [{"x": int(r.Year), "y": round(float(r.Time_Minutes),1),
                 "s": round(float(r.Speed_MPH),2), "g": r.Gender, "w": r.Winner}
                for r in scatter_sample.itertuples()]

# Top speed/pace records
top_speed_row = filtered_df.loc[filtered_df["Speed_MPH"].idxmax()] if len(filtered_df) else None
avg_pace = round(float(filtered_df["Pace_Per_Mile"].dropna().mean()), 2) if len(filtered_df) else 0

# Gender gap
male_avg   = round(float(filtered_df[filtered_df["Gender"]=="Male"]["Time_Minutes"].mean()),1) if "Male" in filtered_df["Gender"].values else None
female_avg = round(float(filtered_df[filtered_df["Gender"]=="Female"]["Time_Minutes"].mean()),1) if "Female" in filtered_df["Gender"].values else None

# Histogram bins
hist_data_raw = td.tolist()
hist_min, hist_max = (min(hist_data_raw), max(hist_data_raw)) if hist_data_raw else (120,220)
bin_edges = list(np.linspace(hist_min, hist_max, 16))
hist_counts, _ = np.histogram(hist_data_raw, bins=bin_edges)
hist_bins = [{"x": round((bin_edges[i]+bin_edges[i+1])/2,1), "y": int(hist_counts[i])}
             for i in range(len(hist_counts))]

fast_name    = safe_val(fast_row["Winner"])   if fast_row is not None else "N/A"
fast_year    = int(safe_val(fast_row["Year"], 0)) if fast_row is not None else 0
top_spd_name = safe_val(top_speed_row["Winner"]) if top_speed_row is not None else "N/A"
top_spd_val  = round(float(top_speed_row["Speed_MPH"]),2) if top_speed_row is not None else 0
total_cntry  = int(filtered_df["Country"].nunique())
unique_win   = int(filtered_df["Winner"].nunique())
yr_min       = int(filtered_df["Year"].min())
yr_max       = int(filtered_df["Year"].max())

# Improvement arrow text
improvement  = round(slow_t - fast_t, 1)
std_t        = round(float(td.std()), 1) if len(td) > 1 else 0

# Pack all JS data
js_data = json.dumps({
    "menYears": men_years, "menTimes": men_times,
    "womenYears": women_years, "womenTimes": women_times,
    "countryLabels": country_labels, "countryVals": country_vals,
    "decLabels": dec_labels, "decMen": dec_men_v, "decWomen": dec_women_v,
    "scatter": scatter_data,
    "histBins": hist_bins,
    "hof": hof_data,
    "stats": {
        "total": len(filtered_df), "avgTime": round(avg_t,1),
        "fastTime": round(fast_t,1), "fastHMS": mins_to_hms(fast_t),
        "fastName": fast_name, "fastYear": fast_year,
        "avgSpeed": round(avg_spd,2), "medTime": round(med_t,1),
        "countries": total_cntry, "uniqueWinners": unique_win,
        "yrMin": yr_min, "yrMax": yr_max,
        "improvement": improvement, "stdT": std_t,
        "avgPace": avg_pace, "topSpeedName": top_spd_name, "topSpeedVal": top_spd_val,
        "maleAvg": male_avg, "femaleAvg": female_avg,
        "menCount": len(trend_men), "womenCount": len(trend_women),
    }
})

# ════════════════════════════════════════════════════════════════════════════
# MAIN CINEMATIC COMPONENT
# ════════════════════════════════════════════════════════════════════════════
html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
:root{{
    --bg:#07070a;--bg1:#0b0b0f;--bg2:#0f0e13;--bg3:#141318;
    --amber:#e8933a;--amber2:#f0a852;--gold:#d4a850;
    --orange:#e07830;--red:#e86850;
    --tw:#f5f0e8;--tl:#c8c0b0;--td:#7a7468;--tm:#4a4540;
    --border:rgba(232,147,58,0.08);--border2:rgba(232,147,58,0.18);
}}
html,body{{background:var(--bg);color:var(--tw);font-family:'Georgia',serif;overflow-x:hidden;}}

/* ─ Particle canvas ─ */
#particle-canvas{{
    position:fixed;top:0;left:0;width:100%;height:100%;
    pointer-events:none;z-index:0;opacity:0.35;
}}

/* ─ Hero ─ */
.hero{{
    position:relative;z-index:1;
    background:linear-gradient(160deg,#0a080d 0%,#0f0c0a 40%,#080a0d 100%);
    border-bottom:1px solid var(--border);
    padding:48px 40px 36px;overflow:hidden;
}}
.hero-bg-num{{
    position:absolute;right:-10px;top:50%;transform:translateY(-50%);
    font-size:clamp(120px,18vw,220px);font-weight:900;
    color:rgba(232,147,58,0.04);letter-spacing:-10px;
    font-family:'Georgia',serif;pointer-events:none;line-height:1;
    user-select:none;
}}
.hero-eyebrow{{
    display:inline-flex;align-items:center;gap:8px;
    background:rgba(232,147,58,0.07);border:1px solid rgba(232,147,58,0.14);
    padding:5px 14px;border-radius:100px;
    font-size:0.62rem;font-weight:700;letter-spacing:2.5px;
    text-transform:uppercase;color:var(--amber);margin-bottom:18px;
    font-family:'Inter','Arial',sans-serif;
}}
.hero-title{{
    font-size:clamp(2.4rem,5vw,4rem);font-weight:800;
    color:var(--tw);letter-spacing:-1.5px;line-height:1.05;margin-bottom:6px;
}}
.hero-title span{{color:var(--amber);}}
.hero-sub{{
    font-size:0.88rem;color:var(--td);margin-bottom:28px;
    font-family:'Inter','Arial',sans-serif;line-height:1.6;
}}

/* ─ Route strip ─ */
.route-strip{{
    display:flex;align-items:center;gap:0;margin-bottom:10px;
    position:relative;
}}
.rd{{width:12px;height:12px;border-radius:50%;background:var(--amber);flex-shrink:0;
    box-shadow:0 0 14px rgba(232,147,58,0.6);}}
.rpath{{flex:1;height:3px;margin:0 6px;position:relative;overflow:visible;}}
.rpath-line{{
    width:100%;height:100%;
    background:linear-gradient(90deg,var(--amber) 0%,#c47520 45%,#5a2e08 75%,rgba(232,147,58,0.12) 100%);
    border-radius:2px;
}}
.runner-anim{{
    position:absolute;top:50%;transform:translateY(-50%);
    font-size:1.1rem;animation:runForward 6s linear infinite;
    filter:drop-shadow(0 0 6px rgba(232,147,58,0.8));
}}
@keyframes runForward{{
    0%{{left:-2%;opacity:0;}}
    5%{{opacity:1;}}
    92%{{opacity:1;}}
    100%{{left:98%;opacity:0;}}
}}
.heartbreak-pin{{
    position:absolute;top:-28px;left:70%;transform:translateX(-50%);
    text-align:center;white-space:nowrap;
}}
.heartbreak-label{{
    background:rgba(220,50,30,0.12);border:1px solid rgba(220,50,30,0.25);
    color:#e84530;font-size:0.5rem;font-weight:700;letter-spacing:1px;
    padding:2px 7px;border-radius:4px;font-family:'Inter','Arial',sans-serif;
    text-transform:uppercase;
}}
.heartbreak-tick{{
    width:1px;height:10px;background:rgba(220,50,30,0.3);
    margin:0 auto;
}}
.rde{{width:12px;height:12px;border-radius:50%;flex-shrink:0;
    border:2px solid rgba(232,147,58,0.3);background:rgba(232,147,58,0.06);}}
.route-stops{{
    display:flex;justify-content:space-between;margin-top:6px;
    font-size:0.58rem;font-family:'Inter','Arial',sans-serif;
    font-weight:600;letter-spacing:1px;
}}
.route-stops .s1{{color:var(--amber);}}
.route-stops .s2{{color:var(--tm);}}
.route-stops .s3{{color:var(--tm);}}

/* ─ Milestone bar ─ */
.milestones{{
    display:flex;gap:8px;padding:20px 40px;
    background:linear-gradient(90deg,var(--bg1),var(--bg));
    border-bottom:1px solid var(--border);
    overflow-x:auto;flex-wrap:nowrap;position:relative;z-index:1;
}}
.milestones::-webkit-scrollbar{{height:2px;}}
.milestones::-webkit-scrollbar-thumb{{background:rgba(232,147,58,0.2);}}
.ms{{
    flex:0 0 auto;min-width:160px;max-width:200px;
    background:var(--bg2);border:1px solid var(--border);
    border-radius:12px;padding:14px;position:relative;overflow:hidden;
    cursor:default;transition:border-color 0.3s,transform 0.3s;
}}
.ms:hover{{border-color:var(--border2);transform:translateY(-2px);}}
.ms::before{{
    content:'';position:absolute;left:0;top:0;bottom:0;width:2px;
    background:linear-gradient(180deg,var(--amber),transparent);
}}
.ms-yr{{color:var(--amber);font-size:0.72rem;font-weight:800;margin-bottom:5px;
    font-family:'Inter','Arial',sans-serif;}}
.ms-txt{{color:var(--td);font-size:0.64rem;line-height:1.5;
    font-family:'Inter','Arial',sans-serif;}}
.ms-txt b{{color:var(--tl);}}

/* ─ Stats bar ─ */
.stats-bar{{
    display:flex;gap:0;padding:0 40px;
    border-bottom:1px solid var(--border);position:relative;z-index:1;
}}
.stat-item{{
    flex:1;padding:20px 0;border-right:1px solid var(--border);
    text-align:center;transition:background 0.3s;cursor:default;
}}
.stat-item:last-child{{border-right:none;}}
.stat-item:hover{{background:rgba(232,147,58,0.03);}}
.stat-lbl{{color:var(--tm);font-size:0.56rem;font-weight:700;letter-spacing:2px;
    text-transform:uppercase;margin-bottom:5px;font-family:'Inter','Arial',sans-serif;}}
.stat-val{{color:var(--tw);font-size:1.3rem;font-weight:800;letter-spacing:-0.5px;}}
.stat-val span{{color:var(--amber);}}
.stat-sub{{color:var(--td);font-size:0.58rem;margin-top:2px;
    font-family:'Inter','Arial',sans-serif;}}

/* ─ Section headings ─ */
.sec{{
    display:flex;align-items:center;gap:14px;
    padding:40px 40px 20px;position:relative;z-index:1;
}}
.sec-badge{{
    display:flex;align-items:center;justify-content:center;
    width:30px;height:30px;border-radius:50%;
    background:linear-gradient(135deg,#b06018,var(--amber));
    color:#07070a;font-size:0.7rem;font-weight:900;flex-shrink:0;
    box-shadow:0 0 14px rgba(232,147,58,0.3);
    font-family:'Inter','Arial',sans-serif;
}}
.sec-info .st{{
    font-size:1.1rem;font-weight:700;color:var(--tw);letter-spacing:-0.3px;
}}
.sec-info .ss{{
    font-size:0.68rem;color:var(--td);margin-top:2px;
    font-family:'Inter','Arial',sans-serif;
}}
.sec-line{{flex:1;height:1px;background:linear-gradient(90deg,rgba(232,147,58,0.15),transparent);}}

/* ─ Chart grid ─ */
.chart-grid{{display:grid;gap:16px;padding:0 40px 10px;position:relative;z-index:1;}}
.chart-grid.two{{grid-template-columns:1fr 1fr;}}
.chart-grid.one{{grid-template-columns:1fr;}}
.chart-grid.three{{grid-template-columns:1fr 1fr 1fr;}}

/* ─ Chart card ─ */
.chart-card{{
    background:linear-gradient(145deg,var(--bg2),var(--bg3));
    border:1px solid var(--border);border-radius:18px;
    overflow:hidden;transition:border-color 0.4s,transform 0.4s,box-shadow 0.4s;
    cursor:pointer;position:relative;
}}
.chart-card:hover{{
    border-color:var(--border2);transform:translateY(-3px);
    box-shadow:0 16px 50px rgba(0,0,0,0.5),0 0 50px rgba(232,147,58,0.06);
}}
.chart-card::before{{
    content:'';position:absolute;top:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,rgba(232,147,58,0.12),transparent);
}}
/* click ripple */
.chart-card.ripple::after{{
    content:'';position:absolute;border-radius:50%;
    background:rgba(232,147,58,0.12);
    width:200px;height:200px;margin-top:-100px;margin-left:-100px;
    animation:rippleAnim 0.6s linear;pointer-events:none;
    top:var(--ry,50%);left:var(--rx,50%);
}}
@keyframes rippleAnim{{
    0%{{transform:scale(0);opacity:1;}}
    100%{{transform:scale(4);opacity:0;}}
}}
.chart-header{{padding:16px 20px 8px;}}
.chart-title{{
    font-size:0.78rem;font-weight:700;color:var(--tl);
    letter-spacing:0.3px;font-family:'Inter','Arial',sans-serif;
}}
.chart-sub{{
    font-size:0.62rem;color:var(--tm);margin-top:3px;
    font-family:'Inter','Arial',sans-serif;
}}
.chart-body{{padding:0 14px 14px;}}
canvas{{display:block;width:100%!important;}}

/* ─ Tooltip ─ */
.custom-tooltip{{
    position:fixed;pointer-events:none;z-index:9999;
    background:rgba(10,9,14,0.96);border:1px solid var(--border2);
    border-radius:10px;padding:10px 14px;font-family:'Inter','Arial',sans-serif;
    font-size:0.72rem;color:var(--tl);max-width:200px;
    box-shadow:0 8px 30px rgba(0,0,0,0.6);display:none;
    backdrop-filter:blur(8px);
}}
.custom-tooltip .ttl{{color:var(--amber);font-weight:700;margin-bottom:3px;}}

/* ─ Hall of Fame ─ */
.hof-grid{{
    display:grid;grid-template-columns:repeat(5,1fr);gap:12px;
    padding:0 40px 10px;position:relative;z-index:1;
}}
.hof-card{{
    background:linear-gradient(145deg,var(--bg2),var(--bg3));
    border:1px solid var(--border);border-radius:16px;
    padding:18px 14px;text-align:center;
    position:relative;overflow:hidden;
    transition:border-color 0.3s,transform 0.3s,box-shadow 0.3s;
    cursor:default;
}}
.hof-card:hover{{
    border-color:var(--border2);transform:translateY(-4px);
    box-shadow:0 14px 40px rgba(0,0,0,0.5),0 0 30px rgba(232,147,58,0.07);
}}
.hof-card::before{{
    content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,transparent,rgba(232,147,58,0.25),transparent);
}}
.hof-rank{{color:var(--tm);font-size:0.55rem;font-weight:700;letter-spacing:2px;
    text-transform:uppercase;margin-bottom:8px;font-family:'Inter','Arial',sans-serif;}}
.hof-medal{{font-size:1.8rem;margin-bottom:8px;}}
.hof-name{{color:var(--tw);font-size:0.75rem;font-weight:700;
    margin-bottom:3px;line-height:1.3;font-family:'Inter','Arial',sans-serif;}}
.hof-country{{color:var(--td);font-size:0.6rem;margin-bottom:10px;
    font-family:'Inter','Arial',sans-serif;}}
.hof-wins{{color:var(--amber);font-size:2rem;font-weight:900;letter-spacing:-1.5px;}}
.hof-wins-lbl{{color:var(--tm);font-size:0.55rem;font-weight:700;letter-spacing:2px;
    text-transform:uppercase;font-family:'Inter','Arial',sans-serif;}}
.hof-years{{color:var(--tm);font-size:0.56rem;margin-top:3px;
    font-family:'Inter','Arial',sans-serif;}}

/* ─ Insight strip ─ */
.insight-strip{{
    display:grid;grid-template-columns:repeat(3,1fr);gap:12px;
    padding:0 40px 10px;position:relative;z-index:1;
}}
.ic{{
    background:linear-gradient(145deg,var(--bg2),var(--bg3));
    border:1px solid var(--border);border-radius:14px;
    padding:16px 18px;position:relative;overflow:hidden;
    transition:border-color 0.3s,transform 0.3s;
}}
.ic:hover{{border-color:var(--border2);transform:translateY(-2px);}}
.ic::before{{
    content:'';position:absolute;top:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,rgba(232,147,58,0.12),transparent);
}}
.ic-lbl{{color:var(--tm);font-size:0.58rem;font-weight:700;letter-spacing:2px;
    text-transform:uppercase;margin-bottom:5px;font-family:'Inter','Arial',sans-serif;}}
.ic-val{{color:var(--amber);font-size:1.1rem;font-weight:800;
    letter-spacing:-0.3px;margin-bottom:4px;}}
.ic-desc{{color:var(--td);font-size:0.68rem;line-height:1.55;
    font-family:'Inter','Arial',sans-serif;}}
.ic-desc b{{color:var(--tl);font-weight:600;}}

/* ─ Fact banner ─ */
.fb{{
    display:flex;align-items:flex-start;gap:14px;
    background:linear-gradient(135deg,rgba(232,147,58,0.04),rgba(212,168,80,0.03));
    border:1px solid rgba(232,147,58,0.09);border-radius:14px;
    padding:14px 20px;margin:4px 40px 28px;
    position:relative;z-index:1;
}}
.fb-icon{{font-size:1.2rem;flex-shrink:0;margin-top:2px;}}
.fb-txt{{color:var(--td);font-size:0.73rem;line-height:1.65;
    font-family:'Inter','Arial',sans-serif;}}
.fb-txt b{{color:var(--amber);}}

/* ─ Chart caption ─ */
.cap{{
    background:rgba(232,147,58,0.03);border:1px solid rgba(232,147,58,0.06);
    border-radius:10px;padding:9px 14px;
    margin:4px 40px 20px;font-size:0.67rem;color:var(--td);line-height:1.6;
    font-family:'Inter','Arial',sans-serif;position:relative;z-index:1;
}}
.cap b{{color:#a89070;}}

/* ─ Footer ─ */
.footer{{
    text-align:center;padding:32px 40px;margin-top:20px;
    border-top:1px solid var(--border);position:relative;z-index:1;
}}
.footer p{{color:var(--tm);font-size:0.7rem;line-height:1.8;
    font-family:'Inter','Arial',sans-serif;}}
.footer b{{color:var(--amber);}}

/* ─ Entrance animations ─ */
.fade-up{{opacity:0;transform:translateY(20px);transition:opacity 0.6s ease,transform 0.6s ease;}}
.fade-up.visible{{opacity:1;transform:translateY(0);}}

/* ─ Count-up numbers ─ */
.count-up{{display:inline-block;}}

/* ─ Responsive ─ */
@media(max-width:900px){{
    .chart-grid.two,.chart-grid.three{{grid-template-columns:1fr;}}
    .hof-grid{{grid-template-columns:repeat(3,1fr);}}
    .insight-strip{{grid-template-columns:1fr;}}
    .stats-bar{{flex-wrap:wrap;}}
    .stat-item{{min-width:50%;border-right:none;border-bottom:1px solid var(--border);}}
}}
</style>
</head>
<body>

<canvas id="particle-canvas"></canvas>
<div class="custom-tooltip" id="tooltip"><div class="ttl" id="tt-title"></div><div id="tt-body"></div></div>

<!-- ═══ HERO ═══ -->
<div class="hero fade-up">
    <div class="hero-bg-num">26.2</div>
    <div class="hero-eyebrow">🏃 Est. 1897 · Patriots Day · Hopkinton → Boston</div>
    <h1 class="hero-title">Boston <span>Marathon</span><br>Analytics</h1>
    <p class="hero-sub">
        127 years of champions · {int(filtered_df['Year'].min())}–{int(filtered_df['Year'].max())} · 
        {len(filtered_df)} records · {int(filtered_df['Country'].nunique())} nations
    </p>
    <div class="route-strip">
        <div class="rd"></div>
        <div class="rpath">
            <div class="rpath-line"></div>
            <span class="runner-anim">🏃</span>
            <div class="heartbreak-pin">
                <div class="heartbreak-label">⚡ Heartbreak Hill · Mile 20</div>
                <div class="heartbreak-tick"></div>
            </div>
        </div>
        <div class="rde"></div>
    </div>
    <div class="route-stops">
        <span class="s1">▶ START · Hopkinton</span>
        <span class="s2">· · · 26.2 miles / 42.195 km · · ·</span>
        <span class="s3">FINISH · Boylston St ■</span>
    </div>
</div>

<!-- ═══ MILESTONES ═══ -->
<div class="milestones fade-up">
    <div class="ms"><div class="ms-yr">1897</div><div class="ms-txt"><b>First Race.</b> 15 runners. John McDermott wins in 2:55:10. A legend is born.</div></div>
    <div class="ms"><div class="ms-yr">1924</div><div class="ms-txt"><b>Standard distance</b> set at 26.2 miles after Olympic standardization.</div></div>
    <div class="ms"><div class="ms-yr">1967</div><div class="ms-txt"><b>Kathrine Switzer</b> runs as the first numbered woman. RD tries to physically remove her.</div></div>
    <div class="ms"><div class="ms-yr">1972</div><div class="ms-txt"><b>Women officially allowed.</b> Nina Kuscsik wins the inaugural women's division.</div></div>
    <div class="ms"><div class="ms-yr">1990s</div><div class="ms-txt"><b>Kenyan dominance.</b> East African runners redefine distance running with altitude training.</div></div>
    <div class="ms"><div class="ms-yr">2011</div><div class="ms-txt"><b>Geoffrey Mutai</b> sets course record 2:03:02 — one of the fastest marathons ever run.</div></div>
    <div class="ms"><div class="ms-yr">Today</div><div class="ms-txt"><b>World Marathon Major.</b> 30,000 runners, 500,000 spectators. Qualifying time required.</div></div>
</div>

<!-- ═══ LIVE STATS BAR ═══ -->
<div class="stats-bar fade-up">
    <div class="stat-item">
        <div class="stat-lbl">Course Record</div>
        <div class="stat-val"><span id="s-record">–</span></div>
        <div class="stat-sub" id="s-record-name">–</div>
    </div>
    <div class="stat-item">
        <div class="stat-lbl">Avg Finish Time</div>
        <div class="stat-val" id="s-avg">–</div>
        <div class="stat-sub">All filtered records</div>
    </div>
    <div class="stat-item">
        <div class="stat-lbl">Avg Speed</div>
        <div class="stat-val"><span id="s-speed">–</span> <span style="font-size:0.8rem;color:var(--td)">mph</span></div>
        <div class="stat-sub">Winning average</div>
    </div>
    <div class="stat-item">
        <div class="stat-lbl">Nations</div>
        <div class="stat-val"><span class="count-up" id="s-nations">0</span></div>
        <div class="stat-sub">Countries represented</div>
    </div>
    <div class="stat-item">
        <div class="stat-lbl">Unique Champions</div>
        <div class="stat-val"><span class="count-up" id="s-winners">0</span></div>
        <div class="stat-sub">Different athletes</div>
    </div>
    <div class="stat-item">
        <div class="stat-lbl">Year Span</div>
        <div class="stat-val" id="s-span">–</div>
        <div class="stat-sub">Race history</div>
    </div>
</div>

<!-- ═══ SECTION 1: HALL OF FAME ═══ -->
<div class="sec fade-up">
    <div class="sec-badge">1</div>
    <div class="sec-info">
        <div class="st">Hall of Fame</div>
        <div class="ss">Most decorated champions in Boston Marathon history</div>
    </div>
    <div class="sec-line"></div>
</div>
<div class="hof-grid fade-up" id="hof-grid"></div>
<div class="fb fade-up">
    <div class="fb-icon">🏆</div>
    <div class="fb-txt">
        <b>Clarence DeMar</b> won Boston 7 times (1911–1930) — a record that stood for decades. 
        Modern Kenyan legends like <b>Robert Kipkoech Cheruiyot</b> and <b>Catherine Ndereba</b> (4 wins each) 
        dominate the contemporary era. The Hall of Fame updates live with your sidebar filters.
    </div>
</div>

<!-- ═══ SECTION 2: WINNING TIMES TREND ═══ -->
<div class="sec fade-up">
    <div class="sec-badge">2</div>
    <div class="sec-info">
        <div class="st">Performance Trends</div>
        <div class="ss">How winning times evolved — 127 years of improvement</div>
    </div>
    <div class="sec-line"></div>
</div>
<div class="chart-grid one fade-up">
    <div class="chart-card" onclick="ripple(event,this)">
        <div class="chart-header">
            <div class="chart-title">Winning Times Over the Years</div>
            <div class="chart-sub">Amber = Men · Red = Women · Click to highlight</div>
        </div>
        <div class="chart-body"><canvas id="lineChart" height="90"></canvas></div>
    </div>
</div>
<div class="chart-grid two fade-up">
    <div class="chart-card" onclick="ripple(event,this)">
        <div class="chart-header">
            <div class="chart-title">Speed vs Year Scatter</div>
            <div class="chart-sub">Each dot = one race · Hover for details</div>
        </div>
        <div class="chart-body"><canvas id="scatterChart" height="160"></canvas></div>
    </div>
    <div class="chart-card" onclick="ripple(event,this)">
        <div class="chart-header">
            <div class="chart-title">Finishing Time Distribution</div>
            <div class="chart-sub">Frequency histogram of winning times</div>
        </div>
        <div class="chart-body"><canvas id="histChart" height="160"></canvas></div>
    </div>
</div>
<div class="cap fade-up">
    <b>Line Chart</b> — Steady decline reflects training science, nutrition, altitude prep, and carbon-fiber super-shoes (Nike Vaporfly adds ~4 min). 
    <b>Scatter</b> — Each dot one race; hover to see winner + year. 
    <b>Histogram</b> — Most wins cluster in the 125–160 min band; the right tail is early-era pre-standardization races.
</div>

<!-- insight strip 2 -->
<div class="insight-strip fade-up" id="ins2"></div>

<div class="fb fade-up">
    <div class="fb-icon">💡</div>
    <div class="fb-txt">
        The infamous <b>Heartbreak Hill</b> (miles 20–21) is actually a series of four hills in Newton, MA. 
        Coming when runners are already depleted at mile 20, it has broken more race strategies than any other single factor. 
        World record holder <b>Eliud Kipchoge</b> has said Boston's course is "honest but unforgiving." 
        The combination of early downhills (quad-destroying) followed by Newton's hills makes Boston uniquely brutal.
    </div>
</div>

<!-- ═══ SECTION 3: NATIONAL BREAKDOWN ═══ -->
<div class="sec fade-up">
    <div class="sec-badge">3</div>
    <div class="sec-info">
        <div class="st">National Dominance</div>
        <div class="ss">Country wins and decade-by-decade breakdown</div>
    </div>
    <div class="sec-line"></div>
</div>
<div class="chart-grid two fade-up">
    <div class="chart-card" onclick="ripple(event,this)">
        <div class="chart-header">
            <div class="chart-title">Top Countries by Wins</div>
            <div class="chart-sub">Horizontal bar · Hover for exact count</div>
        </div>
        <div class="chart-body"><canvas id="barChart" height="180"></canvas></div>
    </div>
    <div class="chart-card" onclick="ripple(event,this)">
        <div class="chart-header">
            <div class="chart-title">Winners Per Decade</div>
            <div class="chart-sub">Men vs Women · Click to toggle series</div>
        </div>
        <div class="chart-body"><canvas id="decadeChart" height="180"></canvas></div>
    </div>
</div>
<div class="cap fade-up">
    <b>USA</b> dominated early decades; <b>Japan</b> surged mid-century with rigorous team training; 
    <b>Kenya & Ethiopia</b> have dominated since the 1990s through altitude training at 2,400m+ elevation. 
    The decade chart shows the dramatic expansion of the women's field after 1972's official recognition.
</div>

<!-- insight strip 3 -->
<div class="insight-strip fade-up" id="ins3"></div>

<!-- ═══ SECTION 4: PACE & SPEED ═══ -->
<div class="sec fade-up">
    <div class="sec-badge">4</div>
    <div class="sec-info">
        <div class="st">Speed & Pace Analysis</div>
        <div class="ss">Bubble chart · three dimensions at once</div>
    </div>
    <div class="sec-line"></div>
</div>
<div class="chart-grid one fade-up">
    <div class="chart-card" onclick="ripple(event,this)">
        <div class="chart-header">
            <div class="chart-title">Year · Time · Speed — Three Dimensions</div>
            <div class="chart-sub">Bubble size = Speed (mph) · Amber = Men · Red = Women · Hover for winner details</div>
        </div>
        <div class="chart-body"><canvas id="bubbleChart" height="85"></canvas></div>
    </div>
</div>
<div class="cap fade-up">
    <b>Bubble Chart</b> — Year on x-axis, Finishing Time on y-axis, Speed encoded as bubble size. 
    Larger bubbles = faster races. The cluster of large bubbles in recent decades (post-2000) 
    reflects the era of super-shoes, superior training, and elite-paced rabbit runners.
</div>
<!-- insight strip 4 -->
<div class="insight-strip fade-up" id="ins4"></div>

<div class="fb fade-up">
    <div class="fb-icon">📌</div>
    <div class="fb-txt">
        Boston is one of six <b>World Marathon Majors</b> (Tokyo, London, Berlin, Chicago, NYC). 
        It's the only major with a <b>qualifying standard</b> — men must run sub-3:00, women sub-3:30. 
        The race draws ~30,000 runners and ~500,000 spectators lining the 26.2-mile route every April.
        Prize money: <b>$150,000</b> for the overall winner.
    </div>
</div>

<!-- ═══ FOOTER ═══ -->
<div class="footer fade-up">
    <p>
        <b>Boston Marathon</b> Elite Analytics Dashboard<br>
        Built with <b>Streamlit</b> · <b>Chart.js</b> · <b>Python</b> · <b>Pandas</b><br>
        Data: <b>1897–2022</b> · Patriots Day · Hopkinton → Boylston Street · 26.2 miles
    </p>
</div>

<script>
const D = {js_data};

// ── utils ────────────────────────────────────────────────────────────────
function mins2hms(m){{
    const h=Math.floor(m/60),mi=Math.floor(m%60),s=Math.round((m%1)*60);
    return `${{h}}:${{String(mi).padStart(2,'0')}}:${{String(s).padStart(2,'0')}}`;
}}
function hmsAbbr(m){{
    const h=Math.floor(m/60),mi=Math.floor(m%60);
    return `${{h}}h ${{String(mi).padStart(2,'0')}}m`;
}}

// ── Particle system ───────────────────────────────────────────────────────
(function(){{
    const c=document.getElementById('particle-canvas');
    const ctx=c.getContext('2d');
    let W,H,pts=[];
    function resize(){{W=c.width=window.innerWidth;H=c.height=document.body.scrollHeight;}}
    resize();
    window.addEventListener('resize',()=>{{resize();init();}});
    function init(){{
        pts=[];
        const n=Math.min(60,Math.floor(W*H/25000));
        for(let i=0;i<n;i++)pts.push({{
            x:Math.random()*W,y:Math.random()*H,
            vx:(Math.random()-0.5)*0.3,vy:(Math.random()-0.5)*0.3,
            r:Math.random()*1.5+0.4,
            a:Math.random()*0.35+0.08,
        }});
    }}
    init();
    function draw(){{
        ctx.clearRect(0,0,W,H);
        pts.forEach(p=>{{
            p.x+=p.vx;p.y+=p.vy;
            if(p.x<0||p.x>W)p.vx*=-1;
            if(p.y<0||p.y>H)p.vy*=-1;
            ctx.beginPath();
            ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
            ctx.fillStyle=`rgba(232,147,58,${{p.a}})`;
            ctx.fill();
        }});
        // connect nearby
        for(let i=0;i<pts.length;i++){{
            for(let j=i+1;j<pts.length;j++){{
                const dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y;
                const d=Math.sqrt(dx*dx+dy*dy);
                if(d<120){{
                    ctx.beginPath();
                    ctx.moveTo(pts[i].x,pts[i].y);
                    ctx.lineTo(pts[j].x,pts[j].y);
                    ctx.strokeStyle=`rgba(232,147,58,${{(1-d/120)*0.08}})`;
                    ctx.lineWidth=0.5;
                    ctx.stroke();
                }}
            }}
        }}
        requestAnimationFrame(draw);
    }}
    draw();
}})();

// ── count-up animation ────────────────────────────────────────────────────
function countUp(el,target,duration=1200){{
    const start=performance.now();
    const isFloat=target%1!==0;
    function step(now){{
        const p=Math.min((now-start)/duration,1);
        const ease=1-Math.pow(1-p,3);
        const val=isFloat?(ease*target).toFixed(2):Math.round(ease*target);
        el.textContent=val;
        if(p<1)requestAnimationFrame(step);
    }}
    requestAnimationFrame(step);
}}

// ── Fill stats bar ────────────────────────────────────────────────────────
const S=D.stats;
document.getElementById('s-record').textContent=S.fastHMS;
document.getElementById('s-record-name').textContent=S.fastName+' · '+S.fastYear;
document.getElementById('s-avg').textContent=mins2hms(S.avgTime);
document.getElementById('s-speed').textContent=S.avgSpeed.toFixed(2);
document.getElementById('s-span').textContent=S.yrMin+'–'+S.yrMax;
countUp(document.getElementById('s-nations'),S.countries);
countUp(document.getElementById('s-winners'),S.uniqueWinners);

// ── Hall of Fame ──────────────────────────────────────────────────────────
const medals=['🥇','🥈','🥉','🏅','🏅'];
const ranks=['1ST','2ND','3RD','4TH','5TH'];
const hg=document.getElementById('hof-grid');
D.hof.forEach((h,i)=>{{
    hg.innerHTML+=`
    <div class="hof-card">
        <div class="hof-rank">${{ranks[i]||''}}</div>
        <div class="hof-medal">${{medals[i]||'🏅'}}</div>
        <div class="hof-name">${{h.name}}</div>
        <div class="hof-country">${{h.country}}</div>
        <div class="hof-wins">${{h.wins}}</div>
        <div class="hof-wins-lbl">Wins</div>
        <div class="hof-years">${{h.first}}–${{h.last}}</div>
    </div>`;
}});

// ── insight helper ─────────────────────────────────────────────────────────
function insStrip(id,cards){{
    const el=document.getElementById(id);
    if(!el)return;
    el.innerHTML=cards.map(c=>`
    <div class="ic">
        <div class="ic-lbl">${{c.lbl}}</div>
        <div class="ic-val">${{c.val}}</div>
        <div class="ic-desc">${{c.desc}}</div>
    </div>`).join('');
}}

// Section 2 insights
insStrip('ins2',[
    {{lbl:'Course Record',val:S.fastHMS,
      desc:`Set by <b>${{S.fastName}}</b> in <b>${{S.fastYear}}</b>. Elite marathons keep improving as training science and shoe tech advance.`}},
    {{lbl:'Total Improvement',val:S.improvement.toFixed(1)+' min',
      desc:`Winning times improved by <b>${{S.improvement.toFixed(1)}} min</b> across the dataset — driven by training, nutrition, and carbon-fiber shoes.`}},
    {{lbl:'Avg Winning Speed',val:S.avgSpeed.toFixed(2)+' mph',
      desc:`Winners average <b>${{S.avgSpeed.toFixed(2)}} mph</b> sustained over 26.2 miles — roughly <b>${{hmsAbbr(S.avgTime)}}</b> of non-stop running.`}},
]);

// Section 3 insights
const topC=D.countryLabels[0]||'N/A';
const topN=D.countryVals[0]||0;
const topPct=S.total>0?(topN/S.total*100).toFixed(1):0;
insStrip('ins3',[
    {{lbl:'Dominant Nation',val:topC,
      desc:`Won <b>${{topN}}</b> races — <b>${{topPct}}%</b> of all filtered records. <b>${{S.countries}}</b> nations have won Boston.`}},
    {{lbl:'Unique Champions',val:S.uniqueWinners,
      desc:`<b>${{S.uniqueWinners}}</b> different athletes across filtered records. <b>Clarence DeMar</b> leads all-time with 7 wins (1911–1930).`}},
    {{lbl:'Gender Split',val:S.menCount+' / '+S.womenCount,
      desc:`<b>${{S.menCount}}</b> Men's records · <b>${{S.womenCount}}</b> Women's records. Women officially recognised since <b>1972</b>.`}},
]);

// Section 4 insights
const gapStr=S.maleAvg&&S.femaleAvg?`Men avg <b>${{S.maleAvg}} min</b>, Women avg <b>${{S.femaleAvg}} min</b> — a gap of <b>${{(S.femaleAvg-S.maleAvg).toFixed(1)}} min</b>. Narrowing since 1970s.`:'Filter to All gender to see gap.';
insStrip('ins4',[
    {{lbl:'Avg Pace / Mile',val:S.avgPace+' min/mi',
      desc:`Winners run each mile in <b>${{Math.floor(S.avgPace)}}:${{String(Math.round((S.avgPace%1)*60)).padStart(2,'0')}}</b> — sustained over 26.2 miles. Superhuman.`}},
    {{lbl:'Top Speed',val:S.topSpeedVal+' mph',
      desc:`<b>${{S.topSpeedName}}</b> holds the top recorded speed in this filter at <b>${{S.topSpeedVal}} mph</b>. Modern supershoes add 2–4 minutes to a marathon.`}},
    {{lbl:'Gender Gap',val:S.maleAvg&&S.femaleAvg?(S.femaleAvg-S.maleAvg).toFixed(1)+' min':'N/A',
      desc:gapStr}},
]);

// ── Chart.js defaults ─────────────────────────────────────────────────────
Chart.defaults.color='#7a7468';
Chart.defaults.borderColor='rgba(232,147,58,0.07)';
Chart.defaults.font.family="'Inter','Arial',sans-serif";

// ── Tooltip helper ────────────────────────────────────────────────────────
const TT=document.getElementById('tooltip');
const TTT=document.getElementById('tt-title');
const TTB=document.getElementById('tt-body');
function showTT(x,y,title,body){{
    TTT.textContent=title;TTB.innerHTML=body;
    TT.style.display='block';
    TT.style.left=(x+14)+'px';TT.style.top=(y-10)+'px';
}}
function hideTT(){{TT.style.display='none';}}
document.addEventListener('mousemove',e=>{{
    if(TT.style.display==='block'){{TT.style.left=(e.clientX+14)+'px';TT.style.top=(e.clientY-10)+'px';}}
}});

// ── Ripple on click ───────────────────────────────────────────────────────
function ripple(e,el){{
    const rect=el.getBoundingClientRect();
    el.style.setProperty('--rx',(e.clientX-rect.left)+'px');
    el.style.setProperty('--ry',(e.clientY-rect.top)+'px');
    el.classList.remove('ripple');
    void el.offsetWidth;
    el.classList.add('ripple');
    setTimeout(()=>el.classList.remove('ripple'),700);
}}

// ── 1. Line Chart ─────────────────────────────────────────────────────────
(function(){{
    const ctx=document.getElementById('lineChart').getContext('2d');
    new Chart(ctx,{{
        type:'line',
        data:{{
            datasets:[
                {{label:'Men',data:D.menTimes.map((t,i)=>{{return {{x:D.menYears[i],y:t}}}}),
                  borderColor:'#e8933a',backgroundColor:'rgba(232,147,58,0.06)',
                  borderWidth:2,pointRadius:2,pointHoverRadius:5,
                  pointBackgroundColor:'#e8933a',tension:0.3,fill:true}},
                {{label:'Women',data:D.womenTimes.map((t,i)=>{{return {{x:D.womenYears[i],y:t}}}}),
                  borderColor:'#e86850',backgroundColor:'rgba(232,104,80,0.05)',
                  borderWidth:2,pointRadius:2,pointHoverRadius:5,
                  pointBackgroundColor:'#e86850',tension:0.3,fill:true}},
            ]
        }},
        options:{{
            responsive:true,maintainAspectRatio:true,
            interaction:{{mode:'index',intersect:false}},
            animation:{{duration:1200,easing:'easeOutQuart'}},
            plugins:{{
                legend:{{labels:{{color:'#7a7468',boxWidth:10,font:{{size:11}}}}}},
                tooltip:{{
                    backgroundColor:'rgba(10,9,14,0.95)',
                    borderColor:'rgba(232,147,58,0.2)',borderWidth:1,
                    titleColor:'#e8933a',bodyColor:'#c8c0b0',
                    callbacks:{{label:c=>' '+c.dataset.label+': '+mins2hms(c.parsed.y)}}
                }}
            }},
            scales:{{
                x:{{type:'linear',title:{{display:true,text:'Year',color:'#4a4540'}},
                    ticks:{{color:'#4a4540',maxTicksLimit:12}},grid:{{color:'rgba(232,147,58,0.05)'}}}},
                y:{{title:{{display:true,text:'Time (min)',color:'#4a4540'}},
                    ticks:{{color:'#4a4540',callback:v=>Math.floor(v/60)+'h'+String(Math.floor(v%60)).padStart(2,'0')+'m'}},
                    grid:{{color:'rgba(232,147,58,0.05)'}}}}
            }}
        }}
    }});
}})();

// ── 2. Scatter ────────────────────────────────────────────────────────────
(function(){{
    const ctx=document.getElementById('scatterChart').getContext('2d');
    const men=D.scatter.filter(d=>d.g==='Male').map(d=>{{return{{x:d.x,y:d.s,_d:d}}}});
    const women=D.scatter.filter(d=>d.g==='Female').map(d=>{{return{{x:d.x,y:d.s,_d:d}}}});
    const ch=new Chart(ctx,{{
        type:'scatter',
        data:{{datasets:[
            {{label:'Men',data:men,backgroundColor:'rgba(232,147,58,0.5)',
              borderColor:'rgba(232,147,58,0.8)',borderWidth:1,pointRadius:4,pointHoverRadius:7}},
            {{label:'Women',data:women,backgroundColor:'rgba(232,104,80,0.5)',
              borderColor:'rgba(232,104,80,0.8)',borderWidth:1,pointRadius:4,pointHoverRadius:7}},
        ]}},
        options:{{
            responsive:true,maintainAspectRatio:false,
            animation:{{duration:1000}},
            plugins:{{
                legend:{{labels:{{color:'#7a7468',boxWidth:10,font:{{size:10}}}}}},
                tooltip:{{
                    backgroundColor:'rgba(10,9,14,0.95)',borderColor:'rgba(232,147,58,0.2)',borderWidth:1,
                    titleColor:'#e8933a',bodyColor:'#c8c0b0',
                    callbacks:{{
                        title:items=>items[0].raw._d.w+' ('+items[0].raw._d.x+')',
                        label:item=>' Speed: '+item.raw.y.toFixed(2)+' mph · Time: '+mins2hms(item.raw._d.y)+''
                    }}
                }}
            }},
            scales:{{
                x:{{title:{{display:true,text:'Year',color:'#4a4540'}},ticks:{{color:'#4a4540'}},grid:{{color:'rgba(232,147,58,0.05)'}}}},
                y:{{title:{{display:true,text:'Speed (mph)',color:'#4a4540'}},ticks:{{color:'#4a4540'}},grid:{{color:'rgba(232,147,58,0.05)'}}}}
            }}
        }}
    }});
}})();

// ── 3. Histogram ──────────────────────────────────────────────────────────
(function(){{
    const ctx=document.getElementById('histChart').getContext('2d');
    new Chart(ctx,{{
        type:'bar',
        data:{{
            labels:D.histBins.map(b=>Math.floor(b.x/60)+'h'+String(Math.round(b.x%60)).padStart(2,'0')+'m'),
            datasets:[{{
                label:'Winners',
                data:D.histBins.map(b=>b.y),
                backgroundColor:D.histBins.map((_,i)=>{{
                    const t=i/D.histBins.length;
                    return `rgba(${{Math.round(232-t*40)}},${{Math.round(147-t*60)}},${{Math.round(58+t*20)}},0.75)`;
                }}),
                borderColor:'transparent',borderRadius:4,
            }}]
        }},
        options:{{
            responsive:true,maintainAspectRatio:false,
            animation:{{duration:900,easing:'easeOutBounce'}},
            plugins:{{
                legend:{{display:false}},
                tooltip:{{backgroundColor:'rgba(10,9,14,0.95)',borderColor:'rgba(232,147,58,0.2)',borderWidth:1,
                    titleColor:'#e8933a',bodyColor:'#c8c0b0'}}
            }},
            scales:{{
                x:{{ticks:{{color:'#4a4540',maxRotation:45,font:{{size:9}}}},grid:{{display:false}}}},
                y:{{ticks:{{color:'#4a4540'}},grid:{{color:'rgba(232,147,58,0.05)'}}}}
            }}
        }}
    }});
}})();

// ── 4. Horizontal Bar (countries) ─────────────────────────────────────────
(function(){{
    const ctx=document.getElementById('barChart').getContext('2d');
    const n=D.countryLabels.length;
    new Chart(ctx,{{
        type:'bar',
        data:{{
            labels:D.countryLabels,
            datasets:[{{
                label:'Wins',
                data:D.countryVals,
                backgroundColor:D.countryVals.map((_,i)=>{{
                    const t=i/n;
                    return `rgba(${{Math.round(232-t*80)}},${{Math.round(147-t*80)}},${{Math.round(58+t*30)}},0.8)`;
                }}),
                borderColor:'transparent',borderRadius:6,
            }}]
        }},
        options:{{
            indexAxis:'y',responsive:true,maintainAspectRatio:false,
            animation:{{duration:1000,delay:(ctx)=>ctx.dataIndex*80}},
            plugins:{{
                legend:{{display:false}},
                tooltip:{{backgroundColor:'rgba(10,9,14,0.95)',borderColor:'rgba(232,147,58,0.2)',borderWidth:1,
                    titleColor:'#e8933a',bodyColor:'#c8c0b0',
                    callbacks:{{label:c=>' '+c.parsed.x+' wins'}}}}
            }},
            scales:{{
                x:{{ticks:{{color:'#4a4540'}},grid:{{color:'rgba(232,147,58,0.05)'}}}},
                y:{{ticks:{{color:'#c8c0b0',font:{{size:11,weight:'600'}}}},grid:{{display:false}}}}
            }}
        }}
    }});
}})();

// ── 5. Decade grouped bar ─────────────────────────────────────────────────
(function(){{
    const ctx=document.getElementById('decadeChart').getContext('2d');
    new Chart(ctx,{{
        type:'bar',
        data:{{
            labels:D.decLabels,
            datasets:[
                {{label:'Men',data:D.decMen,backgroundColor:'rgba(232,147,58,0.75)',
                  borderColor:'transparent',borderRadius:4}},
                {{label:'Women',data:D.decWomen,backgroundColor:'rgba(232,104,80,0.75)',
                  borderColor:'transparent',borderRadius:4}},
            ]
        }},
        options:{{
            responsive:true,maintainAspectRatio:false,
            animation:{{duration:1000,easing:'easeOutQuart'}},
            plugins:{{
                legend:{{labels:{{color:'#7a7468',boxWidth:10,font:{{size:10}}}}}},
                tooltip:{{backgroundColor:'rgba(10,9,14,0.95)',borderColor:'rgba(232,147,58,0.2)',borderWidth:1,
                    titleColor:'#e8933a',bodyColor:'#c8c0b0'}}
            }},
            scales:{{
                x:{{ticks:{{color:'#4a4540',maxRotation:45,font:{{size:9}}}},grid:{{display:false}}}},
                y:{{ticks:{{color:'#4a4540'}},grid:{{color:'rgba(232,147,58,0.05)'}}}}
            }}
        }}
    }});
}})();

// ── 6. Bubble chart ───────────────────────────────────────────────────────
(function(){{
    const ctx=document.getElementById('bubbleChart').getContext('2d');
    const men=D.scatter.filter(d=>d.g==='Male').map(d=>{{
        return{{x:d.x,y:d.y,r:Math.max(3,Math.min(14,(d.s-9)*3)),_d:d}};
    }});
    const women=D.scatter.filter(d=>d.g==='Female').map(d=>{{
        return{{x:d.x,y:d.y,r:Math.max(3,Math.min(14,(d.s-9)*3)),_d:d}};
    }});
    new Chart(ctx,{{
        type:'bubble',
        data:{{datasets:[
            {{label:'Men',data:men,backgroundColor:'rgba(232,147,58,0.4)',
              borderColor:'rgba(232,147,58,0.7)',borderWidth:1}},
            {{label:'Women',data:women,backgroundColor:'rgba(232,104,80,0.4)',
              borderColor:'rgba(232,104,80,0.7)',borderWidth:1}},
        ]}},
        options:{{
            responsive:true,maintainAspectRatio:true,
            animation:{{duration:1200,easing:'easeOutElastic'}},
            plugins:{{
                legend:{{labels:{{color:'#7a7468',boxWidth:10,font:{{size:11}}}}}},
                tooltip:{{
                    backgroundColor:'rgba(10,9,14,0.95)',borderColor:'rgba(232,147,58,0.2)',borderWidth:1,
                    titleColor:'#e8933a',bodyColor:'#c8c0b0',
                    callbacks:{{
                        title:items=>items[0].raw._d.w+' ('+items[0].raw._d.x+')',
                        label:item=>' Time: '+mins2hms(item.raw.y)+' · Speed: '+item.raw._d.s+' mph'
                    }}
                }}
            }},
            scales:{{
                x:{{title:{{display:true,text:'Year',color:'#4a4540'}},ticks:{{color:'#4a4540'}},grid:{{color:'rgba(232,147,58,0.05)'}}}},
                y:{{title:{{display:true,text:'Time (min)',color:'#4a4540'}},
                    ticks:{{color:'#4a4540',callback:v=>Math.floor(v/60)+'h'+String(Math.floor(v%60)).padStart(2,'0')+'m'}},
                    grid:{{color:'rgba(232,147,58,0.05)'}}}}
            }}
        }}
    }});
}})();

// ── Scroll-triggered entrance ─────────────────────────────────────────────
(function(){{
    const obs=new IntersectionObserver(entries=>{{
        entries.forEach(e=>{{if(e.isIntersecting)e.target.classList.add('visible');}});
    }},{{threshold:0.08}});
    document.querySelectorAll('.fade-up').forEach(el=>obs.observe(el));
}})();
</script>
</body>
</html>
"""

components.html(html, height=5200, scrolling=False)

# ── Still render Streamlit charts below for deep-dive ─────────────────────────
from charts import (
    plot_pie_chart, plot_boxplot, plot_heatmap, plot_violin,
    plot_pairplot, plot_funnel_chart
)

st.markdown("""
<div style='text-align:center;padding:20px 0 8px;'>
    <span style='background:rgba(232,147,58,0.07);border:1px solid rgba(232,147,58,0.14);
        color:#e8933a;padding:5px 16px;border-radius:100px;
        font-size:0.6rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;
        font-family:Inter,sans-serif;'>Deep Dive Analytics</span>
</div>
""", unsafe_allow_html=True)

def mins_to_hms(m):
    try: return f"{int(m//60)}:{int(m%60):02d}:{int((m%1)*60):02d}"
    except: return "N/A"

def section(n, title, subtitle):
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:14px;padding:32px 0 18px;'>
        <div style='width:30px;height:30px;border-radius:50%;
            background:linear-gradient(135deg,#b06018,#e8933a);
            color:#07070a;font-size:0.7rem;font-weight:900;
            display:flex;align-items:center;justify-content:center;
            box-shadow:0 0 14px rgba(232,147,58,0.3);flex-shrink:0;
            font-family:Inter,sans-serif;'>{n}</div>
        <div>
            <p style='font-family:Georgia,serif;font-size:1.1rem;font-weight:700;
                color:#f5f0e8;margin:0;letter-spacing:-0.3px;'>{title}</p>
            <p style='font-size:0.68rem;color:#7a7468;margin:2px 0 0;
                font-family:Inter,sans-serif;'>{subtitle}</p>
        </div>
        <div style='flex:1;height:1px;background:linear-gradient(90deg,rgba(232,147,58,0.15),transparent);'></div>
    </div>""", unsafe_allow_html=True)

def nc(fn, data, name):
    try:
        b = fn(data)
        if b: st.image(b, use_container_width=True)
        else: st.info(f"No data for {name}")
    except Exception as e:
        st.warning(f"{name}: {str(e)[:80]}")
    finally:
        gc.collect()

def wrap(fn, data, name):
    st.markdown('<div style="background:linear-gradient(145deg,#0f0e13,#141318);border:1px solid rgba(232,147,58,0.07);border-radius:18px;padding:8px;margin-bottom:16px;overflow:hidden;">', unsafe_allow_html=True)
    nc(fn, data, name)
    st.markdown('</div>', unsafe_allow_html=True)

section("A", "Statistical Distribution", "Box plots, violin plots, and correlation heatmap")
ca, cb = st.columns(2)
with ca: wrap(plot_boxplot, filtered_df, "Box Plot")
with cb: wrap(plot_violin, filtered_df, "Violin Plot")
wrap(plot_heatmap, filtered_df, "Heatmap")

section("B", "Composition & Brackets", "Country donut and time bracket funnel")
cc, cd = st.columns(2)
with cc: wrap(plot_pie_chart, filtered_df, "Pie Chart")
with cd: wrap(plot_funnel_chart, filtered_df, "Funnel Chart")

section("C", "Multi-Feature Pair Analysis", "Relationship matrix — expand to view")
with st.expander("🔬 Pair Plot — click to expand", expanded=False):
    nc(plot_pairplot, filtered_df, "Pair Plot")

# ── Data explorer ──────────────────────────────────────────────────────────────
section("D", "Data Explorer", "Browse and download the filtered dataset")
disp = [c for c in ["Year","Winner","Country","Gender","Time","Time_Minutes",
                     "Speed_MPH","Pace_Per_Mile","Distance (Miles)","Decade_Label"]
        if c in filtered_df.columns]
st.dataframe(filtered_df[disp].reset_index(drop=True), use_container_width=True, height=380)

import io
_edf = filtered_df[[c for c in ["Year","Winner","Country","Gender","Time","Time_Minutes",
    "Speed_MPH","Pace_Per_Mile","Distance (Miles)","Distance (KM)","Decade_Label"]
    if c in filtered_df.columns]].reset_index(drop=True)
_buf = io.StringIO(); _edf.to_csv(_buf, index=False); _cbytes = _buf.getvalue().encode()
ex1, ex2, ex3 = st.columns(3)
with ex1:
    st.download_button("⬇️ Filtered CSV", _cbytes,
        f"boston_filtered_{len(_edf)}.csv", "text/csv", use_container_width=True)
with ex2:
    st.download_button("⬇️ Men's Full CSV",
        open("data/Mens_Boston_Marathon_Winners_r0l7bV.csv","rb").read(),
        "boston_mens_full.csv","text/csv",use_container_width=True)
with ex3:
    st.download_button("⬇️ Women's Full CSV",
        open("data/Womens_Boston_Marathon_Winners_8SSnWb.csv","rb").read(),
        "boston_womens_full.csv","text/csv",use_container_width=True)
