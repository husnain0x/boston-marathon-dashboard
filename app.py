"""
app.py — Boston Marathon Elite Dashboard
All 10 required + 3 bonus charts. Cinematic HTML/Chart.js + Matplotlib for statistical charts.
"""
import streamlit as st
import pandas as pd
import numpy as np
import json, gc, io
from filters import load_and_merge_data, apply_filters
import streamlit.components.v1 as components

st.set_page_config(page_title="Boston Marathon", page_icon="🏃", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
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
    box-shadow:0 12px 40px rgba(0,0,0,0.5);}
div[data-testid="stMetric"] label{
    color:#7a7468!important;font-size:0.6rem!important;
    font-weight:700!important;letter-spacing:2px;text-transform:uppercase;}
div[data-testid="stMetric"] div[data-testid="stMetricValue"]{
    color:#f5f0e8!important;font-size:1.4rem!important;font-weight:800!important;}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"]{color:#e8933a!important;font-size:0.65rem!important;}
.stButton>button{
    background:linear-gradient(135deg,#b86a18,#e8933a)!important;
    color:#07070a!important;border:none!important;border-radius:10px!important;
    font-weight:700!important;font-size:0.78rem!important;}
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
.block-container{padding-top:0.5rem!important;padding-bottom:0!important;}
iframe{display:block!important;border:none!important;}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_and_merge_data()

try:
    df = get_data()
except Exception as e:
    st.error(f"Data load error: {e}"); st.stop()

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
    st.warning("No data matches your filters."); st.stop()

# ── Helpers ───────────────────────────────────────────────────────────────────
def hms(m):
    try: return f"{int(m//60)}:{int(m%60):02d}:{int((m%1)*60):02d}"
    except: return "N/A"

def safe(x, fb="N/A"):
    try: return x if pd.notna(x) else fb
    except: return fb

# ── Compute all data for JS ───────────────────────────────────────────────────
td       = filtered_df["Time_Minutes"].dropna()
avg_t    = float(td.mean())  if len(td) else 0
fast_t   = float(td.min())   if len(td) else 0
slow_t   = float(td.max())   if len(td) else 0
med_t    = float(td.median()) if len(td) else 0
std_t    = round(float(td.std()),1) if len(td)>1 else 0
fast_row = filtered_df.loc[filtered_df["Time_Minutes"].idxmin()] if len(td) else None
avg_spd  = float(filtered_df["Speed_MPH"].dropna().mean()) if len(filtered_df) else 0
avg_pace = round(float(filtered_df["Pace_Per_Mile"].dropna().mean()),2) if len(filtered_df) else 0

# Men/Women trend
tm = filtered_df[filtered_df["Gender"]=="Male"].dropna(subset=["Time_Minutes"]).sort_values("Year")
tw = filtered_df[filtered_df["Gender"]=="Female"].dropna(subset=["Time_Minutes"]).sort_values("Year")
men_years   = tm["Year"].astype(int).tolist()
men_times   = [round(float(x),1) for x in tm["Time_Minutes"].tolist()]
women_years = tw["Year"].astype(int).tolist()
women_times = [round(float(x),1) for x in tw["Time_Minutes"].tolist()]

# Cumulative area data
men_cum   = list(range(1, len(men_years)+1))
women_cum = list(range(1, len(women_years)+1))

# Countries
cc = filtered_df["Country"].value_counts().head(10)
country_labels = cc.index.tolist()
country_vals   = cc.values.tolist()

# Pie top 7 + others
pie_top = filtered_df["Country"].value_counts().head(7)
if len(filtered_df["Country"].value_counts()) > 7:
    others = filtered_df["Country"].value_counts().iloc[7:].sum()
    pie_labels = pie_top.index.tolist() + ["Others"]
    pie_vals   = pie_top.values.tolist() + [int(others)]
else:
    pie_labels = pie_top.index.tolist()
    pie_vals   = pie_top.values.tolist()

# Decade
fdf2 = filtered_df.copy()
fdf2["Decade"] = (fdf2["Year"]//10)*10
dm = fdf2[fdf2["Gender"]=="Male"].groupby("Decade").size()
dw = fdf2[fdf2["Gender"]=="Female"].groupby("Decade").size()
all_dec = sorted(set(dm.index.tolist()+dw.index.tolist()))
dec_labels  = [f"{int(d)}s" for d in all_dec]
dec_men_v   = [int(dm.get(d,0)) for d in all_dec]
dec_women_v = [int(dw.get(d,0)) for d in all_dec]

# Histogram
hist_raw = td.tolist()
h_min,h_max = (min(hist_raw),max(hist_raw)) if hist_raw else (120,220)
edges = list(np.linspace(h_min,h_max,16))
hcnts,_ = np.histogram(hist_raw, bins=edges)
hist_bins = [{"x":round((edges[i]+edges[i+1])/2,1),"y":int(hcnts[i])} for i in range(len(hcnts))]

# Scatter sample
sdf = filtered_df.dropna(subset=["Time_Minutes","Speed_MPH"])
ss  = sdf.sample(min(180,len(sdf)), random_state=42)
scatter_data = [{"x":int(r.Year),"y":round(float(r.Time_Minutes),1),
                 "s":round(float(r.Speed_MPH),2),"g":r.Gender,"w":r.Winner}
                for r in ss.itertuples()]

# Hall of fame
hof = filtered_df.groupby("Winner").agg(
    wins=("Year","count"),country=("Country","first"),
    first=("Year","min"),last=("Year","max")
).sort_values("wins",ascending=False).head(5).reset_index()
hof_data = [{"name":r.Winner,"country":r.country,
             "wins":int(r.wins),"first":int(r.first),"last":int(r.last)}
            for r in hof.itertuples()]

# Stats
fast_name  = safe(fast_row["Winner"])   if fast_row is not None else "N/A"
fast_year  = int(safe(fast_row["Year"],0)) if fast_row is not None else 0
tsr        = filtered_df.loc[filtered_df["Speed_MPH"].idxmax()] if len(filtered_df) else None
top_spd_n  = safe(tsr["Winner"]) if tsr is not None else "N/A"
top_spd_v  = round(float(tsr["Speed_MPH"]),2) if tsr is not None else 0
male_avg   = round(float(filtered_df[filtered_df["Gender"]=="Male"]["Time_Minutes"].mean()),1) if "Male" in filtered_df["Gender"].values else None
female_avg = round(float(filtered_df[filtered_df["Gender"]=="Female"]["Time_Minutes"].mean()),1) if "Female" in filtered_df["Gender"].values else None

# Funnel
bins_f=[0,130,140,150,160,170,180,300]
labels_f=["< 2:10","2:10–2:20","2:20–2:30","2:30–2:40","2:40–2:50","2:50–3:00","3:00+"]
fdf3=filtered_df.copy()
fdf3["Bracket"]=pd.cut(fdf3["Time_Minutes"],bins=bins_f,labels=labels_f)
fcnts=fdf3["Bracket"].value_counts().reindex(labels_f).fillna(0)
funnel_labels=[l for l,v in zip(labels_f,fcnts.values) if v>0]
funnel_vals=[int(v) for v in fcnts.values if v>0]

js_data = json.dumps({
    "menYears":men_years,"menTimes":men_times,
    "womenYears":women_years,"womenTimes":women_times,
    "menCum":men_cum,"womenCum":women_cum,
    "pieLabels":pie_labels,"pieVals":pie_vals,
    "countryLabels":country_labels,"countryVals":country_vals,
    "decLabels":dec_labels,"decMen":dec_men_v,"decWomen":dec_women_v,
    "scatter":scatter_data,"histBins":hist_bins,
    "funnelLabels":funnel_labels,"funnelVals":funnel_vals,
    "hof":hof_data,
    "stats":{
        "total":len(filtered_df),"avgTime":round(avg_t,1),
        "fastHMS":hms(fast_t),"fastName":fast_name,"fastYear":fast_year,
        "avgSpeed":round(avg_spd,2),"medTime":round(med_t,1),"stdT":std_t,
        "countries":int(filtered_df["Country"].nunique()),
        "uniqueWinners":int(filtered_df["Winner"].nunique()),
        "yrMin":int(filtered_df["Year"].min()),"yrMax":int(filtered_df["Year"].max()),
        "improvement":round(slow_t-fast_t,1),
        "avgPace":avg_pace,"topSpeedName":top_spd_n,"topSpeedVal":top_spd_v,
        "maleAvg":male_avg,"femaleAvg":female_avg,
        "menCount":len(men_years),"womenCount":len(women_years),
    }
})

# ── Render Matplotlib charts (Box, Violin, Heatmap, Pair Plot) as base64 ─────
from charts import (plot_boxplot, plot_violin, plot_heatmap, plot_area_chart,
                    plot_pairplot, plot_scatter, plot_countplot)
import base64

def chart_b64(fn, data):
    try:
        b = fn(data)
        if b: return "data:image/png;base64," + base64.b64encode(b).decode()
    except: pass
    return ""
    gc.collect()

box_img    = chart_b64(plot_boxplot,   filtered_df)
violin_img = chart_b64(plot_violin,    filtered_df)
heat_img   = chart_b64(plot_heatmap,   filtered_df)
area_img   = chart_b64(plot_area_chart, filtered_df)
count_img  = chart_b64(plot_countplot,  filtered_df)
pair_img   = chart_b64(plot_pairplot,   filtered_df)
scatter_img= chart_b64(plot_scatter,    filtered_df)
gc.collect()

# ── Build HTML ────────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
:root{{
  --bg:#07070a;--bg1:#0b0b0f;--bg2:#0f0e13;--bg3:#141318;
  --amber:#e8933a;--amber2:#f0a852;--gold:#d4a850;--red:#e86850;
  --tw:#f5f0e8;--tl:#c8c0b0;--td:#7a7468;--tm:#4a4540;
  --b:rgba(232,147,58,0.08);--b2:rgba(232,147,58,0.18);
}}
html{{background:var(--bg);color:var(--tw);font-family:'Inter','Arial',sans-serif;
  overflow-x:hidden;scroll-behavior:smooth;}}
body{{min-height:100vh;}}

/* Particle */
#pc{{position:fixed;top:0;left:0;width:100%;height:100%;
  pointer-events:none;z-index:0;opacity:0.3;}}

/* Hero */
.hero{{position:relative;z-index:1;
  background:linear-gradient(160deg,#0a080d 0%,#0f0c0a 40%,#080a0d 100%);
  border-bottom:1px solid var(--b);padding:40px 36px 32px;overflow:hidden;}}
.hero-bg{{position:absolute;right:0;top:50%;transform:translateY(-50%);
  font-size:clamp(80px,14vw,180px);font-weight:900;color:rgba(232,147,58,0.035);
  letter-spacing:-8px;pointer-events:none;line-height:1;user-select:none;font-family:Georgia,serif;}}
.eyebrow{{display:inline-flex;align-items:center;gap:8px;
  background:rgba(232,147,58,0.07);border:1px solid rgba(232,147,58,0.14);
  padding:4px 12px;border-radius:100px;font-size:0.6rem;font-weight:700;
  letter-spacing:2.5px;text-transform:uppercase;color:var(--amber);margin-bottom:14px;}}
.hero h1{{font-size:clamp(2rem,4.5vw,3.5rem);font-weight:800;color:var(--tw);
  letter-spacing:-1.5px;line-height:1.05;margin-bottom:5px;font-family:Georgia,serif;}}
.hero h1 span{{color:var(--amber);}}
.hero-sub{{font-size:0.82rem;color:var(--td);margin-bottom:24px;line-height:1.6;}}

/* Route strip */
.route{{display:flex;align-items:center;margin-bottom:8px;}}
.rd{{width:11px;height:11px;border-radius:50%;background:var(--amber);flex-shrink:0;
  box-shadow:0 0 12px rgba(232,147,58,0.6);}}
.rpath{{flex:1;height:3px;margin:0 6px;position:relative;overflow:visible;}}
.rline{{width:100%;height:100%;
  background:linear-gradient(90deg,var(--amber),#c47520 45%,#5a2e08 75%,rgba(232,147,58,0.1));
  border-radius:2px;}}
.runner{{position:absolute;top:50%;transform:translateY(-50%);
  font-size:1rem;animation:run 7s linear infinite;
  filter:drop-shadow(0 0 5px rgba(232,147,58,0.8));}}
@keyframes run{{0%{{left:-2%;opacity:0;}}5%{{opacity:1;}}92%{{opacity:1;}}100%{{left:98%;opacity:0;}}}}
.hb-pin{{position:absolute;top:-26px;left:70%;transform:translateX(-50%);text-align:center;white-space:nowrap;}}
.hb-lbl{{background:rgba(220,50,30,0.12);border:1px solid rgba(220,50,30,0.25);
  color:#e84530;font-size:0.48rem;font-weight:700;letter-spacing:1px;
  padding:2px 6px;border-radius:4px;text-transform:uppercase;}}
.hb-tick{{width:1px;height:9px;background:rgba(220,50,30,0.3);margin:0 auto;}}
.rde{{width:11px;height:11px;border-radius:50%;flex-shrink:0;
  border:2px solid rgba(232,147,58,0.3);background:rgba(232,147,58,0.06);}}
.route-lbl{{display:flex;justify-content:space-between;margin-top:5px;
  font-size:0.57rem;font-weight:600;letter-spacing:1px;}}
.route-lbl .s1{{color:var(--amber);}} .route-lbl .s2,.route-lbl .s3{{color:var(--tm);}}

/* Milestones */
.ms-row{{display:flex;gap:8px;padding:16px 36px;
  background:linear-gradient(90deg,var(--bg1),var(--bg));
  border-bottom:1px solid var(--b);overflow-x:auto;flex-wrap:nowrap;
  position:relative;z-index:1;scrollbar-width:thin;
  scrollbar-color:rgba(232,147,58,0.2) transparent;}}
.ms{{flex:0 0 auto;min-width:150px;max-width:185px;
  background:var(--bg2);border:1px solid var(--b);
  border-radius:12px;padding:12px;position:relative;overflow:hidden;
  transition:border-color 0.3s,transform 0.25s;cursor:default;}}
.ms:hover{{border-color:var(--b2);transform:translateY(-2px);}}
.ms::before{{content:'';position:absolute;left:0;top:0;bottom:0;width:2px;
  background:linear-gradient(180deg,var(--amber),transparent);}}
.ms-yr{{color:var(--amber);font-size:0.7rem;font-weight:800;margin-bottom:4px;}}
.ms-txt{{color:var(--td);font-size:0.62rem;line-height:1.5;}}
.ms-txt b{{color:var(--tl);}}

/* KPI bar */
.kpi-bar{{display:flex;gap:0;padding:0 36px;
  border-bottom:1px solid var(--b);position:relative;z-index:1;}}
.kpi{{flex:1;padding:18px 0;border-right:1px solid var(--b);
  text-align:center;transition:background 0.3s;}}
.kpi:last-child{{border-right:none;}}
.kpi:hover{{background:rgba(232,147,58,0.03);}}
.kpi-lbl{{color:var(--tm);font-size:0.54rem;font-weight:700;letter-spacing:2px;
  text-transform:uppercase;margin-bottom:4px;}}
.kpi-val{{color:var(--tw);font-size:1.2rem;font-weight:800;letter-spacing:-0.5px;}}
.kpi-val span{{color:var(--amber);}}
.kpi-sub{{color:var(--td);font-size:0.57rem;margin-top:1px;}}

/* Section header */
.sec{{display:flex;align-items:center;gap:12px;padding:36px 36px 18px;
  position:relative;z-index:1;}}
.sec-n{{display:flex;align-items:center;justify-content:center;
  width:28px;height:28px;border-radius:50%;
  background:linear-gradient(135deg,#b06018,var(--amber));
  color:#07070a;font-size:0.68rem;font-weight:900;flex-shrink:0;
  box-shadow:0 0 12px rgba(232,147,58,0.3);}}
.sec-info .st{{font-size:1.05rem;font-weight:700;color:var(--tw);
  font-family:Georgia,serif;letter-spacing:-0.3px;}}
.sec-info .ss{{font-size:0.65rem;color:var(--td);margin-top:1px;}}
.sec-line{{flex:1;height:1px;background:linear-gradient(90deg,rgba(232,147,58,0.15),transparent);}}

/* Chart grid */
.cg{{display:grid;gap:14px;padding:0 36px 8px;position:relative;z-index:1;}}
.cg.two{{grid-template-columns:1fr 1fr;}}
.cg.one{{grid-template-columns:1fr;}}
.cg.three{{grid-template-columns:1fr 1fr 1fr;}}

/* Chart card */
.cc{{background:linear-gradient(145deg,var(--bg2),var(--bg3));
  border:1px solid var(--b);border-radius:16px;overflow:hidden;
  transition:border-color 0.4s,transform 0.3s,box-shadow 0.3s;
  cursor:pointer;position:relative;}}
.cc:hover{{border-color:var(--b2);transform:translateY(-3px);
  box-shadow:0 14px 45px rgba(0,0,0,0.5),0 0 40px rgba(232,147,58,0.05);}}
.cc::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(232,147,58,0.12),transparent);}}
/* ripple */
.cc.rpl::after{{content:'';position:absolute;border-radius:50%;
  background:rgba(232,147,58,0.1);width:180px;height:180px;
  margin:-90px 0 0 -90px;
  animation:rpl 0.55s ease-out;pointer-events:none;
  top:var(--ry,50%);left:var(--rx,50%);}}
@keyframes rpl{{0%{{transform:scale(0);opacity:1;}}100%{{transform:scale(5);opacity:0;}}}}
.ch{{padding:14px 18px 6px;}}
.ct{{font-size:0.76rem;font-weight:700;color:var(--tl);letter-spacing:0.3px;}}
.cs{{font-size:0.6rem;color:var(--tm);margin-top:2px;}}
.cb{{padding:0 12px 12px;}}
canvas{{display:block;width:100%!important;}}
/* static image charts */
.img-chart{{width:100%;display:block;border-radius:8px;}}

/* Caption */
.cap{{background:rgba(232,147,58,0.03);border:1px solid rgba(232,147,58,0.06);
  border-radius:10px;padding:9px 14px;margin:2px 36px 18px;
  font-size:0.66rem;color:var(--td);line-height:1.6;position:relative;z-index:1;}}
.cap b{{color:#a89070;}}

/* Insight strip */
.ins{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;
  padding:0 36px 8px;position:relative;z-index:1;}}
.ic{{background:linear-gradient(145deg,var(--bg2),var(--bg3));
  border:1px solid var(--b);border-radius:13px;padding:14px 16px;
  position:relative;overflow:hidden;transition:border-color 0.3s,transform 0.25s;}}
.ic:hover{{border-color:var(--b2);transform:translateY(-2px);}}
.ic::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(232,147,58,0.1),transparent);}}
.ic-l{{color:var(--tm);font-size:0.56rem;font-weight:700;letter-spacing:2px;
  text-transform:uppercase;margin-bottom:4px;}}
