import streamlit as st
import pandas as pd
import numpy as np
import folium
import requests
import streamlit.components.v1 as components

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="SOFIE | Strategic Command", layout="wide")

# Corrected CSS for the "Military SITREP" look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="metric-container"] {
        background-color: #1a1c24;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
    }
    </style>
    """, unsafe_allow_html=True) # Fixed: Changed from unsafe_allow_index

# --- 2. DATA LOADERS ---
@st.cache_data
def load_sofie_data():
    path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\master\master.parquet"
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    return df

@st.cache_data
def load_world_geojson():
    url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
    return requests.get(url).json()

df = load_sofie_data()
geo_world = load_world_geojson()

# --- 3. COMMAND SIDEBAR ---
with st.sidebar:
    st.title("⚔️ COMMAND CENTER")
    oil_price = st.slider("Energy Flux (Oil $/bbl)", 70, 300, 105)
    risk_sensitivity = st.select_slider("Detection Sensitivity", options=["Low", "Medium", "High", "Critical"])
    
    st.divider()
    st.info("🛰️ SOFIE v3.14 - Baseline 2100 Project")

# --- 4. TABS ---
tab1, tab2, tab3 = st.tabs(["🌍 STRATEGIC SITREP", "📡 INTEL FEED", "📈 KINETIC ANALYTICS"])

# CALCULATE GLOBAL RISK (Normalized to 100%)
fatality_cols = [c for c in df.columns if 'FATALITIES' in c]
raw_risk = df[fatality_cols].iloc[-1].mean()
oil_mult = (oil_price / 80) ** 1.5
war_score = min(((raw_risk * oil_mult) / 10) * 100, 100.0)

# ---------------------------------------------------------
# TAB 1: WORLD SITREP (Choropleth Map)
# ---------------------------------------------------------
with tab1:
    st.subheader("Global Kinetic Risk Distribution")
    
    # Static Mapping for the SitRep look
    country_risk = pd.DataFrame({
        'name': ['Russia', 'Ukraine', 'Iran', 'China', 'United States of America', 'Sudan', 'Israel'],
        'risk_val': [95 * oil_mult, 100, 85 * oil_mult, 40 * oil_mult, 15, 90, 88]
    })

    m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB dark_matter')

    folium.Choropleth(
        geo_data=geo_world,
        name="Kinetic Risk",
        data=country_risk,
        columns=["name", "risk_val"],
        key_on="feature.properties.name",
        fill_color="YlOrRd", 
        fill_opacity=0.6,
        line_opacity=0.3,
        legend_name="KINETIC INTENSITY",
        nan_fill_color="#222222"
    ).add_to(m)

    components.html(m._repr_html_(), height=600)

# ---------------------------------------------------------
# TAB 2: LIVE INTEL FEED (NewsAPI)
# ---------------------------------------------------------
with tab2:
    st.subheader("📡 Real-Time Geopolitical Signal")
    
    try:
        api_key = st.secrets["NEWS_API_KEY"]
        news_url = f"https://newsapi.org/v2/everything?q=conflict+OR+geopolitics+OR+military&sortBy=publishedAt&apiKey={api_key}&language=en"
        
        res = requests.get(news_url).json()
        
        if res.get("articles"):
            for art in res["articles"][:10]:
                with st.container():
                    col_a, col_b = st.columns([1, 4])
                    col_a.caption(art['publishedAt'][:10])
                    # Visual indicators for news importance
                    if "war" in art['title'].lower() or "attack" in art['title'].lower():
                        col_a.error("HIGH RISK")
                    else:
                        col_a.warning("MONITOR")
                        
                    col_b.markdown(f"**{art['source']['name']}**: {art['title']}")
                    with col_b.expander("View Summary"):
                        st.write(art['description'])
                        st.link_button("Source Intel", art['url'])
        else:
            st.warning("No live signals detected. Signal noise too high.")
            
    except Exception as e:
        st.error(f"Signal Lost: {e}")

# ---------------------------------------------------------
# TAB 3: KINETIC ANALYTICS
# ---------------------------------------------------------
with tab3:
    st.subheader("📊 Strategic Projections")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("War Danger Score", f"{war_score:.2f}%", delta=f"{oil_price-80}% Pressure")
    c2.metric("Regional Stability", "VOLATILE" if war_score > 60 else "STABLE")
    c3.metric("Live Intel Nodes", f"{len(df.columns)} Active")

    st.progress(war_score / 100)
    
    st.write("### 5-Year Tension Projection (Oil-Weighted)")
    st.line_chart(df[fatality_cols].tail(60) * oil_mult)
