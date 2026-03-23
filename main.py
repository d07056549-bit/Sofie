import pandas as pd
import numpy as np
import argparse
import sys
import os

# --- FORCE PATH RECOGNITION ---
# This ensures Python sees the 'src' folder regardless of how it's launched
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.utils.data_engine import DataEngine
    from src.utils.visualizer import Visualizer
    print("✅ Modules Imported Successfully.")
except ImportError as e:
    print(f"❌ Critical Error: Could not import SOFIE modules.")
    print(f"Details: {e}")
    print(f"Looking in: {current_dir}")
    sys.exit(1)

def calculate_nexus(row):
    """2-Pillar Baseline: Conflict + Sentiment"""
    try:
        hazard = float(row.get('HAZARD_INDEX', 0))
        sentiment = abs(float(row.get('SENTIMENT_SCORE', 0)))
        # 50/50 weighting
        nexus = (hazard * 0.5) + (sentiment * 0.5)
        return round(nexus * 100, 2)
    except:
        return 0.0

def main():
    parser = argparse.ArgumentParser(description="SOFIE Evolved v2.0")
    parser.add_argument('--scenario', type=str, default='baseline')
    args = parser.parse_args()

    print(f"\n--- SOFIE EVOLVED: SYSTEM RESTORED ---")
    
    # Check for the data file before starting
    data_path = "Data/processed/acled_risk_indices.csv"
    if not os.path.exists(data_path):
        print(f"❌ Error: Data file not found at {data_path}")
        return

    data_engine = DataEngine()
    visualizer = Visualizer()
    
    try:
        # 1. Load Data
        maritime_data = data_engine.get_port_friction_map()
        market_stats = data_engine.get_market_baseline()
        
        acled_df = pd.read_csv(data_path)
        acled_df.columns = [c.upper() for c in acled_df.columns]
        
        # Adjusting column name case for safety
        year_col = 'YEAR' if 'YEAR' in acled_df.columns else 'year'
        current_risks = acled_df[acled_df[year_col] == 2026].copy()
        
        # 2. Process Risk
        current_risks['NEXUS_SCORE'] = current_risks.apply(calculate_nexus, axis=1)
        
        # 3. Aggregate Statistics
        iso_col = 'ISO' if 'ISO' in current_risks.columns else 'COUNTRY'
        tension_map_data = current_risks.set_index(iso_col)['NEXUS_SCORE'].to_dict()
        avg_risk = current_risks['NEXUS_SCORE'].mean()
        stability_score = max(0, 100 - (avg_risk * 1.2))
        
        # 4. Export Visuals
        status = "STABLE" if stability_score > 50 else "CRITICAL"
        output_path = visualizer.generate_unified_intel(
            score=stability_score,
            at_risk=tension_map_data,
            friction=maritime_data,
            alerts=data_engine.get_live_port_alerts(),
            suffix="restored"
        )

        print(f"=======================================================")
        print(f"STATUS: {status}. Stability Index: {stability_score:.2f}%")
        print(f"SITREP EXPORTED: {output_path}")
        print(f"=======================================================")

    except Exception as e:
        print(f"❌ Execution Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
