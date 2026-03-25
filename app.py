import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="SOFIE | Strategic Engine", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\master\master.parquet"
    df = pd.read_parquet(path)
    # Ensure index is datetime if possible
    return df

try:
    df = load_data()
    st.sidebar.success("✅ Master Dataset Loaded")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.title("🛠️ Scenario Controls")
oil_price = st.sidebar.slider("Global Oil Price ($/bbl)", 70, 250, 100)
tension_multiplier = (oil_price / 80) ** 2  # Exponential risk scaling

# --- COORDINATE MAPPING ---
region_coords = {
    'Africa': [1.0, 17.0, 'acled_africa_FATALITIES'],
    'Middle East': [29.0, 43.0, 'acled_middle_east_FATALITIES'],
    'Asia Pacific': [15.0, 120.0, 'acled_asia_pacific_FATALITIES'],
    'Europe': [48.0, 18.0, 'acled_europe_central_asia_FATALITIES'],
    'Latin America': [-15.0, -60.0, 'acled_latin_america_the_caribbean_FATALITIES']
}

# --- MAIN DASHBOARD ---
st.title("🛰️ SOFIE: Global Tension Nexus")
st.subheader(f"Scenario: Oil at ${oil_price} | Conflict Multiplier: {tension_multiplier:.2f}x")

col1, col2 = st.columns([3, 1])

with col1:
    # 1. Prepare Heatmap Data
    heat_data = []
    for region, details in region_coords.items():
        lat, lon, col = details
        if col in df.columns:
            # Baseline fatalities * our oil-driven multiplier
            base_val = df[col].mean()
            current_tension = base_val * tension_multiplier
            heat_data.append([lat, lon, current_tension])

    # 2. Render Map
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB dark_matter')
    HeatMap(heat_data, radius=35, blur=20, min_opacity=0.3).add_to(m)
    
    st_folium(m, width=1000, height=600)

with col2:
    st.metric("Total Conflict Vectors", len(region_coords))
    st.metric("Risk Level", "CRITICAL" if oil_price > 180 else "STABLE")
    
    st.write("### Regional Impact")
    for region, details in region_coords.items():
        st.write(f"**{region}:** Increase")
        st.progress(min(tension_multiplier / 10, 1.0))

# --- RAW DATA PREVIEW ---
with st.expander("View Master Feature Metadata"):
    st.dataframe(df.head(10))
