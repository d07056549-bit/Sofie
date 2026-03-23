import os
import argparse
import pandas as pd
from datetime import datetime

# Import custom intelligence modules
from src.utils.visualizer import SofieVisualizer
from src.utils.data_processor import SofieDataEngine
from src.data_pipeline.loaders import DataLoader
from src.core.risk_engine import SofieRiskEngine
from src.core.scenario_engine import ScenarioEngine
from src.utils.briefing import SofieBriefing
from src.utils.alerts import SofieAlerts
from src.utils.mapper import SofieMapper

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
    global_conflict_avg = 28.5 # Safe starting value
    tension_map_data = {}      # Initialize so it doesn't crash later

    try:
        # A. Load your massive 90M-row historical baseline
        baseline_path = "Data/processed/gdelt_historical_baseline.csv"
        # Note: We use index_col=0 because CountryCode is the first column
        baseline_df = pd.read_csv(baseline_path, index_col=0)
        baseline_map = baseline_df.iloc[:, 0].to_dict() # Map Country -> Goldstein

        # B. Load your 2026 ACLED Conflict Data
        acled_df = pd.read_csv("Data/processed/acled_risk_indices.csv")
        acled_df.columns = [c.upper() for c in acled_df.columns]
        
        # Determine the correct country/country-code column
        # ACLED usually uses 'COUNTRY' or 'ISO'
        c_col = 'COUNTRY' if 'COUNTRY' in acled_df.columns else acled_df.columns[0]
        
        current_risks = acled_df[acled_df['YEAR'] == 2026].copy()
        
        def calculate_anomaly(row):
            country_name = str(row[c_col])
            current_score = row.get('CONFLICT_INDEX', 50) # Fallback to 50
            
            # Get historical average (Default to 0.0 if not found)
            hist_avg = baseline_map.get(country_name, 0.0)
            
            # Convert Goldstein (-10 to 10) to 0-100 Tension
            hist_tension = ((hist_avg - 10) / -20) * 100
            
            # Return weighted average: 70% Today's Events, 30% Long-term Context
            return (current_score * 0.7) + (hist_tension * 0.3)

        current_risks['NEXUS_SCORE'] = current_risks.apply(calculate_anomaly, axis=1)
        
        # Update Dashboard Variables
        global_conflict_avg = current_risks['NEXUS_SCORE'].mean()
        tension_map_data = current_risks.set_index(c_col)['NEXUS_SCORE'].to_dict()

        print(f"🌍 NEXUS INTEGRATION COMPLETE: Global Intensity at {global_conflict_avg:.2f}%")

    except Exception as e:
        print(f"⚠️ Nexus Integration Error: {e}")

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
        at_risk=data_engine.get_at_risk_countries(), 
        friction=data_engine.get_port_friction_map(), 
        alerts=data_engine.get_live_port_alerts(), 
        suffix=file_suffix
    )

    # 7. MULTI-DOMAIN STABILITY PREDICTION
    # Load the processed ACLED data
    import pandas as pd
    acled_data = pd.read_csv("Data/processed/acled_risk_indices.csv")
    global_conflict_avg = acled_data[acled_data['YEAR'] == 2026]['conflict_index'].mean()

    # New Weights: 30% Energy | 20% Logistics | 50% Geopolitical Risk (ACLED)
    w_energy, w_logistics, w_conflict = 0.30, 0.20, 0.50

    # Normalization
    oil_n = (min(current_scenario['oil_price'], 180) / 180) * 100
    fric_n = (min(current_scenario['port_friction'], 5.0) / 5.0) * 100
    conf_n = global_conflict_avg # Already 0-100

    stability_score = round((oil_n * w_energy) + (fric_n * w_logistics) + (conf_n * w_conflict), 2)
    
    print(f"🌍 GEOPOLITICAL Intel: Global Conflict baseline at {global_conflict_avg:.2f}%")
    
    # 8. LOGS & SUMMARY
    record_history(stability_score, args.scenario)

    print("="*55)
    print(f"--- SITREP SUMMARY: {live_date.upper()} ---") 
    status = "CRITICAL" if stability_score > 70 else "STABLE"
    print(f"STATUS: {status}. Stability Index: {stability_score}%")
    print("="*55)
    print("--- RUN COMPLETE ---\n")

if __name__ == "__main__":
    main()
