import os
import argparse
import requests
import pandas as pd
from datetime import datetime

# Import custom intelligence modules
from src.utils.visualizer import SofieVisualizer
from src.utils.data_processor import SofieDataEngine

def fetch_live_world_tension():
    """Fetches real-time global conflict intensity from GDELT."""
    print("📡 CONNECTING TO LIVE GEOPOLITICAL STREAM (GDELT)...")
    
    # Query for 'Conflict' and 'Protest' themes in the last 24 hours
    url = "https://api.gdeltproject.org/api/v2/doc/doc?query=(theme:TAX_WORLDMAM_CONFLICT%20OR%20theme:TAX_MILITARY_ACTION)&mode=TimelineVol&format=json&timespan=24h"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # GDELT returns 'TimelineVol' (Volume of news). 
        # We normalize this into a 0-100 Tension Score.
        # Higher volume of 'Conflict' news = Higher World Tension.
        latest_vol = data['timeline'][0]['data'][-1]['value']
        
        # Simple Normalization (Adjust the 5.0 divisor based on how 'sensitive' you want it)
        live_score = min(float(latest_vol) * 10, 100) 
        return round(live_score, 2)
    except Exception as e:
        print(f"⚠️ Live Feed Offline: {e}. Falling back to CSV.")
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
    
    # 3. GEOPOLITICAL CONSENSUS (Nexus: History + Live)
    # --- Initialize Defaults to prevent UnboundLocalError ---
    world_tension = 2.18 # Your last known stable baseline
    tension_map_data = {} 
    
    # Try fetching Live Feed
    live_tension = fetch_live_world_tension()
    
    try:
        # Load CSV History (The "Memory")
        acled_df = pd.read_csv("Data/processed/acled_risk_indices.csv")
        acled_df.columns = [c.upper() for c in acled_df.columns]
        
        # 1. Calculate Historical Tension (Top 10 Hotspots)
        latest_year = acled_df['YEAR'].max()
        hist_latest = acled_df[acled_df['YEAR'] == latest_year]
        hist_score = hist_latest['CONFLICT_INDEX'].nlargest(10).mean()

        # 2. Blend Logic: 60% History / 40% Live
        if live_tension is not None:
            world_tension = (hist_score * 0.6) + (live_tension * 0.4)
            print(f"🌍 WORLD TENSION: {world_tension:.2f}% (Nexus Blend: {live_tension}% Live / {hist_score:.1f}% Hist)")
        else:
            world_tension = hist_score
            print(f"🌍 WORLD TENSION: {world_tension:.2f}% (Historical Mode Only)")

        # 3. Prep Map Data (Always use CSV for the geography)
        tension_map_data = hist_latest.set_index('COUNTRY')['CONFLICT_INDEX'].to_dict()
        global_conflict_avg = world_tension
        
    except Exception as e:
        print(f"⚠️ Geopolitical Engine Error: {e}")
        # Final safety fallback
        global_conflict_avg = 23.79 
        tension_map_data = {}

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