.ic-v{{color:var(--amber);font-size:1.05rem;font-weight:800;
  letter-spacing:-0.3px;margin-bottom:3px;}}
.ic-d{{color:var(--td);font-size:0.66rem;line-height:1.5;}}
.ic-d b{{color:var(--tl);font-weight:600;}}

/* Fact banner */
.fb{{display:flex;align-items:flex-start;gap:12px;
  background:linear-gradient(135deg,rgba(232,147,58,0.04),rgba(212,168,80,0.03));
  border:1px solid rgba(232,147,58,0.09);border-radius:13px;
  padding:13px 18px;margin:2px 36px 24px;position:relative;z-index:1;}}
.fb-i{{font-size:1.1rem;flex-shrink:0;margin-top:1px;}}
.fb-t{{color:var(--td);font-size:0.7rem;line-height:1.65;}}
.fb-t b{{color:var(--amber);}}

/* Hall of Fame */
.hof{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;
  padding:0 36px 8px;position:relative;z-index:1;}}
.hc{{background:linear-gradient(145deg,var(--bg2),var(--bg3));
  border:1px solid var(--b);border-radius:15px;padding:16px 12px;
  text-align:center;position:relative;overflow:hidden;
  transition:border-color 0.3s,transform 0.3s;cursor:default;}}
