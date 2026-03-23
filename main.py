import pandas as pd
import numpy as np
import argparse
import sys
import os

# Ensure Python looks in the current directory for 'src'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.utils.data_engine import DataEngine
    from src.utils.visualizer import Visualizer
except ImportError:
    print("❌ Critical Error: Could not import SOFIE modules.")
    sys.exit(1)

def calculate_nexus(row):
    """Simple 2-Pillar Baseline: Conflict + Sentiment"""
    try:
        hazard = float(row.get('HAZARD_INDEX', 0))
        sentiment = abs(float(row.get('SENTIMENT_SCORE', 0)))
        nexus = (hazard * 0.5) + (sentiment * 0.5)
        return round(nexus * 100, 2)
    except:
        return 0.0

def main():
    parser = argparse.ArgumentParser(description="SOFIE Evolved v2.0")
    parser.add_argument('--scenario', type=str, default='baseline')
    args = parser.parse_args()

    print(f"\n--- SOFIE EVOLVED: SYSTEM RESTORED ---")
    data_engine = DataEngine()
    visualizer = Visualizer()

    try:
        maritime_data = data_engine.get_port_friction_map()
        market_stats = data_engine.get_market_baseline()
        acled_df = pd.read_csv("Data/processed/acled_risk_indices.csv")
        acled_df.columns = [c.upper() for c in acled_df.columns]

        current_risks = acled_df[acled_df['YEAR'] == 2026].copy()
        current_risks['NEXUS_SCORE'] = current_risks.apply(calculate_nexus, axis=1)

        tension_map_data = current_risks.set_index('ISO')['NEXUS_SCORE'].to_dict()
        avg_risk = current_risks['NEXUS_SCORE'].mean()
        stability_score = max(0, 100 - (avg_risk * 1.2))

        output_path = visualizer.generate_unified_intel(
            score=stability_score,
            at_risk=tension_map_data,
            friction=maritime_data,
            alerts=data_engine.get_live_port_alerts(),
            suffix="restored"
        )
        print(f"STATUS: SUCCESS. Stability Index: {stability_score:.2f}%")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
