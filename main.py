import os
import argparse
import requests
import pandas as pd
from datetime import datetime
from gdeltdoc import GdeltDoc, Filters

# Import custom intelligence modules
from src.utils.visualizer import SofieVisualizer
from src.utils.data_processor import SofieDataEngine
from src.utils.migration_engine import MigrationEngine
mig_engine = MigrationEngine()
displacement_map = mig_engine.get_displacement_risk()

def fetch_live_world_tension():
    """Optimized live feed for broader news capture."""
    print("📡 ANALYZING LIVE GLOBAL NEWS STREAM (GDELT 2.0)...")
    
    # Using 'timespan' instead of specific dates is much more reliable
    f = Filters(
        keyword = "(conflict OR military OR crisis OR blockade)", 
        timespan = "24h" # Scans the last 24 hours relative to NOW
    )
    gd = GdeltDoc()
    
    try:
        timeline = gd.timeline_search("timelinevol", f)
        
        if timeline is not None and not timeline.empty:
            latest_vol = timeline['value'].iloc[-1]
            # News volume is usually a small decimal (e.g. 0.05%)
            # We multiply by 100 to get a 0-100 scale
            live_score = min(float(latest_vol) * 100, 100) 
            return round(live_score, 2)
        
        print("⚠️ GDELT returned empty timeline. Using historical baseline.")
        return None
        
    except Exception as e:
        print(f"⚠️ GDELT Client Error: {e}. Reverting to Historical CSV.")
        return None
        
    except Exception as e:
        print(f"⚠️ GDELT Client Error: {e}. Reverting to Historical CSV.")
        return None

def record_history(score, scenario_name, output_path=r"C:\Users\Empok\Documents\GitHub\Sofie\Data\exports"):
    os.makedirs(output_path, exist_ok=True)
    history_file = os.path.join(output_path, "stability_history.csv")
    file_exists = os.path.isfile(history_file)
    with open(history_file, "a") as f:
        if not file_exists:
            f.write("Timestamp,Scenario,Score\n")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"{timestamp},{scenario_name},{score}\n")
    print(f"📊 HISTORICAL LOG UPDATED: {history_file}")

