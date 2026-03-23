import os
import argparse
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# 1. PATH & MODULE SETUP
BASE_DIR = r"C:\Users\Empok\Documents\GitHub\Sofie"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from src.utils.visualizer import SofieVisualizer
    from src.utils.data_processor import SofieDataEngine
    # Optional modules - wrapped in try/except for stability
    try:
        from src.utils.migration_engine import MigrationEngine
        mig_engine = MigrationEngine()
        displacement_data = mig_engine.get_displacement_risk()
    except ImportError:
        print("⚠️ MigrationEngine not found. Using empty displacement map.")
        displacement_data = {}

    # Patch the visualizer's global namespace to prevent the line 95 crash
    import src.utils.visualizer as vis_mod
    vis_mod.displacement_map = {}
    
    print("✅ System Core: Quad-Nexus Engines Online")
except Exception as e:
    print(f"❌ Critical Import Error: {e}")
    sys.exit(1)

# 2. CALCULATION LOGIC
def calculate_nexus(row, displacement_map):
    """
    Calculates the 2026 Quad-Nexus Score.
    Weights: 40% Conflict, 30% Sentiment (Market), 30% Displacement
    """
    try:
        # Conflict Pillar (from ACLED conflict_index)
        # Using .get() to avoid KeyErrors if columns are named differently
        hazard = float(row.get('CONFLICT_INDEX', row.get('conflict_index', 0.5)))
        
        # Sentiment Pillar (Fallback to 0.2 if missing)
        sentiment = abs(float(row.get('SENTIMENT_SCORE', 0.2)))
        
        # Humanitarian Pillar (from displacement_map)
        country_name = str(row.get('COUNTRY', 'Global'))
        displacement = float(displacement_map.get(country_name, 0.0))
        
        # Weighted Calculation (0-100 scale)
        nexus_base = (hazard * 0.4) + (sentiment * 0.3) + (displacement * 0.3)
        score = nexus_base * 100
        
        # Force Multiplier for high-risk zones
        if hazard > 0.7 and displacement > 0.7:
            score = min(100, score * 1.1)
            
        return round(score, 2)
    except Exception:
        return 25.0 # Safe baseline

def record_history(score, scenario_name):
    output_path = os.path.join(BASE_DIR, "Data", "exports")
    os.makedirs(output_path, exist_ok=True)
    history_file = os.path.join(output_path, "stability_history.csv")
    file_exists = os.path.isfile(history_file)
    with open(history_file, "a") as f:
        if not file_exists:
            f.write("Timestamp,Scenario,Score\n")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"{timestamp},{scenario_name},{score}\n")

def main():
    # Setup
    now = datetime.now()
    file_suffix = now.strftime("%H%M")
    
    parser = argparse.ArgumentParser(description="SOFIE Evolved v2.0")
    parser.add_argument('--scenario', type=str, default='baseline')
    args = parser.parse_args()

    print("="*55)
    print(f"--- SOFIE QUAD-NEXUS | {now.strftime('%B %d, %Y')} ---")
    print("="*55 + "\n")

    # A. DATA INGESTION
    engine = SofieDataEngine(root_dir=BASE_DIR)
    live_stats = engine.run_all()
    
    # B. GEOPOLITICAL ANALYSIS
    tension_map_data = {}
    global_stability = 50.0

    try:
        # Load ACLED 2026 Data
        acled_path = os.path.join(BASE_DIR, "Data", "processed", "acled_risk_indices.csv")
        df = pd.read_csv(acled_path)
        df.columns = [c.upper() for c in df.columns]
        
        # Filter for 2026 and apply Quad-Nexus logic
        current_2026 = df[df['YEAR'] == 2026].copy()
        current_2026['NEXUS_SCORE'] = current_2026.apply(
            lambda x: calculate_nexus(x, displacement_data), axis=1
        )
        
        # Prepare Map Data (ISO or Country mapping)
        c_col = 'COUNTRY' if 'COUNTRY' in current_2026.columns else current_2026.columns[0]
        tension_map_data = current_2026.set_index(c_col)['NEXUS_SCORE'].to_dict()
        
        avg_nexus = current_2026['NEXUS_SCORE'].mean()
        global_stability = max(0, 100 - avg_nexus)
        
        print(f"🌍 NEXUS ANALYSIS: Global Risk Intensity at {avg_nexus:.2f}%")
    except Exception as e:
        print(f"⚠️ Nexus Integration Error: {e}")

    # C. MARKET & SCENARIO LOGIC
    # Simplified scenario impact on stability
    scenarios = {
        'baseline': 1.0,
        'peace': 0.5,
        'blackout': 2.5,
        'ultimatum_expires': 1.8
    }
    multiplier = scenarios.get(args.scenario, 1.0)
    final_score = round(max(0, global_stability / multiplier), 2)

    # D. GENERATE DASHBOARD
    viz = SofieVisualizer()
    # Ensure alerts are strings for the visualizer
    clean_alerts = [a['title'] if isinstance(a, dict) else str(a) for a in engine.get_live_port_alerts()]
    
    try:
        path = viz.generate_unified_intel(
            score=final_score,
            at_risk=tension_map_data,
            friction=engine.get_port_friction_map(),
            alerts=clean_alerts,
            suffix=file_suffix
        )
        print(f"\n✅ SITREP GENERATED: {path}")
    except Exception as e:
        print(f"❌ Visualizer Error: {e}")

    # E. LOGGING
    record_history(final_score, args.scenario)
    
    print("="*55)
    print(f"📊 FINAL STABILITY INDEX: {final_score}%")
    print(f"STATUS: {'CRITICAL' if final_score < 40 else 'STABLE'}")
    print("="*55 + "\n")

if __name__ == "__main__":
    main()