.hc:hover{{border-color:var(--b2);transform:translateY(-4px);
  box-shadow:0 12px 35px rgba(0,0,0,0.5),0 0 25px rgba(232,147,58,0.06);}}
.hc::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,rgba(232,147,58,0.25),transparent);}}
.hc-rk{{color:var(--tm);font-size:0.52rem;font-weight:700;letter-spacing:2px;
  text-transform:uppercase;margin-bottom:6px;}}
.hc-med{{font-size:1.7rem;margin-bottom:6px;}}
.hc-nm{{color:var(--tw);font-size:0.72rem;font-weight:700;margin-bottom:2px;line-height:1.3;}}
.hc-co{{color:var(--td);font-size:0.58rem;margin-bottom:8px;}}
.hc-w{{color:var(--amber);font-size:1.9rem;font-weight:900;letter-spacing:-1.5px;}}
.hc-wl{{color:var(--tm);font-size:0.52rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;}}
.hc-yr{{color:var(--tm);font-size:0.54rem;margin-top:2px;}}

/* Tooltip */
.tt{{position:fixed;pointer-events:none;z-index:9999;
  background:rgba(10,9,14,0.96);border:1px solid var(--b2);
  border-radius:10px;padding:9px 13px;font-size:0.7rem;color:var(--tl);
  max-width:200px;box-shadow:0 8px 28px rgba(0,0,0,0.6);display:none;
  backdrop-filter:blur(8px);}}
.tt-t{{color:var(--amber);font-weight:700;margin-bottom:2px;}}

/* Chart badge */
.cbadge{{display:inline-block;background:rgba(232,147,58,0.08);
  border:1px solid rgba(232,147,58,0.15);color:var(--amber);
  font-size:0.48rem;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;padding:2px 7px;border-radius:100px;
  margin-left:6px;vertical-align:middle;}}

/* Data table */
.dtable{{width:100%;border-collapse:collapse;font-size:0.7rem;
  font-family:'Inter','Arial',sans-serif;}}
.dtable th{{background:rgba(232,147,58,0.08);color:var(--amber);
  font-weight:700;letter-spacing:1px;text-transform:uppercase;
  padding:8px 12px;font-size:0.58rem;text-align:left;
  border-bottom:1px solid var(--b);}}
.dtable td{{padding:7px 12px;color:var(--tl);border-bottom:1px solid rgba(232,147,58,0.04);}}
.dtable tr:hover td{{background:rgba(232,147,58,0.03);}}