def main():
    # 1. SETUP VARIABLES (Scoped inside main)
    now = datetime.now()
    file_suffix = now.strftime("%H%M")
    live_date = now.strftime("%B %d, %Y")
    live_time = now.strftime("%H:%M")

    parser = argparse.ArgumentParser(description="SOFIE Evolved v2.0")
    parser.add_argument('--scenario', type=str, default='baseline', 
                        choices=['baseline', 'peace', 'blackout', 'ultimatum_expires'])
    args = parser.parse_args()

    print("="*55)
    print(f"--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: {live_date} | TIME: {live_time} GMT")
    print("="*55 + "\n")

    # 2. INGESTION
    data_engine = SofieDataEngine(root_dir="Data/raw")
    live_stats = data_engine.run_all()
    
    # 3. GEOPOLITICAL NEXUS (The "Quad-Risk": ACLED + GDELT + GPR + EM-DAT)
    global_conflict_avg = 28.5 
    tension_map_data = {}      

    try:
        # A. LOAD HISTORICAL MEMORY (GDELT)
        baseline_path = "Data/processed/gdelt_historical_baseline.csv"
        baseline_df = pd.read_csv(baseline_path, index_col=0)
        baseline_map = baseline_df.iloc[:, 0].to_dict()

        # B. LOAD RECENT SENTIMENT (GPR)
        gpr_path = r"Data/raw/Events/Geopolitical Risk/data_gpr_export.csv"
        gpr_df = pd.read_csv(gpr_path)
        latest_gpr_row = gpr_df.iloc[-1]
        gpr_map = {col.replace('GPRC_', ''): latest_gpr_row[col] for col in gpr_df.columns if col.startswith('GPRC_')}

        # C. LOAD HAZARD DATA (EM-DAT)
        hazard_path = r"Data/raw/Hazards/Global Hazard & Disaster Risk Data/_EmergencyEventsDatabase-CountryProfiles_emdat-country-profiles_2023_04_06.csv"
        hazard_df = pd.read_csv(hazard_path, sep=';')
        recent_hazards = hazard_df[hazard_df['Year'] == 2023].copy()
        hazard_map = (recent_hazards.groupby('ISO')['Total Events'].sum() * 10).clip(0, 100).to_dict()

        # --- ENHANCED ISO & NAME MAPPING ---
        iso_fix = {
            # Africa
            'COD': 'Dem. Rep. Congo',
            'COG': 'Congo',
            'CAF': 'Central African Rep.',
            'SSD': 'S. Sudan',
            'CIV': "Côte d'Ivoire",
            'GNQ': 'Eq. Guinea',
            'LSO': 'Lesotho',
            
            # Asia & Oceania
            'VNM': 'Vietnam',
            'Viet Nam': 'Vietnam',
            'TLS': 'Timor-Leste',
            'VUT': 'Vanuatu',
            'BRN': 'Brunei',
            'BTN': 'Bhutan',
            'PHL': 'Philippines',
            
            # Europe & Americas
            'CZE': 'Czechia',
            'DOM': 'Dominican Rep.',
            'BHS': 'Bahamas',
            'BIH': 'Bosnia and Herz.',
            'FLK': 'Falkland Is.',
            
            # Territories & Others
            'CYP': 'N. Cyprus',
            'ATF': 'Fr. S. Antarctic Lands',
            'USA': 'United States of America',
            'TUR': 'Turkey'
        }

        # Apply the fix to your tension map
        # This ensures the map finds the scores even if names differ
        tension_map_data = {iso_fix.get(k, k): v for k, v in tension_map_data.items()}

        # D. LOAD LIVE EVENTS (ACLED 2026)
        acled_df = pd.read_csv("Data/processed/acled_risk_indices.csv")
        acled_df.columns = [c.upper() for c in acled_df.columns]
        c_col = 'COUNTRY' if 'COUNTRY' in acled_df.columns else acled_df.columns[0]

        # --- THE AUTO-BRIDGE: Learning ISOs from the Map ---
        import geopandas as gpd
        world_temp = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
        
        # Create a lookup dictionary from the map itself {Name: ISO_CODE}
        # We check both 'NAME' and 'SOVEREIGNT' to catch variations
        map_lookup = pd.concat([
            world_temp.set_index('NAME')['ISO_A3'],
            world_temp.set_index('SOVEREIGNT')['ISO_A3']
        ]).to_dict()
        
        # Add our manual overrides for the tricky ones
        map_lookup.update({
            'United States': 'USA',
            'Dem. Rep. Congo': 'COD',
            'Turkey': 'TUR',
            'Vietnam': 'VNM'
        })

        # Apply the bridge to the ACLED data
        acled_df['ISO'] = acled_df[c_col].map(map_lookup).fillna('GLOBAL')
        
        current_risks = acled_df[acled_df['YEAR'] == 2026].copy()

