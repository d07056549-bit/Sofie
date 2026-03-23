import sys
import os
import importlib.util
import pandas as pd
import argparse

# --- 1. SET PROJECT ROOT ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def import_module_manually(name, folder):
    path = os.path.join(BASE_DIR, "src", folder, f"{name}.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    # --- 2. ADAPT TO YOUR FILENAMES ---
    # We load 'data_processor' instead of 'data_engine'
    dp_mod = import_module_manually("data_processor", "utils")
    vi_mod = import_module_manually("visualizer", "utils")
    
    # Check if the class inside is named DataProcessor or DataEngine
    # This handles both possibilities
    DataProcessor = getattr(dp_mod, 'DataProcessor', getattr(dp_mod, 'DataEngine', None))
    Visualizer = getattr(vi_mod, 'Visualizer', None)
    
    print("✅ System Core: DataProcessor Linked")
except Exception as e:
    print(f"❌ Structural Error: {e}")
    print(f"DEBUG: Verify 'src/utils/data_processor.py' and 'src/utils/visualizer.py' exist.")
    sys.exit(1)

def calculate_nexus(row):
    """50/50 Conflict & Sentiment Baseline"""
    try:
        h = float(row.get('HAZARD_INDEX', 0))
        s = abs(float(row.get('SENTIMENT_SCORE', 0)))
        return round(((h * 0.5) + (s * 0.5)) * 100, 2)
    except:
        return 0.0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', default='baseline')
    args = parser.parse_args()

    print(f"\n--- SOFIE EVOLVED v2.0 | SCENARIO: {args.scenario.upper()} ---")
    
    # Path to your ACLED risk data
    data_file = os.path.join(BASE_DIR, "Data", "processed", "acled_risk_indices.csv")
    
    # Initialize your processor
    processor = DataProcessor()
    viz = Visualizer()
    
    try:
        if not os.path.exists(data_file):
            print(f"⚠️ Warning: {data_file} not found. Using internal processor defaults.")
            # If CSV is missing, we can't do the full map, but we can run the logic
            return

        df = pd.read_csv(data_file)
        df.columns = [c.upper() for c in df.columns]
        
        # Process 2026 Baseline
        current = df[df['YEAR'] == 2026].copy()
        current['NEXUS_SCORE'] = current.apply(calculate_nexus, axis=1)
        
        # Mapping for Visualizer
        map_key = 'ISO' if 'ISO' in current.columns else 'COUNTRY'
        risk_map = current.set_index(map_key)['NEXUS_SCORE'].to_dict()
        
        avg_risk = current['NEXUS_SCORE'].mean()
        stability = max(0, 100 - (avg_risk * 1.2))

        # Generate the Sitrep
        # Note: We check for 'get_port_friction_map' or similar in your processor
        friction = getattr(processor, 'get_port_friction_map', lambda: {})()
        alerts = getattr(processor, 'get_live_port_alerts', lambda: ["System Online"])()

        path = viz.generate_unified_intel(
            score=stability,
            at_risk=risk_map,
            friction=friction,
            alerts=alerts,
            suffix="restored_processor"
        )
        
        print(f"=======================================================")
        print(f"✅ SITREP GENERATED: {path}")
        print(f"📊 GLOBAL STABILITY: {stability:.2f}%")
        print(f"=======================================================")

    except Exception as e:
        print(f"❌ Runtime Error: {e}")

if __name__ == "__main__":
    main()
