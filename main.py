import sys
import os
import pandas as pd
import argparse

# 1. FORCE SYSTEM PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

# 2. ATTEMPT IMPORTS
try:
    from src.utils.data_engine import DataEngine
    from src.utils.visualizer import Visualizer
    print("✅ System Core: Loaded")
except ImportError as e:
    print(f"❌ Module Error: {e}")
    print("\nDEBUG: Ensure 'src/utils/__init__.py' exists.")
    sys.exit(1)

def calculate_nexus(row):
    hazard = float(row.get('HAZARD_INDEX', 0))
    sentiment = abs(float(row.get('SENTIMENT_SCORE', 0)))
    return round(((hazard * 0.5) + (sentiment * 0.5)) * 100, 2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', default='baseline')
    args = parser.parse_args()

    print(f"--- SOFIE EVOLVED | SCENARIO: {args.scenario.upper()} ---")
    
    engine = DataEngine()
    viz = Visualizer()
    
    try:
        # Load Conflict Data
        df = pd.read_csv("Data/processed/acled_risk_indices.csv")
        df.columns = [c.upper() for c in df.columns]
        
        # Filter for current year
        current = df[df['YEAR'] == 2026].copy()
        current['NEXUS_SCORE'] = current.apply(calculate_nexus, axis=1)
        
        # Prepare Map
        risk_map = current.set_index('ISO')['NEXUS_SCORE'].to_dict()
        stability = 100 - current['NEXUS_SCORE'].mean()

        # Generate Output
        path = viz.generate_unified_intel(
            score=stability,
            at_risk=risk_map,
            friction=engine.get_port_friction_map(),
            alerts=engine.get_live_port_alerts(),
            suffix="restored_final"
        )
        
        print(f"✅ SITREP GENERATED: {path}")
        print(f"📊 STABILITY INDEX: {stability:.2f}%")

    except Exception as e:
        print(f"❌ Runtime Error: {e}")

if __name__ == "__main__":
    main()
