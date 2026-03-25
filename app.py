import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMapWithTime
import os

st.set_page_config(page_title="SOFIE | Strategic Engine", layout="wide")

# --- 1. LOAD DATA ---
@st.cache_data
def load_full_data():
    path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\master\master.parquet"
    df = pd.read_parquet(path)
    # Ensure index is datetime for the timeline
    df.index = pd.to_datetime(df.index)
    return df

df = load_full_data()

# --- 2. SIDEBAR CONTROLS ---
st.sidebar.title("🎮 Simulation Room")
oil_price = st.sidebar.slider("Future Oil Price Target ($/bbl)", 70, 300, 100)
speed = st.sidebar.select_slider("Playback Speed", options=["Slow", "Normal", "Fast"], value="Normal")

# --- 3. COORDINATE MAPPING (Your ACLED Regions) ---
region_map = {
    'acled_africa_FATALITIES': [1.0, 17.0],
    'acled_middle_east_FATALITIES': [29.0, 43.0],
    'acled_asia_pacific_FATALITIES': [15.0, 120.0],
    'acled_europe_central_asia_FATALITIES': [48.0, 18.0],
    'acled_latin_america_the_caribbean_FATALITIES': [-15.0, -60.0]
}

# --- 4. DATA PREPARATION (Temporal) ---
df_monthly = df.resample('ME').mean(numeric_only=True)
time_index = [d.strftime('%Y-%m') for d in df_monthly.index]

master_heat_data = []

for index, row in df_monthly.iterrows():
    step_data = []
    
    # Projection logic for 2024+
    is_future = index.year >= 2024
    multiplier = (oil_price / 80) ** 1.5 if is_future else 1.0
    
    for col, coords in region_map.items():
        if col in row:
            val = row[col]
            # Clean the data: skip NaNs or zeros
            if pd.notna(val) and val > 0:
                weight = float(np.log1p(val * multiplier))
                step_data.append([coords[0], coords[1], weight])
    
    # 🚨 THE FIX: If step_data is empty, add a "Ghost Point" 
    # This prevents the IndexError by ensuring the list is never empty
    if not step_data:
        step_data.append([0.0, 0.0, 0.0])
        
    master_heat_data.append(step_data)

# --- 5. RENDER ---
m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB dark_matter')

# Add a check to ensure we actually have data before calling the plugin
if master_heat_data:
    HeatMapWithTime(
        data=master_heat_data,
        index=time_index,
        auto_play=False,
        max_opacity=0.7,
        radius=25, # Slightly smaller for cleaner look
        use_local_extrema=False # Set to False for consistent global scaling
    ).add_to(m)

st_folium(m, width=1200, height=650, key="sofie_timeline_map")

# --- 6. MACRO METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Timeline Scope", "1980 - 2030")
with col2:
    st.metric("Total Indicators Analyzed", "1,280")
with col3:
    st.metric("Scenario Status", "PROJECTED" if oil_price > 120 else "HISTORICAL")

st.write("### 💡 How to use")
st.write("1. Press the **Play** button on the map (bottom left).")
st.write("2. Watch the 'Glow' move from the Cold War era into the 2020s.")
st.write("3. Adjust the **Oil Price** in the sidebar to see how the 'Projection' phase (2024+) expands.")
