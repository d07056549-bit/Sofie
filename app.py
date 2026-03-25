import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMapWithTime
import streamlit.components.v1 as components
import requests

# --- 1. CONFIG & SETTINGS ---
st.set_page_config(page_title="SOFIE | Strategic Command", layout="wide")

# --- 2. DATA ENGINE ---
@st.cache_data
def load_data():
    # Replace with your actual path if different
    path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\master\master.parquet"
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    return df

df = load_data()
all_cols = df.columns.tolist()

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.title("🎛️ Command Controls")
oil_price = st.sidebar.slider("Forecast Oil Price ($)", 70, 300, 100)
# Multiplier: 1.0 at $80, grows as price rises
risk_mult = (oil_price / 80) ** 1.5 

# --- 4. TAB SYSTEM ---
tab1, tab2, tab3 = st.tabs(["🌍 Global Tension Map", "📰 Live Intelligence Feed", "📊 War Score Analytics"])

# ---------------------------------------------------------
# TAB 1: WORLD TENSION MAP
# ---------------------------------------------------------
with tab1:
    st.subheader("Global Kinetic Heatmap (1980 - 2030)")
    
    # We map your specific ACLED fatality columns to coordinates
    # Note: If your columns are ALL CAPS in the parquet, change these to match!
    region_map = {
        'Africa': [1.0, 17.0, 'acled_africa_FATALITIES'],
        'Middle East': [29.0, 43.0, 'acled_middle_east_FATALITIES'],
        'Asia': [15.0, 120.0, 'acled_asia_pacific_FATALITIES'],
        'Europe': [48.0, 18.0, 'acled_europe_central_asia_FATALITIES'],
        'Americas': [-15.0, -60.0, 'acled_latin_america_the_caribbean_FATALITIES']
    }

    # Data Processing for Heatmap
    df_monthly = df.resample('ME').mean(numeric_only=True).fillna(0)
    time_index = [d.strftime('%Y-%m') for d in df_monthly.index]
    
    heat_data = []
    for index, row in df_monthly.iterrows():
        step = []
        # Future Projection Logic (Apply oil multiplier after 2024)
        m_val = risk_mult if index.year >= 2024 else 1.0
        
        for name, info in region_map.items():
            lat, lon, col = info
            # Search for column (case-insensitive check for safety)
            actual_col = next((c for c in all_cols if c.lower() == col.lower()), None)
            
            if actual_col:
                val = float(row.get(actual_col, 0))
                if val > 0:
                    weight = float(np.log1p(val * m_val))
                    step.append([lat, lon, weight])
        
        # Security: Always provide at least one point to prevent IndexError
        if not step: step = [[51.5, -0.1, 0.0]] 
        heat_data.append(step)

    # Create the Folium Map
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB dark_matter')
    HeatMapWithTime(heat_data, index=time_index, radius=25, max_opacity=0.7, auto_play=False).add_to(m)
    
    # Render using HTML bypass to prevent the "get_bounds" crash
    components.html(m._repr_html_(), height=600)

# ---------------------------------------------------------
# TAB 2: LIVE NEWS UPDATES
# ---------------------------------------------------------
with tab2:
    st.subheader("📡 Live Signal Intelligence")
    
    try:
        # Pull key from .streamlit/secrets.toml
        api_key = st.secrets["NEWS_API_KEY"]
        url = f'https://newsapi.org/v2/everything?q=conflict+OR+geopolitics&apiKey={api_key}&language=en&sortBy=publishedAt'
        
        response = requests.get(url)
        news_data = response.json()

        if news_data.get("articles"):
            for article in news_data["articles"][:8]:
                with st.expander(f"🛰️ {article['source']['name']}: {article['title']}"):
                    st.write(f"**Source:** {article['source']['name']} | **Date:** {article['publishedAt'][:10]}")
                    st.write(article['description'])
                    st.link_button("Read Full Intel", article['url'])
        else:
            st.info("No active conflict signals detected in current cycle.")
            
    except Exception as e:
        st.error(f"News Signal Interrupted: Ensure NEWS_API_KEY is in secrets.toml")

# ---------------------------------------------------------
# TAB 3: DANGER WAR SCORE
# ---------------------------------------------------------
with tab3:
    st.subheader("📈 SOFIE Kinetic Index")
    
    # War Score Normalization
    fatality_cols = [c for c in all_cols if 'FATALITIES' in c]
    if fatality_cols:
        current_val = df[fatality_cols].iloc[-1].mean()
        avg_val = df[fatality_cols].mean().mean()
        
        # Normalize: Score of 50 = Average History. 100 = Double history/High Risk.
        base_score = (current_val / (avg_val + 0.1)) * 50
        war_score = min(base_score * risk_mult, 100.0) # Cap at 100
    else:
        war_score = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("War Danger Score", f"{war_score:.1f}/100", delta=f"{oil_price-80}% Pressure")
    col2.metric("Kinetic Status", "CRITICAL" if war_score > 70 else "ELEVATED" if war_score > 40 else "STABLE")
    col3.metric("Monitored Features", len(all_cols))

    st.write("### Regional Volatility Forecast")
    # Show the last 2 years + next 5 years projection trend
    trend_data = df_monthly[fatality_cols].tail(84) # 7 years of months
    st.area_chart(trend_data)
