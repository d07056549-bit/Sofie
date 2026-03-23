import sys
import os
import importlib.util
import pandas as pd
import argparse

# --- 1. FORCE MANUAL LOADING ---
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
    # Load your specific files
    dp_mod = import_module_manually("data_processor", "utils")
    vi_mod = import_module_manually("visualizer", "utils")
    
    # LINK TO YOUR CLASS NAME: SofieDataEngine
    DataEngine = getattr(dp_mod, 'SofieDataEngine', None)
    Visualizer = getattr(vi_mod, 'Visualizer', None)
    
    if not DataEngine:
        print("❌ Error: Could not find 'SofieDataEngine' class in data_processor.py")
        sys.exit(1)
        
    print("✅ System Core: SofieDataEngine Linked")
except Exception as e:
    print(f"❌ Structural Error: {e}")
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
    
    # Initialize your specific engine
    engine = DataEngine()
    viz = Visualizer()
    
    data_file = os.path.join(BASE_DIR, "Data", "processed", "acled_risk_indices.csv")
    
    try:
        # 1. Run the Maritime Processor
        maritime_results = engine.run_all()
        live_alerts = engine.get_live_port_alerts()
        at_risk_list = engine.get_at_risk_countries()
        
        # 2. Process Conflict Data
        if os.path.exists(data_file):
            df = pd.read_csv(data_file)
            df.columns = [c.upper() for c in df.columns]
            current = df[df['YEAR'] == 2026].copy()
            current['NEXUS_SCORE'] = current.apply(calculate_nexus, axis=1)
            
            risk_map = current.set_index('ISO')['NEXUS_SCORE'].to_dict()
            stability = 100 - current['NEXUS_SCORE'].mean()
        else:
            print(f"⚠️ Conflict data missing. Using baseline stability.")
            risk_map = {}
            stability = 50.0

        # 3. Generate the Visual SITREP
        # We pass the friction map and the live alerts from your RSS feeds
        path = viz.generate_unified_intel(
            score=stability,
            at_risk=risk_map,
            friction=engine.get_port_friction_map(),
            alerts=[a['title'] for a in live_alerts],
            suffix="sofie_final"
        )
        
        print(f"\n=======================================================")
        print(f"📊 GLOBAL STABILITY: {stability:.2f}%")
        print(f"🌍 AT-RISK TRADE: {', '.join(at_risk_list[:3])}")
        print(f"✅ SITREP EXPORTED: {path}")
        print(f"=======================================================")

    except Exception as e:
        print(f"❌ Runtime Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