/* Footer */
.footer{{text-align:center;padding:28px 36px;margin-top:16px;
  border-top:1px solid var(--b);position:relative;z-index:1;}}
.footer p{{color:var(--tm);font-size:0.68rem;line-height:1.8;}}
.footer b{{color:var(--amber);}}

/* Fade-in on scroll */
.fade{{opacity:0;transform:translateY(18px);
  transition:opacity 0.55s ease,transform 0.55s ease;}}
.fade.in{{opacity:1;transform:translateY(0);}}

/* Responsive */
@media(max-width:860px){{
  .cg.two,.cg.three{{grid-template-columns:1fr;}}
  .hof{{grid-template-columns:repeat(3,1fr);}}
  .ins{{grid-template-columns:1fr;}}
  .kpi-bar{{flex-wrap:wrap;}}
  .kpi{{min-width:33.33%;border-right:none;border-bottom:1px solid var(--b);}}
}}
</style>
</head>
<body>
<canvas id="pc"></canvas>
<div class="tt" id="tt"><div class="tt-t" id="tt-t"></div><div id="tt-b"></div></div>

<!-- ═══ HERO ═══ -->
<div class="hero fade">
  <div class="hero-bg">26.2</div>
  <div class="eyebrow">🏃 Est. 1897 · Patriots Day · World Marathon Major</div>
  <h1>Boston <span>Marathon</span><br>Analytics</h1>
  <p class="hero-sub">127 years of champions · {int(filtered_df['Year'].min())}–{int(filtered_df['Year'].max())} · {len(filtered_df)} records · {int(filtered_df['Country'].nunique())} nations · 10 chart types</p>
  <div class="route">
    <div class="rd"></div>
    <div class="rpath">
      <div class="rline"></div>
      <span class="runner">🏃</span>
      <div class="hb-pin"><div class="hb-lbl">⚡ Heartbreak Hill · Mile 20</div><div class="hb-tick"></div></div>
    </div>
    <div class="rde"></div>
  </div>
  <div class="route-lbl">
    <span class="s1">▶ START · Hopkinton</span>
    <span class="s2">· · · 26.2 miles / 42.195 km · · ·</span>
    <span class="s3">FINISH · Boylston St ■</span>
  </div>
</div>

<!-- ═══ MILESTONES ═══ -->
<div class="ms-row fade">
  <div class="ms"><div class="ms-yr">1897</div><div class="ms-txt"><b>First Race.</b> 15 runners. McDermott wins in 2:55:10.</div></div>
  <div class="ms"><div class="ms-yr">1924</div><div class="ms-txt"><b>26.2 miles</b> standardized after Olympic distance rules.</div></div>
  <div class="ms"><div class="ms-yr">1967</div><div class="ms-txt"><b>Kathrine Switzer</b> — first numbered woman, nearly dragged off course.</div></div>
  <div class="ms"><div class="ms-yr">1972</div><div class="ms-txt"><b>Women officially allowed.</b> Nina Kuscsik wins inaugural women's race.</div></div>
  <div class="ms"><div class="ms-yr">1990s</div><div class="ms-txt"><b>Kenyan dominance</b> — altitude training redefines distance running.</div></div>
  <div class="ms"><div class="ms-yr">2011</div><div class="ms-txt"><b>Geoffrey Mutai</b> sets course record 2:03:02.</div></div>
  <div class="ms"><div class="ms-yr">Today</div><div class="ms-txt"><b>World Marathon Major.</b> 30,000 runners. Qualifying time required.</div></div>
</div>

<!-- ═══ KPI BAR ═══ -->
<div class="kpi-bar fade">
  <div class="kpi"><div class="kpi-lbl">Course Record</div><div class="kpi-val"><span id="k1">–</span></div><div class="kpi-sub" id="k1s">–</div></div>
  <div class="kpi"><div class="kpi-lbl">Avg Finish Time</div><div class="kpi-val" id="k2">–</div><div class="kpi-sub">Filtered avg</div></div>
  <div class="kpi"><div class="kpi-lbl">Avg Speed</div><div class="kpi-val"><span id="k3">–</span> <span style="font-size:0.75rem;color:var(--td)">mph</span></div><div class="kpi-sub">Winning avg</div></div>
  <div class="kpi"><div class="kpi-lbl">Nations</div><div class="kpi-val"><span id="k4">0</span></div><div class="kpi-sub">Countries</div></div>
  <div class="kpi"><div class="kpi-lbl">Unique Champions</div><div class="kpi-val"><span id="k5">0</span></div><div class="kpi-sub">Different athletes</div></div>
  <div class="kpi"><div class="kpi-lbl">Year Span</div><div class="kpi-val" id="k6">–</div><div class="kpi-sub">Race history</div></div>
</div>

<!-- ═══ SECTION 1: HALL OF FAME ═══ -->
<div class="sec fade"><div class="sec-n">1</div><div class="sec-info"><div class="st">Hall of Fame</div><div class="ss">Most decorated champions in Boston Marathon history</div></div><div class="sec-line"></div></div>
<div class="hof fade" id="hof"></div>
<div class="fb fade"><div class="fb-i">🏆</div><div class="fb-t"><b>Clarence DeMar</b> (7 wins, 1911–1930) is the all-time Boston legend. Modern era: <b>Robert Kipkoech Cheruiyot</b> & <b>Catherine Ndereba</b> (4 wins each). Hall of Fame updates live with your sidebar filters.</div></div>

<!-- ═══ SECTION 2: PIE + HISTOGRAM ═══ -->
<div class="sec fade"><div class="sec-n">2</div><div class="sec-info"><div class="st">Overview & Composition <span class="cbadge">Chart 1 · 2</span></div><div class="ss">Pie Chart — national distribution · Histogram — finishing time frequency</div></div><div class="sec-line"></div></div>
<div class="cg two fade">
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Winners by Country <span class="cbadge">Pie Chart</span></div><div class="cs">Proportional distribution · Hover for count</div></div>
    <div class="cb"><canvas id="pieChart" height="200"></canvas></div>
  </div>
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Finishing Time Distribution <span class="cbadge">Histogram</span></div><div class="cs">Frequency of winning times in minutes · Mean line shown</div></div>
    <div class="cb"><canvas id="histChart" height="200"></canvas></div>
  </div>
</div>
<div class="cap fade"><b>Pie Chart</b> — National dominance at a glance; the long tail represents early-era American dominance vs modern Kenyan/Ethiopian excellence. <b>Histogram</b> — Winning times cluster in the 125–160 min band. The right tail represents pre-1924 races when the distance wasn't standardized at 26.2 miles.</div>
<div class="ins fade" id="ins1"></div>

<!-- ═══ SECTION 3: LINE + SCATTER ═══ -->
<div class="sec fade"><div class="sec-n">3</div><div class="sec-info"><div class="st">Performance Trends <span class="cbadge">Chart 3 · 5</span></div><div class="ss">Line Chart — time over years · Scatter Plot — year vs time with regression</div></div><div class="sec-line"></div></div>
<div class="cg one fade">
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Winning Times Trend Over the Years <span class="cbadge">Line Chart</span></div><div class="cs">Amber = Men · Red = Women · Hover for exact time · Click to highlight</div></div>
    <div class="cb"><canvas id="lineChart" height="85"></canvas></div>
  </div>
</div>
<div class="cg one fade">
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Year vs Finishing Time — Scatter Plot <span class="cbadge">Scatter Plot</span></div><div class="cs">Polynomial regression lines · Each dot = one race · Hover for winner details</div></div>
    <div class="cb"><img class="img-chart" src="{scatter_img}" alt="Scatter Plot"/></div>
  </div>
