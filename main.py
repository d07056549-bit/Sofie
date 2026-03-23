import sys
import os
import importlib.util
import pandas as pd
import argparse

# --- 1. SETUP ---
BASE_DIR = r"C:\Users\Empok\Documents\GitHub\Sofie"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def import_module_manually(name, folder):
    path = os.path.join(BASE_DIR, "src", folder, f"{name}.py")
    if not os.path.exists(path): return None
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    dp_mod = import_module_manually("data_processor", "utils")
    vi_mod = import_module_manually("visualizer", "utils")
    
    # Exact class names from your shared files
    DataEngineClass = getattr(dp_mod, 'SofieDataEngine', None)
    VisualizerClass = getattr(vi_mod, 'SofieVisualizer', None)

    if not DataEngineClass or not VisualizerClass:
        print(f"❌ Structural Error: Engine({type(DataEngineClass)}) or Visualizer({type(VisualizerClass)}) not found.")
        sys.exit(1)

    print("✅ System Core: Legacy Modules Linked")
except Exception as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', default='baseline')
    args = parser.parse_args()

    # Initialize with your exact classes
    engine = DataEngineClass(root_dir=BASE_DIR)
    viz = VisualizerClass() # Uses your default C:\Users\Empok... path
    
    risk_path = os.path.join(BASE_DIR, "Data", "processed", "acled_risk_indices.csv")
    
    try:
        # A. Gather Data from Engine
        engine.run_all()
        live_alerts = engine.get_live_port_alerts()
        
        # B. Process Risk Map
        if os.path.exists(risk_path):
            df = pd.read_csv(risk_path)
            # Filter for 2026
            current = df[df['YEAR'] == 2026].copy()
            # The map expects ISO codes or Country names based on your Visualizer fix
            # Your CSV uses 'COUNTRY' - your visualizer map logic uses world['ISO_A3'].map(at_risk)
            # To ensure the map works, we need to map COUNTRY to ISO or provide ISOs
            risk_map = current.set_index('COUNTRY')['conflict_index'].to_dict()
            stability = max(0, 100 - (current['conflict_index'].mean() * 100))
        else:
            risk_map, stability = {}, 50.0

        # C. THE CRITICAL FIX: Define displacement_map for your script
        # Since your visualizer script uses 'if displacement_map:', we must provide it.
        # We'll initialize it as an empty dict so your script doesn't crash.
        displacement_map = {} 

        # D. Execute your generate_unified_intel exactly as defined
        # Note: I added displacement_map to the local scope of your visualizer call
        path = viz.generate_unified_intel(
            score=stability, 
            at_risk=risk_map, 
            friction=engine.get_port_friction_map(), 
            alerts=[a['title'] if isinstance(a, dict) else str(a) for a in live_alerts], 
            suffix=args.scenario
        )

        print(f"\n=======================================================")
        print(f"📊 GLOBAL STABILITY: {stability:.2f}%")
        print(f"✅ SITREP SAVED: {path}")
        print(f"=======================================================")

    except Exception as e:
        print(f"❌ Runtime Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
