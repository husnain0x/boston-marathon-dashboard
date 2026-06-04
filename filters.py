"""
filters.py — Filter / data processing functions for Boston Marathon Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np


def load_and_merge_data():
    """Load both CSVs, merge with Gender column, and clean data."""
    mens = pd.read_csv("data/Mens_Boston_Marathon_Winners_r0l7bV.csv")
    womens = pd.read_csv("data/Womens_Boston_Marathon_Winners_8SSnWb.csv")

    mens["Gender"] = "Male"
    womens["Gender"] = "Female"

    df = pd.concat([mens, womens], ignore_index=True)

    # Parse time to total minutes
    def time_to_minutes(t):
        try:
            parts = str(t).split(":")
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 60 + int(m) + int(s) / 60
            elif len(parts) == 2:
                m, s = parts
                return int(m) + int(s) / 60
        except:
            return np.nan
        return np.nan

    df["Time_Minutes"] = df["Time"].apply(time_to_minutes)

    # Parse time to seconds for more precision
    def time_to_seconds(t):
        try:
            parts = str(t).split(":")
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + int(s)
            elif len(parts) == 2:
                m, s = parts
                return int(m) * 60 + int(s)
        except:
            return np.nan
        return np.nan

    df["Time_Seconds"] = df["Time"].apply(time_to_seconds)

    # Create decade column
    df["Decade"] = (df["Year"] // 10) * 10
    df["Decade_Label"] = df["Decade"].astype(str) + "s"

    # Calculate pace (min/mile)
    df["Pace_Per_Mile"] = df["Time_Minutes"] / df["Distance (Miles)"]

    # Calculate pace (min/km)
    df["Pace_Per_KM"] = df["Time_Minutes"] / df["Distance (KM)"]

    # Speed (mph)
    df["Speed_MPH"] = df["Distance (Miles)"] / (df["Time_Minutes"] / 60)

    # Sort by year
    df = df.sort_values("Year").reset_index(drop=True)

    return df


def apply_filters(df):
    """Render sidebar filters and return filtered dataframe."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Filters")

    # ---- Reset Button ----
    # Delete the widget keys so they fall back to their defaults on rerun.
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        for k in ["year_range", "gender_filter", "time_range",
                  "country_filter", "search_filter"]:
            st.session_state.pop(k, None)
        st.rerun()

    # ---- 1. Date/Year Range Filter ----
    st.sidebar.markdown("#### 📅 Year Range")
    year_min = int(df["Year"].min())
    year_max = int(df["Year"].max())
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
        key="year_range",
    )

    # ---- 2. Category Filter (Gender) ----
    st.sidebar.markdown("#### 👤 Gender")
    gender_options = df["Gender"].unique().tolist()
    selected_gender = st.sidebar.selectbox(
        "Select Gender", ["All"] + gender_options, key="gender_filter"
    )

    # ---- 3. Numerical Range Slider (Time in Minutes) ----
    st.sidebar.markdown("#### ⏱️ Finishing Time (Minutes)")
    time_min = float(df["Time_Minutes"].min())
    time_max = float(df["Time_Minutes"].max())
    time_range = st.sidebar.slider(
        "Select Time Range",
        min_value=time_min,
        max_value=time_max,
        value=(time_min, time_max),
        step=1.0,
        key="time_range",
    )

    # ---- 4. Multi-Select Filter (Country) ----
    st.sidebar.markdown("#### 🌍 Countries")
    countries = sorted([str(c) for c in df["Country"].unique().tolist()])
    selected_countries = st.sidebar.multiselect(
        "Select Countries (leave empty for all)",
        countries,
        default=[],
        key="country_filter",
    )

    # ---- 5. Search / Text Filter ----
    st.sidebar.markdown("#### 🔍 Search Winner")
    search_text = st.sidebar.text_input(
        "Search by winner name", "", key="search_filter"
    )

    # ---- Apply Filters ----
    filtered = df.copy()

    # Year range
    filtered = filtered[
        (filtered["Year"] >= year_range[0]) & (filtered["Year"] <= year_range[1])
    ]

    # Gender
    if selected_gender != "All":
        filtered = filtered[filtered["Gender"] == selected_gender]

    # Time range
    filtered = filtered[
        (filtered["Time_Minutes"] >= time_range[0])
        & (filtered["Time_Minutes"] <= time_range[1])
    ]

    # Countries
    if selected_countries:
        filtered = filtered[filtered["Country"].isin(selected_countries)]

    # Search
    if search_text:
        filtered = filtered[
            filtered["Winner"].str.contains(search_text, case=False, na=False)
        ]

    return filtered