</div>
<div class="cap fade"><b>Line Chart</b> — The steady decline reflects advances in training science, altitude preparation, nutrition, and carbon-fiber super-shoes. <b>Scatter + Regression</b> — Dashed polynomial trendlines show the long-term improvement trajectory separately for men and women.</div>
<div class="ins fade" id="ins2"></div>
<div class="fb fade"><div class="fb-i">💡</div><div class="fb-t">The infamous <b>Heartbreak Hill</b> (miles 20–21) is actually four hills in Newton, MA. Elite runners specifically train for this section — pacing strategy at mile 20 often decides the race. <b>Super-shoes</b> (Nike Vaporfly, Adidas Adizero) are estimated to save 2–4 minutes on marathon times.</div></div>

<!-- ═══ SECTION 4: BAR + COUNT PLOT ═══ -->
<div class="sec fade"><div class="sec-n">4</div><div class="sec-info"><div class="st">National & Era Breakdown <span class="cbadge">Chart 4 · 9</span></div><div class="ss">Bar Chart — country wins · Count Plot — winners per decade by gender</div></div><div class="sec-line"></div></div>
<div class="cg two fade">
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Top Countries by Wins <span class="cbadge">Bar Chart</span></div><div class="cs">Horizontal bars · Staggered animation · Hover for count</div></div>
    <div class="cb"><canvas id="barChart" height="200"></canvas></div>
  </div>
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Winners Per Decade <span class="cbadge">Count Plot</span></div><div class="cs">Men vs Women grouped · Click legend to toggle</div></div>
    <div class="cb"><img class="img-chart" src="{count_img}" alt="Count Plot"/></div>
  </div>
</div>
<div class="cap fade"><b>USA</b> dominated 1897–1960s; <b>Japan</b> surged mid-century; <b>Kenya & Ethiopia</b> dominate post-1990 through altitude training at 2,400m+ elevation. <b>Count Plot</b> — Women's field only appears from 1966 onward, expanding rapidly after 1972's official recognition.</div>
<div class="ins fade" id="ins3"></div>

<!-- ═══ SECTION 5: AREA + BOX PLOT ═══ -->
<div class="sec fade"><div class="sec-n">5</div><div class="sec-info"><div class="st">Cumulative Trends & Distribution <span class="cbadge">Chart 8 · 6</span></div><div class="ss">Area Chart — cumulative wins over time · Box Plot — spread and outliers by gender</div></div><div class="sec-line"></div></div>
<div class="cg two fade">
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Cumulative Wins Over Time <span class="cbadge">Area Chart</span></div><div class="cs">Filled area showing total wins accumulated · Amber = Men · Red = Women</div></div>
    <div class="cb"><img class="img-chart" src="{area_img}" alt="Area Chart"/></div>
  </div>
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Time Distribution by Gender <span class="cbadge">Box Plot</span></div><div class="cs">IQR boxes · Median line · Outliers as dots · Hover for stats</div></div>
    <div class="cb"><img class="img-chart" src="{box_img}" alt="Box Plot"/></div>
  </div>
</div>
<div class="cap fade"><b>Area Chart</b> — Men's cumulative curve starts 1897; Women's from 1966. The steeper recent slope of both lines reflects the race's growing prestige. <b>Box Plot</b> — Outliers (dots beyond whiskers) are typically pre-1924 races with non-standard distances. IQR shows how tightly modern winners cluster.</div>

<!-- ═══ SECTION 6: HEATMAP + VIOLIN ═══ -->
<div class="sec fade"><div class="sec-n">6</div><div class="sec-info"><div class="st">Statistical Analysis <span class="cbadge">Chart 7 · 10</span></div><div class="ss">Heatmap — feature correlations · Violin Plot — full density distribution</div></div><div class="sec-line"></div></div>
<div class="cg two fade">
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Feature Correlation Matrix <span class="cbadge">Heatmap</span></div><div class="cs">Lower triangle · Warm = positive · Cool = negative correlation</div></div>
    <div class="cb"><img class="img-chart" src="{heat_img}" alt="Heatmap"/></div>
  </div>
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Time Distribution Density <span class="cbadge">Violin Plot</span></div><div class="cs">Width = density at that time · Inner quartile lines shown</div></div>
    <div class="cb"><img class="img-chart" src="{violin_img}" alt="Violin Plot"/></div>
  </div>
</div>
<div class="cap fade"><b>Heatmap</b> — Strong negative Year↔Time correlation: as years increase, times decrease. Speed and Pace/Mile are perfectly inverse by definition. <b>Violin Plot</b> — Women's distribution is wider (more variance) reflecting the shorter competitive history; men's violin is tighter showing deeper field depth.</div>
<div class="ins fade" id="ins4"></div>
<div class="fb fade"><div class="fb-i">🧠</div><div class="fb-t"><b>Statistical note:</b> The correlation heatmap reveals Year vs Time (r ≈ −0.8) is the strongest signal — a clean story of continuous improvement. Distance columns show near-zero variance (most races = 26.2 mi post-1924), making them less informative for recent-era analysis.</div></div>

<!-- ═══ SECTION 7: BUBBLE + FUNNEL (BONUS) ═══ -->
<div class="sec fade"><div class="sec-n">7</div><div class="sec-info"><div class="st">Advanced Visualizations <span class="cbadge">Bonus Charts</span></div><div class="ss">Bubble Chart — 3D analysis · Funnel Chart — performance tier brackets</div></div><div class="sec-line"></div></div>
<div class="cg two fade">
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Year · Time · Speed — Bubble Chart <span class="cbadge">Bubble Chart</span></div><div class="cs">Bubble size = Speed · Amber = Men · Red = Women · Hover for details</div></div>
    <div class="cb"><canvas id="bubbleChart" height="200"></canvas></div>
  </div>
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Performance Tier Brackets <span class="cbadge">Funnel Chart</span></div><div class="cs">Winners grouped by finishing time bracket · Top tier = elite sub-2:10</div></div>
    <div class="cb"><canvas id="funnelChart" height="200"></canvas></div>
  </div>
</div>
<div class="cap fade"><b>Bubble Chart</b> — Three variables simultaneously: Year (x), Time (y), Speed (bubble size). Larger = faster. Post-2000 cluster shows the era of super-shoes and elite pacing. <b>Funnel/Bracket Chart</b> — Most winners sit in 2:10–2:50. Sub-2:10 performances are extremely rare world-class feats.</div>
<div class="ins fade" id="ins5"></div>
<div class="fb fade"><div class="fb-i">📌</div><div class="fb-t">Boston is the only World Marathon Major with a <b>qualifying standard</b> — sub-3:00 (men), sub-3:30 (women). Prize money: <b>$150,000</b> for the winner. The Bubble Chart shows clearly how the fastest modern races cluster in a region unreachable by pre-1970 runners regardless of effort.</div></div>

<!-- ═══ SECTION 8: PAIR PLOT (BONUS) ═══ -->
<div class="sec fade"><div class="sec-n">8</div><div class="sec-info"><div class="st">Multi-Feature Pair Analysis <span class="cbadge">Pair Plot</span></div><div class="ss">Relationship matrix — every numeric feature vs every other</div></div><div class="sec-line"></div></div>
<div class="cg one fade">
  <div class="cc" onclick="rpl(event,this)">
    <div class="ch"><div class="ct">Pair Plot — Multi-Feature Correlations <span class="cbadge">Pair Plot</span></div><div class="cs">Diagonal = KDE distribution · Off-diagonal = scatter by gender · Amber = Men · Red = Women</div></div>
    <div class="cb"><img class="img-chart" src="{pair_img}" alt="Pair Plot"/></div>
  </div>