def calculate_nexus(row, displacement_map):
    """
    Calculates the 2026 Quad-Nexus Score by balancing:
    1. Hazard Index (Conflict Data) - 40%
    2. Sentiment Score (Market/News) - 30%
    3. Displacement Pressure (Migration) - 30%
    """
    # 1. Extract Conflict Data
    hazard = float(row.get('HAZARD_INDEX', 0))
    
    # 2. Extract Sentiment (Absolute value for intensity)
    sentiment = abs(float(row.get('SENTIMENT_SCORE', 0)))
    
    # 3. Extract Humanitarian Displacement
    # We check by Country name or ISO
    country_name = row.get('COUNTRY', 'Global')
    displacement = float(displacement_map.get(country_name, 0))
    
    # --- WEIGHTED CALCULATION ---
    # 0.4 Hazard + 0.3 Sentiment + 0.3 Displacement
    nexus_base = (hazard * 0.4) + (sentiment * 0.3) + (displacement * 0.3)

    
    # Scale to 0-100%
    nexus_score = nexus_base * 100
    
    # 4. Crisis Force Multiplier: High conflict + High displacement = Systemic Failure
    if hazard > 0.7 and displacement > 0.7:
        nexus_score = min(100.0, nexus_score * 1.1)
        
    return round(nexus_score, 2)
    
    # 2. Sentiment Pillar (0.0 to 1.0)
    # We take the absolute value because both extreme negative (-1) 
    # and extreme positive (+1) indicate high volatility/intensity.
    sentiment = abs(float(row.get('SENTIMENT_SCORE', 0)))
    
    # 3. Humanitarian Pillar (0.0 to 1.0)
    # We look up the country's displacement score from our migration data.
    # 'COUNTRY' is the name, but if you used the ISO fix, use row.get('ISO')
    country_key = row.get('COUNTRY', 'Global')
    displacement = float(displacement_map.get(country_key, 0))
    
    # --- WEIGHTED CALCULATION ---
    # Weight distribution: 0.4 Hazard + 0.3 Sentiment + 0.3 Displacement
    nexus_base = (hazard * 0.4) + (sentiment * 0.3) + (displacement * 0.3)
    
    # Scale to a percentage (0-100)
    nexus_score = nexus_base * 100
    
    # Add a 'Force Multiplier': If both Conflict and Displacement are high (>0.7),
    # it indicates a systemic collapse. We boost the score by 10%.
    if hazard > 0.7 and displacement > 0.7:
        nexus_score = min(100, nexus_score * 1.1)
        
    return round(nexus_score, 2)

    # 4. SCENARIO LOGIC (Market Driven by gpr_master_pro.csv)
    try:
        market_path = r"Data/raw/Events/Geopolitical Risk/gpr_master_pro.csv"
        market_df = pd.read_csv(market_path)
        latest_market = market_df.iloc[-1]
        
        # Baseline is now driven by your real CSV data!
        live_oil = latest_market.get('Brent', 85.0)
        live_gold = latest_market.get('Gold', 2000.0)

        scenarios = {
            'baseline': {'oil': live_oil, 'conflict': global_conflict_avg},
            'peace': {'oil': 70.0, 'conflict': global_conflict_avg * 0.5},
            'ultimatum': {'oil': live_oil * 1.5, 'conflict': global_conflict_avg * 2.0}
        }
        curr = scenarios.get(args.scenario, scenarios['baseline'])
        print(f"📊 MARKET BASELINE: Brent Oil @ ${curr['oil']:.2f} | Gold @ ${live_gold:.2f}")

    except Exception as e:
        print(f"⚠️ Market Logic Error: {e}")

    # 4. SCENARIO LOGIC
    scenarios = {
        'baseline': {'oil_price': 112.19, 'port_friction': live_stats['friction'], 'conflict': global_conflict_avg},
        'peace': {'oil_price': 72.50, 'port_friction': 1.0, 'conflict': 0.05},
        'blackout': {'oil_price': 185.00, 'port_friction': 5.0, 'conflict': global_conflict_avg * 2.5},
        'ultimatum_expires': {'oil_price': 145.20, 'port_friction': 3.5, 'conflict': global_conflict_avg * 1.8}
    }
    current = scenarios.get(args.scenario, scenarios['baseline'])

    # 5. CALCULATION
    oil_n = (min(current['oil_price'], 180) / 180) * 100
    fric_n = (min(current['port_friction'], 5.0) / 5.0) * 100
    stability_score = round((oil_n * 0.3) + (fric_n * 0.2) + (current['conflict'] * 0.5), 2)

    # 6. DASHBOARD
    visualizer = SofieVisualizer()
    visualizer.generate_unified_intel(
        score=stability_score, 
        at_risk=tension_map_data, 
        friction=data_engine.get_port_friction_map(), 
        alerts=data_engine.get_live_port_alerts(), 
        suffix=file_suffix
    )

    # 7. LOGS & SUMMARY
    record_history(stability_score, args.scenario)

    print("="*55)
    print(f"--- SITREP SUMMARY: {live_date.upper()} ---") 
    status = "CRITICAL" if stability_score > 70 else "STABLE"
    print(f"STATUS: {status}. Stability Index: {stability_score}%")
    print("="*55)
    print("--- RUN COMPLETE ---\n")

if __name__ == "__main__":
    main()
