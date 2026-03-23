import sys
import os
import importlib.util
import pandas as pd
import argparse

# --- 1. SET PROJECT ROOT ---
BASE_DIR = r"C:\Users\Empok\Documents\GitHub\Sofie"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def import_module_manually(name, folder):
    path = os.path.join(BASE_DIR, "src", folder, f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    # Load your specific modules
    dp_mod = import_module_manually("data_processor", "utils")
    vi_mod = import_module_manually("visualizer", "utils")
    
    # Class Linkage (SofieDataEngine & SofieVisualizer)
    DataEngineClass = getattr(dp_mod, 'SofieDataEngine')
    VisualizerClass = getattr(vi_mod, 'SofieVisualizer')
    
    # --- CRITICAL PATCH ---
    # We inject an empty displacement_map into the visualizer's global namespace
    # This prevents the "NameError" when your script checks 'if displacement_map:'
    setattr(vi_mod, 'displacement_map', {})
    
    print("✅ System Core: Legacy Modules Linked & Patched")
except Exception as e:
    print(f"❌ Structural Error: {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', default='baseline')
    args = parser.parse_args()

    # Initialize
    engine = DataEngineClass(root_dir=BASE_DIR)
    viz = VisualizerClass()
    
    # Data path for your 2026 ACLED risk indices
    risk_path = os.path.join(BASE_DIR, "Data", "processed", "acled_risk_indices.csv")
    
    try:
        # A. Trigger Maritime Stream
        engine.run_all()
        live_alerts = engine.get_live_port_alerts()
        
        # B. Process Conflict Data for the Map
        if os.path.exists(risk_path):
            df = pd.read_csv(risk_path)
            # Filter for the projection year 2026
            current = df[df['YEAR'] == 2026].copy()
            
            # Map values to countries (Visualizer uses ISO_A3 mapping internally)
            # Ensure at_risk is a dict of {Country: Score}
            risk_map = current.set_index('COUNTRY')['conflict_index'].to_dict()
            
            # Global Stability Gauge calculation
            avg_risk = current['conflict_index'].mean()
            stability = max(0, 100 - (avg_risk * 100))
        else:
            print(f"⚠️ Warning: Risk data missing at {risk_path}")
            risk_map, stability = {}, 50.0

        # C. EXECUTE GENERATION
        # We pass exactly what your SofieVisualizer expects
        path = viz.generate_unified_intel(
            score=stability,
            at_risk=risk_map,
            friction=engine.get_port_friction_map(),
            alerts=[a['title'] if isinstance(a, dict) else str(a) for a in live_alerts],
            suffix=args.scenario
        )

        print(f"\n=======================================================")
        print(f"📊 GLOBAL STABILITY: {stability:.2f}%")
        print(f"✅ SITREP GENERATED: {path}")
        print(f"=======================================================")

    except Exception as e:
        print(f"❌ Runtime Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
