import sys
import os
import pandas as pd
import argparse

# --- THE AGGRESSIVE PATH FIX ---
# This forces Python to look at the 'src' folder directly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'src'))
sys.path.append(os.path.join(BASE_DIR, 'src', 'utils'))

# --- ATTEMPT DIRECT IMPORTS ---
try:
    # Try importing directly from the utils folder
    from data_engine import DataEngine
    from visualizer import Visualizer
    print("✅ System Core: Loaded (Direct Access)")
except ImportError:
    try:
        # Fallback to standard src path
        from src.utils.data_engine import DataEngine
        from src.utils.visualizer import Visualizer
        print("✅ System Core: Loaded (Standard Path)")
    except ImportError as e:
        print(f"❌ Module Error: {e}")
        print(f"\nDEBUG: Project is at {BASE_DIR}")
        sys.exit(1)

def calculate_nexus(row):
    """50% Conflict + 50% Sentiment"""
    h = float(row.get('HAZARD_INDEX', 0))
    s = abs(float(row.get('SENTIMENT_SCORE', 0)))
    return round(((h * 0.5) + (s * 0.5)) * 100, 2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', default='baseline')
    args = parser.parse_args()

    print(f"\n--- SOFIE EVOLVED v2.0 | SCENARIO: {args.scenario.upper()} ---")
    
    # Path to your processed ACLED data
    data_file = os.path.join(BASE_DIR, "Data", "processed", "acled_risk_indices.csv")
    
    if not os.path.exists(data_file):
        print(f"❌ Data Missing: {data_file}")
        return

    # Initialize Engines
    engine = DataEngine()
    viz = Visualizer()
    
    try:
        # Load and Clean
        df = pd.read_csv(data_file)
        df.columns = [c.upper() for c in df.columns]
        
        # Filter for 2026 Baseline
        current = df[df['YEAR'] == 2026].copy()
        current['NEXUS_SCORE'] = current.apply(calculate_nexus, axis=1)
        
        # Prepare Visuals
        # If your CSV uses 'COUNTRY' instead of 'ISO', this handles both
        map_key = 'ISO' if 'ISO' in current.columns else 'COUNTRY'
        risk_map = current.set_index(map_key)['NEXUS_SCORE'].to_dict()
        
        avg_risk = current['NEXUS_SCORE'].mean()
        stability = max(0, 100 - (avg_risk * 1.2))

        # Generate the PNG Sitrep
        path = viz.generate_unified_intel(
            score=stability,
            at_risk=risk_map,
            friction=engine.get_port_friction_map(),
            alerts=engine.get_live_port_alerts(),
            suffix="restore_fix"
        )
        
        print(f"=======================================================")
        print(f"✅ SITREP GENERATED: {path}")
        print(f"📊 GLOBAL STABILITY: {stability:.2f}%")
        print(f"=======================================================")

    except Exception as e:
        print(f"❌ Runtime Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
