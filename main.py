import sys
import os
import importlib.util
import pandas as pd
import argparse

# --- 1. FORCE MANUAL LOADING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def import_module_manually(name, folder):
    path = os.path.join(BASE_DIR, "src", folder, f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    # Manually load the classes from the files
    de_mod = import_module_manually("data_engine", "utils")
    vi_mod = import_module_manually("visualizer", "utils")
    
    DataEngine = de_mod.DataEngine
    Visualizer = vi_mod.Visualizer
    print("✅ System Core: Loaded (Direct File Injection)")
except Exception as e:
    print(f"❌ Structural Error: {e}")
    print(f"Check that 'src/utils/data_engine.py' exists at: {os.path.join(BASE_DIR, 'src', 'utils')}")
    sys.exit(1)

# --- 2. NEXUS LOGIC ---
def calculate_nexus(row):
    try:
        h = float(row.get('HAZARD_INDEX', 0))
        s = abs(float(row.get('SENTIMENT_SCORE', 0)))
        return round(((h * 0.5) + (s * 0.5)) * 100, 2)
    except:
        return 0.0

# --- 3. MAIN LOOP ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', default='baseline')
    args = parser.parse_args()

    print(f"\n--- SOFIE EVOLVED v2.0 | SCENARIO: {args.scenario.upper()} ---")
    
    data_file = os.path.join(BASE_DIR, "Data", "processed", "acled_risk_indices.csv")
    
    if not os.path.exists(data_file):
        print(f"❌ Data Missing: {data_file}")
        return

    engine = DataEngine()
    viz = Visualizer()
    
    try:
        df = pd.read_csv(data_file)
        df.columns = [c.upper() for c in df.columns]
        
        # Filter for 2026
        current = df[df['YEAR'] == 2026].copy()
        current['NEXUS_SCORE'] = current.apply(calculate_nexus, axis=1)
        
        # Prepare Map
        map_key = 'ISO' if 'ISO' in current.columns else 'COUNTRY'
        risk_map = current.set_index(map_key)['NEXUS_SCORE'].to_dict()
        
        avg_risk = current['NEXUS_SCORE'].mean()
        stability = max(0, 100 - (avg_risk * 1.2))

        # Generate Sitrep
        path = viz.generate_unified_intel(
            score=stability,
            at_risk=risk_map,
            friction=engine.get_port_friction_map(),
            alerts=engine.get_live_port_alerts(),
            suffix="final_restore"
        )
        
        print(f"=======================================================")
        print(f"✅ SITREP GENERATED: {path}")
        print(f"📊 GLOBAL STABILITY: {stability:.2f}%")
        print(f"=======================================================")

    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    main()
