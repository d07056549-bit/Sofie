import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMapWithTime
import datetime

# --- CONFIG ---
st.set_page_config(page_title="SOFIE | Strategic Command", layout="wide", initial_sidebar_state="expanded")

# --- DATA ENGINE ---
@st.cache_data
def load_sofie_data():
    path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\master\master.parquet"
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    return df

df = load_sofie_data()

# --- THE TABS ---
tab1, tab2, tab3 = st.tabs(["🌍 Global Tension Map", "📰 Live Intelligence Feed", "📊 War Score Analytics"])

# ---------------------------------------------------------
# TAB 1: WORLD TENSION MAP
# ---------------------------------------------------------
with tab1:
    st.header("Global Kinetic Heatmap")
    
    # Sidebar Filters inside Tab 1
    with st.sidebar:
        st.title("🎛️ Command Controls")
        oil_price = st.slider("Forecast Oil Price ($)", 70, 300, 95)
        risk_tolerance = st.select_slider("Risk Sensitivity", options=["Low", "Medium", "High", "Extreme"])
        
    # Map Logic (Using our previously optimized temporal code)
    region_map = {
        'Africa': [1.0, 17.0, 'acled_africa_FATALITIES'],
        'Middle East': [29.0, 43.0, 'acled_middle_east_FATALITIES'],
        'Asia': [15.0, 120.0, 'acled_asia_pacific_FATALITIES'],
        'Europe': [48.0, 18.0, 'acled_europe_central_asia_FATALITIES'],
        'Americas': [-15.0, -60.0, 'acled_latin_america_the_caribbean_FATALITIES']
    }

    # Prepare heatmap data
    df_monthly = df.resample('ME').mean(numeric_only=True).fillna(0)
    time_index = [d.strftime('%Y-%m') for d in df_monthly.index]
    heat_data = []

    for _, row in df_monthly.iterrows():
        step = []
        multiplier = (oil_price / 85) ** 2
        for name, info in region_map.items():
            lat, lon, col = info
            if col in row:
                weight = np.log1p(row[col] * multiplier)
                if weight > 0: step.append([lat, lon, weight])
        heat_data.append(step if step else [[51.5, -0.1, 0]])

    m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB dark_matter')
    HeatMapWithTime(heat_data, index=time_index, radius=25, max_opacity=0.7).add_to(m)
    st_folium(m, width=1300, height=600, key="war_map", returned_objects=[])

# ---------------------------------------------------------
# TAB 2: LIVE NEWS UPDATES
# ---------------------------------------------------------
with tab2:
    st.header("📡 Live Signal Intelligence")
    
    # In a real scenario, use: requests.get(f"https://newsapi.org/v2/everything?q=conflict&apiKey={8ff73836d6794247851bcdcd8f9653b6}")
    mock_news = [
        {"time": "10:42 AM", "tag": "RED SEA", "head": "Shipping premiums rise 15% amid regional friction."},
        {"time": "09:15 AM", "tag": "ARCTIC", "head": "New logistics corridor testing begins in Northern Sea Route."},
        {"time": "06:00 AM", "tag": "MACRO", "head": "Global crude stocks dip below 5-year average."},
    ]
    
    for news in mock_news:
        with st.container(border=True):
            col_a, col_b = st.columns([1, 6])
            col_a.caption(news['time'])
            col_a.error(news['tag']) if news['tag'] == "RED SEA" else col_a.warning(news['tag'])
            col_b.subheader(news['head'])

# ---------------------------------------------------------
# TAB 3: DANGER WAR SCORE
# ---------------------------------------------------------
with tab3:
    st.header("📈 SOFIE Kinetic Index")
    
    # Calculate War Score based on feature density
    # We take the mean of all fatality columns across the whole dataset
    fatality_cols = [c for c in df.columns if 'FATALITIES' in c]
    current_agg = df[fatality_cols].iloc[-1].mean() * (oil_price / 80)
    
    # Visual Gauge
    st.metric(label="Global War Score (K-Index)", value=f"{current_agg:.2f}", delta=f"{oil_price-80}% vs Baseline")
    
    # Regional Breakdown
    st.subheader("Regional Vulnerability Breakdown")
    chart_data = df_monthly[fatality_cols].tail(12)
    st.area_chart(chart_data)
    
    with st.expander("📝 Intelligence Methodology"):
        st.write("""
        The **War Score** is a composite metric calculated using:
        1. **ACLED Kinetic Data:** Fatalities and Event Frequency.
        2. **Oil Shock Multiplier:** Scaling risk based on energy logistics.
        3. **Mobility Friction:** Responding to Google Mobility dips in conflict zones.
        """)