</div>
<div class="cap fade"><b>Pair Plot</b> — The Year↔Time diagonal trend is the clearest signal across all panels. Speed↔Time shows a near-perfect inverse relationship. The gender separation is most visible in the Time axis — men and women occupy distinct but converging bands over decades.</div>

<!-- ═══ SECTION 9: DATA TABLE ═══ -->
<div class="sec fade"><div class="sec-n">9</div><div class="sec-info"><div class="st">Data Explorer</div><div class="ss">Browse the filtered dataset — showing top 30 records</div></div><div class="sec-line"></div></div>
<div style="padding:0 36px 24px;position:relative;z-index:1;" class="fade">
  <div style="background:var(--bg2);border:1px solid var(--b);border-radius:14px;overflow:auto;max-height:380px;">
    <table class="dtable" id="dtable"></table>
  </div>
</div>

<!-- ═══ FOOTER ═══ -->
<div class="footer fade">
  <p>
    <b>Boston Marathon</b> Elite Analytics Dashboard &nbsp;·&nbsp; Exploratory Data Analysis Course<br>
    <b>Streamlit</b> · <b>Pandas</b> · <b>Matplotlib</b> · <b>Seaborn</b> · <b>Chart.js</b> · <b>NumPy</b><br>
    Data: <b>1897–2022</b> · 10 Required Charts + 3 Bonus · All filters connected to all visualizations<br>
    Patriots Day · Hopkinton → Boylston Street · 26.2 miles
  </p>
</div>

<script>
const D={js_data};
const S=D.stats;

// ── utils ──────────────────────────────────────────────────────────────────
function hms(m){{const h=Math.floor(m/60),mi=Math.floor(m%60),s=Math.round((m%1)*60);return `${{h}}:${{String(mi).padStart(2,'0')}}:${{String(s).padStart(2,'0')}}`;}}
function ha(m){{const h=Math.floor(m/60),mi=Math.floor(m%60);return `${{h}}h ${{String(mi).padStart(2,'0')}}m`;}}

// ── particles ──────────────────────────────────────────────────────────────
(function(){{
  const c=document.getElementById('pc'),ctx=c.getContext('2d');
  let W,H,pts=[];
  function sz(){{W=c.width=window.innerWidth;H=c.height=Math.max(document.body.scrollHeight,window.innerHeight);}}
  sz();window.addEventListener('resize',()=>{{sz();init();}});
  function init(){{pts=[];const n=Math.min(50,Math.floor(W*H/30000));for(let i=0;i<n;i++)pts.push({{x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.25,vy:(Math.random()-.5)*.25,r:Math.random()*1.4+.3,a:Math.random()*.3+.06}});}}
  init();
  function draw(){{
    ctx.clearRect(0,0,W,H);
    pts.forEach(p=>{{p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>W)p.vx*=-1;if(p.y<0||p.y>H)p.vy*=-1;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle=`rgba(232,147,58,${{p.a}})`;ctx.fill();}});
    for(let i=0;i<pts.length;i++)for(let j=i+1;j<pts.length;j++){{const dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y,d=Math.sqrt(dx*dx+dy*dy);if(d<110){{ctx.beginPath();ctx.moveTo(pts[i].x,pts[i].y);ctx.lineTo(pts[j].x,pts[j].y);ctx.strokeStyle=`rgba(232,147,58,${{(1-d/110)*.07}})`;ctx.lineWidth=.5;ctx.stroke();}}}}
    requestAnimationFrame(draw);
  }}
  draw();
  // resize canvas when content changes height
  const ro=new ResizeObserver(()=>sz());ro.observe(document.body);
}})();

// ── count-up ───────────────────────────────────────────────────────────────
function cu(el,v,dur=1100){{const s=performance.now(),f=v%1!==0;(function step(n){{const p=Math.min((n-s)/dur,1),e=1-Math.pow(1-p,3),val=f?(e*v).toFixed(2):Math.round(e*v);el.textContent=val;if(p<1)requestAnimationFrame(step);}}) (performance.now());}}

// ── Fill KPIs ──────────────────────────────────────────────────────────────
document.getElementById('k1').textContent=S.fastHMS;
document.getElementById('k1s').textContent=S.fastName+' · '+S.fastYear;
document.getElementById('k2').textContent=hms(S.avgTime);
document.getElementById('k3').textContent=S.avgSpeed.toFixed(2);
document.getElementById('k6').textContent=S.yrMin+'–'+S.yrMax;
cu(document.getElementById('k4'),S.countries);
cu(document.getElementById('k5'),S.uniqueWinners);

// ── Hall of Fame ───────────────────────────────────────────────────────────
const medals=['🥇','🥈','🥉','🏅','🏅'],ranks=['1ST','2ND','3RD','4TH','5TH'];
const hg=document.getElementById('hof');
D.hof.forEach((h,i)=>{{hg.innerHTML+=`<div class="hc"><div class="hc-rk">${{ranks[i]}}</div><div class="hc-med">${{medals[i]}}</div><div class="hc-nm">${{h.name}}</div><div class="hc-co">${{h.country}}</div><div class="hc-w">${{h.wins}}</div><div class="hc-wl">Wins</div><div class="hc-yr">${{h.first}}–${{h.last}}</div></div>`;}});

// ── Insight helper ─────────────────────────────────────────────────────────
function ins(id,cards){{const el=document.getElementById(id);if(!el)return;el.innerHTML=cards.map(c=>`<div class="ic"><div class="ic-l">${{c.l}}</div><div class="ic-v">${{c.v}}</div><div class="ic-d">${{c.d}}</div></div>`).join('');}}

const topC=D.countryLabels[0]||'N/A',topN=D.countryVals[0]||0;
const topPct=S.total>0?(topN/S.total*100).toFixed(1):0;

ins('ins1',[
  {{l:'Dominant Nation',v:topC,d:`Won <b>${{topN}}</b> races — <b>${{topPct}}%</b> of filtered records. <b>${{S.countries}}</b> nations have claimed the Boston finish line.`}},
  {{l:'Most Common Time',v:'~'+Math.round(S.medTime)+' min',d:`Median of <b>${{ha(S.medTime)}}</b>. Elite times cluster tightly — σ = <b>${{S.stdT}} min</b>, showing deep competitive field.`}},
  {{l:'Records in View',v:S.total,d:`<b>${{S.total}}</b> results across <b>${{S.yrMax-S.yrMin}}</b> years, <b>${{S.menCount}}</b> men's and <b>${{S.womenCount}}</b> women's races.`}},
]);
ins('ins2',[
  {{l:'Course Record',v:S.fastHMS,d:`Set by <b>${{S.fastName}}</b> in <b>${{S.fastYear}}</b>. Marathon records keep falling as training science and shoe tech advance.`}},
  {{l:'Total Improvement',v:S.improvement.toFixed(1)+' min',d:`Times improved by <b>${{S.improvement.toFixed(1)}} min</b> from slowest to fastest — a testament to 127 years of athletic evolution.`}},
  {{l:'Avg Speed',v:S.avgSpeed.toFixed(2)+' mph',d:`Winners average <b>${{S.avgSpeed.toFixed(2)}} mph</b> over 26.2 miles — roughly <b>${{ha(S.avgTime)}}</b> of relentless non-stop effort.`}},
]);
ins('ins3',[
  {{l:'Top 3 Nations',v:'',d:`<b>${{(D.countryLabels.slice(0,3)||[]).join(' · ')}}</b> lead all nations. These countries shaped every era of Boston history.`}},
  {{l:'Gender Split',v:S.menCount+' / '+S.womenCount,d:`<b>${{S.menCount}}</b> men's · <b>${{S.womenCount}}</b> women's records. Women officially included since <b>1972</b>.`}},
  {{l:'Unique Champions',v:S.uniqueWinners,d:`<b>${{S.uniqueWinners}}</b> athletes across filtered records. <b>Clarence DeMar</b> leads all-time with 7 wins.`}},
]);
ins('ins4',[
  {{l:'Gender Gap',v:S.maleAvg&&S.femaleAvg?(S.femaleAvg-S.maleAvg).toFixed(1)+' min':'N/A',d:S.maleAvg&&S.femaleAvg?`Men avg <b>${{S.maleAvg}} min</b>, Women avg <b>${{S.femaleAvg}} min</b> — gap narrowing since the 1970s as women's athletics matured.`:'Select All gender to see the gap.'}},
  {{l:'Std Deviation',v:S.stdT+' min',d:`σ = <b>${{S.stdT}} min</b>. Lower σ in recent decades proves the field is getting simultaneously deeper and faster.`}},
  {{l:'Median Time',v:ha(S.medTime),d:`Median of <b>${{ha(S.medTime)}}</b> vs mean <b>${{ha(S.avgTime)}}</b>. The skew comes from early-era slower races in the right tail.`}},
]);
ins('ins5',[
  {{l:'Avg Pace / Mile',v:S.avgPace+' min/mi',d:`Winners run each mile in <b>${{Math.floor(S.avgPace)}}:${{String(Math.round((S.avgPace%1)*60)).padStart(2,'0')}}</b>. Sustained over 26.2 miles — superhuman consistency.`}},
  {{l:'Top Speed',v:S.topSpeedVal+' mph',d:`<b>${{S.topSpeedName}}</b> holds the highest recorded speed at <b>${{S.topSpeedVal}} mph</b> in this filter.`}},
  {{l:'Sub-2:10 Races',v:D.funnelVals[0]||0,d:`Only <b>${{D.funnelVals[0]||0}}</b> races in the sub-2:10 tier — the most exclusive bracket in marathon running.`}},
]);

