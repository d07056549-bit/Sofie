import os
import argparse
import pandas as pd
from datetime import datetime

# Import custom intelligence modules
from src.utils.visualizer import SofieVisualizer
from src.utils.data_processor import SofieDataEngine

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
    
    # 3. GEOPOLITICAL CONSENSUS (World Tension Model)
    tension_map_data = {} # Initialize empty dict for the map
    
    try:
        # Load ACLED (Tactical/Riots)
        acled_df = pd.read_csv("Data/processed/acled_risk_indices.csv")
        acled_df.columns = [c.upper() for c in acled_df.columns]
        latest_year_acled = acled_df['YEAR'].max()
        
        # Filter for latest year and get Top 10 for the Global Score
        acled_latest = acled_df[acled_df['YEAR'] == latest_year_acled]
        top_acled_score = acled_latest['CONFLICT_INDEX'].nlargest(10).mean()

        # Load UCDP (Strategic/Warfare)
        ucdp_df = pd.read_csv("Data/processed/ucdp_risk_indices.csv")
        ucdp_df.columns = [c.upper() for c in ucdp_df.columns]
        latest_year_ucdp = ucdp_df['YEAR'].max()
        
        # Filter for latest year and get Top 10 for the Global Score
        ucdp_latest = ucdp_df[ucdp_df['YEAR'] == latest_year_ucdp]
        top_ucdp_score = ucdp_latest['UCDP_RISK_INDEX'].nlargest(10).mean()

        # --- CALCULATE GLOBAL TENSION ---
        world_tension = (top_acled_score + top_ucdp_score) / 2
        global_conflict_avg = world_tension
        
        # --- PREPARE DATA FOR THE MAP ---
        # We merge the two datasets to get a single score per country for the heatmap
        # ACLED is our base, UCDP adds strategic depth
        acled_map = acled_latest.set_index('COUNTRY')['CONFLICT_INDEX']
        ucdp_map = ucdp_latest.set_index('COUNTRY')['UCDP_RISK_INDEX']
        
        # Combine them (taking the max risk score found in either dataset)
        combined_map = pd.concat([acled_map, ucdp_map], axis=1).fillna(0).max(axis=1)
        tension_map_data = combined_map.to_dict()

        print(f"🌍 WORLD TENSION: Current Flashpoint Intensity at {world_tension:.2f}%")
        
    except Exception as e:
        print(f"⚠️ Tension Calculation Error: {e}")
        global_conflict_avg = 0.47 
        tension_map_data = {} # Map will fall back to grey if this fails

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
