import os
import argparse
import requests
import pandas as pd
from datetime import datetime
from gdeltdoc import GdeltDoc, Filters

# Import custom intelligence modules
from src.utils.visualizer import SofieVisualizer
from src.utils.data_processor import SofieDataEngine

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
        
        # --- FIX: Ensure ISO exists for the Visualizer ---
        # We create a reverse map from our iso_fix dictionary to fill in missing ISOs
        name_to_iso = {v: k for k, v in iso_fix.items()}
        if 'ISO' not in acled_df.columns:
            acled_df['ISO'] = acled_df[c_col].map(name_to_iso).fillna('GLOBAL')

        current_risks = acled_df[acled_df['YEAR'] == 2026].copy()

        def calculate_nexus(row):
            country = str(row[c_col])
            iso3 = row.get('ISO', 'GLOBAL')
            current = row.get('CONFLICT_INDEX', 50)
            hist_avg = baseline_map.get(country, 0.0)
            hist_tension = max(0, ((hist_avg - 10) / -20) * 100)
            sentiment = gpr_map.get(iso3, latest_gpr_row['GPR'] / 2.0)
            sentiment_n = min(sentiment * 60, 100) 
            hazard_score = hazard_map.get(iso3, 10.0)

            score = (current * 0.40) + (hist_tension * 0.20) + (sentiment_n * 0.20) + (hazard_score * 0.20)
            return min(100, (score ** 1.1))

        current_risks['NEXUS_SCORE'] = current_risks.apply(calculate_nexus, axis=1)
        global_conflict_avg = current_risks['NEXUS_SCORE'].mean()
        tension_map_data = current_risks.set_index('ISO')['NEXUS_SCORE'].to_dict()

        print(f"🌍 QUAD-NEXUS ONLINE: Global Intensity at {global_conflict_avg:.2f}%")
    except Exception as e:
        print(f"⚠️ Nexus Integration Error: {e}")

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

    # --- NEW: DATA COVERAGE AUDIT (Aligned with the code above) ---
    # Note: 'world' must be accessible here. 
    # If 'world' was defined inside the 'try' block, move this audit inside there too.
    try:
        import geopandas as gpd
        world_data = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
        all_countries = set(world_data['NAME'].unique())
        covered_countries = set(tension_map_data.keys())
        missing = all_countries - covered_countries
        
        print(f"📊 DATA COVERAGE: {len(covered_countries)}/{len(all_countries)} countries mapped.")
        if missing:
            print(f"⚠️ MISSING NODES (Sample): {list(missing)[:10]}")
    except Exception as audit_err:
        print(f"⚠️ Audit skipped: {audit_err}")

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