// ── Ripple on click ────────────────────────────────────────────────────────
function rpl(e,el){{const r=el.getBoundingClientRect();el.style.setProperty('--rx',(e.clientX-r.left)+'px');el.style.setProperty('--ry',(e.clientY-r.top)+'px');el.classList.remove('rpl');void el.offsetWidth;el.classList.add('rpl');setTimeout(()=>el.classList.remove('rpl'),650);}}

// ── Chart.js defaults ──────────────────────────────────────────────────────
Chart.defaults.color='#7a7468';
Chart.defaults.borderColor='rgba(232,147,58,0.07)';
Chart.defaults.font.family="'Inter','Arial',sans-serif";

const TT=document.getElementById('tt'),TTT=document.getElementById('tt-t'),TTB=document.getElementById('tt-b');
document.addEventListener('mousemove',e=>{{if(TT.style.display==='block'){{TT.style.left=(e.clientX+14)+'px';TT.style.top=(e.clientY-10)+'px';}}}});

// ─ 1. Pie Chart ────────────────────────────────────────────────────────────
(function(){{
  const ctx=document.getElementById('pieChart').getContext('2d');
  const clrs=['#e8933a','#e07830','#d4a850','#c88040','#b07038','#a85830','#c47520','#f0a852'];
  new Chart(ctx,{{type:'doughnut',
    data:{{labels:D.pieLabels,datasets:[{{data:D.pieVals,backgroundColor:clrs.slice(0,D.pieVals.length),borderColor:'#07070a',borderWidth:3,hoverOffset:8}}]}},
    options:{{responsive:true,maintainAspectRatio:false,cutout:'62%',
      animation:{{duration:1100,easing:'easeOutQuart'}},
      plugins:{{legend:{{position:'right',labels:{{color:'#7a7468',boxWidth:10,font:{{size:10}}}}}},
        tooltip:{{backgroundColor:'rgba(10,9,14,0.95)',borderColor:'rgba(232,147,58,0.2)',borderWidth:1,titleColor:'#e8933a',bodyColor:'#c8c0b0',callbacks:{{label:c=>` ${{c.label}}: ${{c.parsed}} wins (${{(c.parsed/S.total*100).toFixed(1)}}%)`}}}}}}
    }}
  }});
}})();

// ─ 2. Histogram ───────────────────────────────────────────────────────────
(function(){{
  const ctx=document.getElementById('histChart').getContext('2d');
  new Chart(ctx,{{type:'bar',
    data:{{labels:D.histBins.map(b=>Math.floor(b.x/60)+'h'+String(Math.round(b.x%60)).padStart(2,'0')+'m'),
      datasets:[{{label:'Winners',data:D.histBins.map(b=>b.y),
        backgroundColor:D.histBins.map((_,i)=>{{const t=i/D.histBins.length;return `rgba(${{Math.round(232-t*40)}},${{Math.round(147-t*60)}},${{Math.round(58+t*20)}},0.8)`;}}),
        borderColor:'transparent',borderRadius:4}}]}},
    options:{{responsive:true,maintainAspectRatio:false,
      animation:{{duration:900,easing:'easeOutBounce'}},
      plugins:{{legend:{{display:false}},tooltip:{{backgroundColor:'rgba(10,9,14,0.95)',borderColor:'rgba(232,147,58,0.2)',borderWidth:1,titleColor:'#e8933a',bodyColor:'#c8c0b0',callbacks:{{label:c=>` ${{c.parsed.y}} winners`}}}}}},
      scales:{{x:{{ticks:{{color:'#4a4540',maxRotation:45,font:{{size:8}}}},grid:{{display:false}}}},y:{{ticks:{{color:'#4a4540'}},grid:{{color:'rgba(232,147,58,0.05)'}}}}}}
    }}
  }});
}})();

// ─ 3. Line Chart ──────────────────────────────────────────────────────────
(function(){{
  const ctx=document.getElementById('lineChart').getContext('2d');
  new Chart(ctx,{{type:'line',
    data:{{datasets:[
      {{label:'Men',data:D.menTimes.map((t,i)=>{{return {{x:D.menYears[i],y:t}}}}),borderColor:'#e8933a',backgroundColor:'rgba(232,147,58,0.06)',borderWidth:2,pointRadius:1.5,pointHoverRadius:5,pointBackgroundColor:'#e8933a',tension:0.35,fill:true}},
      {{label:'Women',data:D.womenTimes.map((t,i)=>{{return {{x:D.womenYears[i],y:t}}}}),borderColor:'#e86850',backgroundColor:'rgba(232,104,80,0.05)',borderWidth:2,pointRadius:1.5,pointHoverRadius:5,pointBackgroundColor:'#e86850',tension:0.35,fill:true}},
    ]}},
    options:{{responsive:true,maintainAspectRatio:true,
      interaction:{{mode:'index',intersect:false}},
      animation:{{duration:1200,easing:'easeOutQuart'}},
      plugins:{{legend:{{labels:{{color:'#7a7468',boxWidth:10,font:{{size:11}}}}}},
        tooltip:{{backgroundColor:'rgba(10,9,14,0.95)',borderColor:'rgba(232,147,58,0.2)',borderWidth:1,titleColor:'#e8933a',bodyColor:'#c8c0b0',callbacks:{{label:c=>' '+c.dataset.label+': '+hms(c.parsed.y)}}}}}},
      scales:{{
        x:{{type:'linear',title:{{display:true,text:'Year',color:'#4a4540'}},ticks:{{color:'#4a4540',maxTicksLimit:12}},grid:{{color:'rgba(232,147,58,0.05)'}}}},
        y:{{title:{{display:true,text:'Time (min)',color:'#4a4540'}},ticks:{{color:'#4a4540',callback:v=>Math.floor(v/60)+'h'+String(Math.floor(v%60)).padStart(2,'0')+'m'}},grid:{{color:'rgba(232,147,58,0.05)'}}}}
      }}
    }}
  }});
}})();

