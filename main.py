import sys
import os
import importlib.util
import pandas as pd
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def import_module_manually(name, folder):
    path = os.path.join(BASE_DIR, "src", folder, f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    dp_mod = import_module_manually("data_processor", "utils")
    vi_mod = import_module_manually("visualizer", "utils")
    
    # --- AUTO-DETECT CLASS NAME ---
    # We look for ANY class defined in your file if 'DataProcessor' isn't there
    DataProcessor = getattr(dp_mod, 'DataProcessor', None)
    if not DataProcessor:
        classes = [cls for cls in dir(dp_mod) if isinstance(getattr(dp_mod, cls), type)]
        if classes:
            DataProcessor = getattr(dp_mod, classes[0])
            print(f"✅ Auto-Detected Class: {classes[0]}")
    
    Visualizer = getattr(vi_mod, 'Visualizer', None)
    print("✅ System Core: Linked")
except Exception as e:
    print(f"❌ Structural Error: {e}")
    sys.exit(1)

def calculate_nexus(row):
    h = float(row.get('HAZARD_INDEX', 0))
    s = abs(float(row.get('SENTIMENT_SCORE', 0)))
    return round(((h * 0.5) + (s * 0.5)) * 100, 2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', default='baseline')
    args = parser.parse_args()
    print(f"\n--- SOFIE EVOLVED v2.0 | SCENARIO: {args.scenario.upper()} ---")
    
    # Initialize
    processor = DataProcessor()
    viz = Visualizer()
    
    data_file = os.path.join(BASE_DIR, "Data", "processed", "acled_risk_indices.csv")
    
    try:
        df = pd.read_csv(data_file)
        df.columns = [c.upper() for c in df.columns]
        current = df[df['YEAR'] == 2026].copy()
        current['NEXUS_SCORE'] = current.apply(calculate_nexus, axis=1)
        
        risk_map = current.set_index('ISO')['NEXUS_SCORE'].to_dict()
        stability = 100 - current['NEXUS_SCORE'].mean()

        path = viz.generate_unified_intel(
            score=stability, at_risk=risk_map,
            friction=getattr(processor, 'get_port_friction_map', lambda: {})(),
            alerts=getattr(processor, 'get_live_port_alerts', lambda: [])(),
            suffix="restored"
        )
        
        print(f"✅ SITREP GENERATED: {path}")
        print(f"📊 STABILITY INDEX: {stability:.2f}%")
    except Exception as e:
        print(f"❌ Runtime Error: {e}")

if __name__ == "__main__":
    main()
