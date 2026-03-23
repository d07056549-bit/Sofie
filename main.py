import sys
import os
import importlib.util
import pandas as pd
import argparse

# --- 1. SET PROJECT PATHS ---
BASE_DIR = r"C:\Users\Empok\Documents\GitHub\Sofie"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def import_module_manually(name, folder):
    path = os.path.join(BASE_DIR, "src", folder, f"{name}.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    # Load your specific processor and visualizer
    dp_mod = import_module_manually("data_processor", "utils")
    vi_mod = import_module_manually("visualizer", "utils")
    
    # Class names from your provided files
    DataEngineClass = getattr(dp_mod, 'SofieDataEngine', None)
    VisualizerClass = getattr(vi_mod, 'Visualizer', None)
    
    if not DataEngineClass:
        print("❌ Error: 'SofieDataEngine' not found in data_processor.py")
        sys.exit(1)
    print("✅ System Core: Linked to SofieDataEngine")
except Exception as e:
    print(f"❌ Structural Error: {e}")
    sys.exit(1)

# --- 2. RISK LOGIC ---
def calculate_nexus(row):
    """Targets 'conflict_index' from acled_risk_indices.csv"""
    try:
        # Based on your CSV snippet: 'conflict_index' is the key
        val = float(row.get('CONFLICT_INDEX', row.get('conflict_index', 0)))
        return round(val * 100, 2)
    except:
        return 0.0

# --- 3. MAIN COMMAND CENTER ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', type=str, default='baseline')
    args = parser.parse_args()

    print(f"\n--- SOFIE EVOLVED v2.0 | SITREP MARCH 2026 ---")
    
    engine = DataEngineClass(root_dir=BASE_DIR)
    viz = VisualizerClass()
    
    # Target your processed directory
    risk_path = os.path.join(BASE_DIR, "Data", "processed", "acled_risk_indices.csv")
    
    try:
        # A. Trigger Maritime/Trade Sensors
        maritime_intel = engine.run_all()
        live_alerts = engine.get_live_port_alerts()
        trade_exposure = engine.get_at_risk_countries()
        
        # B. Process Risk Indices
        if os.path.exists(risk_path):
            df = pd.read_csv(risk_path)
            # Filter for the projection year 2026
            current = df[df['YEAR'] == 2026].copy() if 'YEAR' in df.columns else df[df['year'] == 2026].copy()
            current['NEXUS_SCORE'] = current.apply(calculate_nexus, axis=1)
            
            # Use 'COUNTRY' for the mapping
            country_col = 'COUNTRY' if 'COUNTRY' in current.columns else 'country'
            risk_map = current.set_index(country_col)['NEXUS_SCORE'].to_dict()
            stability_score = max(0, 100 - current['NEXUS_SCORE'].mean())
        else:
            print(f"⚠️ Risk data missing at {risk_path}")
            risk_map = {}
            stability_score = 50.0

        # C. Export Unified Intel
        alert_titles = [a['title'] for a in live_alerts if isinstance(a, dict)]
        
        export_path = viz.generate_unified_intel(
            score=stability_score,
            at_risk=risk_map,
            friction=engine.get_port_friction_map(),
            alerts=alert_titles if alert_titles else ["System Online"],
            suffix=f"{args.scenario}_deploy"
        )

        print(f"\n=======================================================")
        print(f"📊 GLOBAL STABILITY: {stability_score:.2f}%")
        print(f"🌍 TOP TRADE EXPOSURE: {', '.join(trade_exposure[:2])}")
        print(f"✅ SITREP EXPORTED: {export_path}")
        print(f"=======================================================\n")

    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    main()