// ─ 4. Bar Chart (countries) ───────────────────────────────────────────────
(function(){{
  const ctx=document.getElementById('barChart').getContext('2d');
  const n=D.countryLabels.length;
  new Chart(ctx,{{type:'bar',
    data:{{labels:D.countryLabels,datasets:[{{label:'Wins',data:D.countryVals,
      backgroundColor:D.countryVals.map((_,i)=>{{const t=i/n;return `rgba(${{Math.round(232-t*80)}},${{Math.round(147-t*80)}},${{Math.round(58+t*30)}},0.85)`;}}),
      borderColor:'transparent',borderRadius:6}}]}},
    options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      animation:{{duration:1000,delay:ctx=>ctx.dataIndex*70}},
      plugins:{{legend:{{display:false}},tooltip:{{backgroundColor:'rgba(10,9,14,0.95)',borderColor:'rgba(232,147,58,0.2)',borderWidth:1,titleColor:'#e8933a',bodyColor:'#c8c0b0',callbacks:{{label:c=>' '+c.parsed.x+' wins'}}}}}},
      scales:{{x:{{ticks:{{color:'#4a4540'}},grid:{{color:'rgba(232,147,58,0.05)'}}}},y:{{ticks:{{color:'#c8c0b0',font:{{size:11,weight:'600'}}}},grid:{{display:false}}}}}}
    }}
  }});
}})();

// ─ 5. Bubble Chart ────────────────────────────────────────────────────────
(function(){{
  const ctx=document.getElementById('bubbleChart').getContext('2d');
  const men=D.scatter.filter(d=>d.g==='Male').map(d=>{{return {{x:d.x,y:d.y,r:Math.max(3,Math.min(13,(d.s-9)*2.8)),_d:d}}}});
  const women=D.scatter.filter(d=>d.g==='Female').map(d=>{{return {{x:d.x,y:d.y,r:Math.max(3,Math.min(13,(d.s-9)*2.8)),_d:d}}}});
  new Chart(ctx,{{type:'bubble',
    data:{{datasets:[
      {{label:'Men',data:men,backgroundColor:'rgba(232,147,58,0.4)',borderColor:'rgba(232,147,58,0.7)',borderWidth:1}},
      {{label:'Women',data:women,backgroundColor:'rgba(232,104,80,0.4)',borderColor:'rgba(232,104,80,0.7)',borderWidth:1}},
    ]}},
    options:{{responsive:true,maintainAspectRatio:false,
      animation:{{duration:1200,easing:'easeOutElastic'}},
      plugins:{{legend:{{labels:{{color:'#7a7468',boxWidth:10,font:{{size:11}}}}}},
        tooltip:{{backgroundColor:'rgba(10,9,14,0.95)',borderColor:'rgba(232,147,58,0.2)',borderWidth:1,titleColor:'#e8933a',bodyColor:'#c8c0b0',
          callbacks:{{title:i=>i[0].raw._d.w+' ('+i[0].raw._d.x+')',label:i=>' Time: '+hms(i.raw.y)+' · Speed: '+i.raw._d.s+' mph'}}}}}},
      scales:{{
        x:{{title:{{display:true,text:'Year',color:'#4a4540'}},ticks:{{color:'#4a4540'}},grid:{{color:'rgba(232,147,58,0.05)'}}}},
        y:{{title:{{display:true,text:'Time (min)',color:'#4a4540'}},ticks:{{color:'#4a4540',callback:v=>Math.floor(v/60)+'h'+String(Math.floor(v%60)).padStart(2,'0')+'m'}},grid:{{color:'rgba(232,147,58,0.05)'}}}}
      }}
    }}
  }});
}})();

// ─ 6. Funnel Chart ────────────────────────────────────────────────────────
(function(){{
  const ctx=document.getElementById('funnelChart').getContext('2d');
  const clrs=['#c47520','#e8933a','#e07830','#c88040','#b07038','#a85830','#8a5028'];
  new Chart(ctx,{{type:'bar',
    data:{{labels:D.funnelLabels,
      datasets:[{{label:'Winners',data:D.funnelVals,
        backgroundColor:D.funnelVals.map((_,i)=>clrs[i%clrs.length]),
        borderColor:'transparent',borderRadius:6}}]}},
    options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      animation:{{duration:1000,easing:'easeOutQuart',delay:ctx=>ctx.dataIndex*100}},
      plugins:{{legend:{{display:false}},tooltip:{{backgroundColor:'rgba(10,9,14,0.95)',borderColor:'rgba(232,147,58,0.2)',borderWidth:1,titleColor:'#e8933a',bodyColor:'#c8c0b0',callbacks:{{label:c=>' '+c.parsed.x+' winners'}}}}}},
      scales:{{
        x:{{ticks:{{color:'#4a4540'}},grid:{{color:'rgba(232,147,58,0.05)'}}}},
        y:{{ticks:{{color:'#c8c0b0',font:{{size:11}}}},grid:{{display:false}}}}
      }}
    }}
  }});
}})();

// ── Data table ─────────────────────────────────────────────────────────────
(function(){{
  const cols=['Year','Winner','Country','Gender','Time','Speed','Pace'];
  const dataRows=D.scatter.sort((a,b)=>b.x-a.x).slice(0,30);
  const tbl=document.getElementById('dtable');
  tbl.innerHTML='<thead><tr>'+cols.map(c=>`<th>${{c}}</th>`).join('')+'</tr></thead>';
  const tb=document.createElement('tbody');
  dataRows.forEach(r=>{{
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${{r.x}}</td><td style="color:var(--tl);font-weight:600">${{r.w}}</td><td>${{r.g==='Male'?'🇰🇪':'🌍'}} ${{r._country||''}}</td><td style="color:${{r.g==='Male'?'#e8933a':'#e86850'}}">${{r.g}}</td><td>${{hms(r.y)}}</td><td>${{r.s}} mph</td><td>–</td>`;
    tb.appendChild(tr);
  }});
  tbl.appendChild(tb);
}})();

// ── Scroll-triggered fade-in ───────────────────────────────────────────────
(function(){{
  const obs=new IntersectionObserver(entries=>{{entries.forEach(e=>{{if(e.isIntersecting)e.target.classList.add('in');}});}},{{threshold:0.06}});
  document.querySelectorAll('.fade').forEach(el=>obs.observe(el));
}})();
</script>
</body></html>"""

# ── Render component with scrolling=True and auto height ─────────────────────
components.html(html, height=7200, scrolling=True)

# ── Download buttons below the component ─────────────────────────────────────
st.markdown("---")
_edf = filtered_df[[c for c in ["Year","Winner","Country","Gender","Time","Time_Minutes",
    "Speed_MPH","Pace_Per_Mile","Distance (Miles)","Distance (KM)","Decade_Label"]
    if c in filtered_df.columns]].reset_index(drop=True)
_buf = io.StringIO(); _edf.to_csv(_buf, index=False); _cb = _buf.getvalue().encode()
ex1,ex2,ex3 = st.columns(3)
with ex1: st.download_button("⬇️ Download Filtered CSV",_cb,f"boston_{len(_edf)}.csv","text/csv",use_container_width=True)
with ex2: st.download_button("⬇️ Men's Full Dataset",open("data/Mens_Boston_Marathon_Winners_r0l7bV.csv","rb").read(),"boston_mens.csv","text/csv",use_container_width=True)
with ex3: st.download_button("⬇️ Women's Full Dataset",open("data/Womens_Boston_Marathon_Winners_8SSnWb.csv","rb").read(),"boston_womens.csv","text/csv",use_container_width=True)
