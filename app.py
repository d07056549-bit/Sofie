import requests
import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMapWithTime
import streamlit.components.v1 as components

st.set_page_config(page_title="SOFIE | Strategic Command", layout="wide")

# --- 1. DATA ENGINE ---
@st.cache_data
def load_data():
    path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\master\master.parquet"
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    return df

df = load_data()

# --- 2. SIDEBAR CONTROLS ---
st.sidebar.title("🎛️ Command Controls")
oil_price = st.sidebar.slider("Forecast Oil Price ($)", 70, 300, 100)
risk_mult = (oil_price / 80) ** 1.5

# --- 3. TAB SYSTEM ---
tab1, tab2, tab3 = st.tabs(["🌍 Global Tension Map", "📰 Live Intelligence Feed", "📊 War Score Analytics"])

# ---------------------------------------------------------
# TAB 1: WORLD TENSION MAP (Fixed IndexError Bypass)
# ---------------------------------------------------------
with tab1:
    st.subheader("Global Kinetic Heatmap (1980 - 2030)")
    
    region_map = {
        'Africa': [1.0, 17.0, 'acled_africa_FATALITIES'],
        'Middle East': [29.0, 43.0, 'acled_middle_east_FATALITIES'],
        'Asia': [15.0, 120.0, 'acled_asia_pacific_FATALITIES'],
        'Europe': [48.0, 18.0, 'acled_europe_central_asia_FATALITIES'],
        'Americas': [-15.0, -60.0, 'acled_latin_america_the_caribbean_FATALITIES']
    }

    df_monthly = df.resample('ME').mean(numeric_only=True).fillna(0)
    time_index = [d.strftime('%Y-%m') for d in df_monthly.index]
    
    heat_data = []
    for index, row in df_monthly.iterrows():
        step = []
        # Projection multiplier for future dates
        m_val = risk_mult if index.year >= 2024 else 1.0
        for name, info in region_map.items():
            lat, lon, col = info
            weight = float(np.log1p(row.get(col, 0) * m_val))
            if weight > 0:
                step.append([lat, lon, weight])
        
        # Ensure every step has at least one valid point (London Ghost Point)
        if not step: step = [[51.5, -0.1, 0.0]]
        heat_data.append(step)

    # CREATE MAP
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB dark_matter')
    HeatMapWithTime(heat_data, index=time_index, radius=25, max_opacity=0.7).add_to(m)
    
    # 🚨 THE FIX: Render as raw HTML to avoid st_folium bounds crash
    map_html = m._repr_html_()
    components.html(map_html, height=600)

# ---------------------------------------------------------
# TAB 2: LIVE NEWS UPDATES
# ---------------------------------------------------------
with tab2:
    st.subheader("📡 Live Signal Intelligence")
    
    # 1. Access the secret key from your .streamlit/secrets.toml
    try:
        api_key = st.secrets["NEWS_API_KEY"]
        
        # 2. Setup the Request (Searching for conflict + geopolitics)
        import requests
        url = f'https://newsapi.org/v2/everything?q=conflict+OR+geopolitics&apiKey={api_key}&language=en&sortBy=publishedAt'
        
        response = requests.get(url)
        data = response.json()

        # 3. Display the results
        if data.get("articles"):
            for article in data["articles"][:10]: # Show latest 10
                with st.expander(f"🛰️ {article['source']['name']}: {article['title']}"):
                    st.write(f"**Published:** {article['publishedAt']}")
                    st.write(article['description'])
                    st.link_button("View Full Intel", article['url'])
        else:
            st.warning("No live signals found. Check your API key or query terms.")

    except KeyError:
        st.error("🔑 API Key Missing! Create `.streamlit/secrets.toml` with `NEWS_API_KEY = 'your_key'`")
    except Exception as e:
        st.error(f"Connection Error: {e}")

# ---------------------------------------------------------
# TAB 3: DANGER WAR SCORE
# ---------------------------------------------------------
with tab3:
    st.subheader("📈 SOFIE Kinetic Index")
    
    # Logic for War Score: Aggregate ACLED Fatalities + Oil Stress
    base_fatalities = df[[c for c in df.columns if 'FATALITIES' in c]].mean().mean()
    war_score = (base_fatalities * risk_mult) * 10 
    
    c1, c2, c3 = st.columns(3)
    c1.metric("War Danger Score", f"{war_score:.1f}/100", delta=f"{oil_price-80}% Pressure")
    c2.metric("Kinetic Volatility", "HIGH" if oil_price > 120 else "STABLE")
    c3.metric("Data Features Analyzed", "1,280")

    st.write("### Regional Risk Over Time")
    st.line_chart(df_monthly[[c for c in df.columns if 'FATALITIES' in c]].tail(50))
