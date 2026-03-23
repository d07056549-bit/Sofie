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
    
    # 3. GEOPOLITICAL NEXUS (Deep Memory + Live Analysis)
    try:
        # A. Load your massive 90M-row historical baseline
        baseline_path = "Data/processed/gdelt_historical_baseline.csv"
        baseline_df = pd.read_csv(baseline_path, index_col=0)
        baseline_map = baseline_df['GoldsteinScale'].to_dict()

        # B. Load your 2026 ACLED Conflict Data
        acled_df = pd.read_csv("Data/processed/acled_risk_indices.csv")
        acled_df.columns = [c.upper() for c in acled_df.columns]
        
        # C. CALCULATION: Identify Anomalies (Current vs. Historical)
        # Logic: If Current Conflict > Historical Average, Tension spikes.
        current_risks = acled_df[acled_df['YEAR'] == 2026].copy()
        
        def calculate_anomaly(row):
            country = row['COUNTRY_CODE'] # Ensure this matches your ACLED column
            current_score = row['CONFLICT_INDEX']
            # Get historical average (Default to 0.0 if country not found)
            hist_avg = baseline_map.get(country, 0.0)
            
            # Convert Goldstein (-10 to 10) to a 0-100 scale (100 = War)
            hist_tension = ((hist_avg - 10) / -20) * 100
            
            # Return weighted average: 70% Current, 30% Historical Context
            return (current_score * 0.7) + (hist_tension * 0.3)

        current_risks['NEXUS_SCORE'] = current_risks.apply(calculate_anomaly, axis=1)
        
        # Final Global Average for the Dashboard
        global_conflict_avg = current_risks['NEXUS_SCORE'].mean()
        tension_map_data = current_risks.set_index('COUNTRY')['NEXUS_SCORE'].to_dict()

        print(f"🌍 NEXUS INTEGRATION COMPLETE: Global Intensity at {global_conflict_avg:.2f}%")

    except Exception as e:
        print(f"⚠️ Nexus Integration Error: {e}")
        global_conflict_avg = 28.5  # Realistic fallback

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
