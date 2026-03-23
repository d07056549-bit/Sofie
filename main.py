import sys
import os
import importlib.util
import pandas as pd
import argparse

# --- 1. DYNAMIC PATH CONFIGURATION ---
BASE_DIR = r"C:\Users\Empok\Documents\GitHub\Sofie"
# Ensure the project root is in the search path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def import_module_manually(name, folder):
    """Bypasses Python's import system to load files directly from disk."""
    path = os.path.join(BASE_DIR, "src", folder, f"{name}.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing component: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    # Load your specific utilities
    dp_mod = import_module_manually("data_processor", "utils")
    vi_mod = import_module_manually("visualizer", "utils")
    
    # Connect to your specific class names
    DataEngineClass = getattr(dp_mod, 'SofieDataEngine', None)
    VisualizerClass = getattr(vi_mod, 'Visualizer', None)
    
    if not DataEngineClass:
        print("❌ Error: Could not find 'SofieDataEngine' in data_processor.py")
        sys.exit(1)
        
    print("✅ System Core: SofieDataEngine & Visualizer Linked")
except Exception as e:
    print(f"❌ Structural Error: {e}")
    sys.exit(1)

# --- 2. RISK LOGIC ---
def calculate_nexus(row):
    """
    Calculates the 2026 Strategic Risk. 
    Uses 'conflict_index' as the primary hazard pillar.
    """
    try:
        # Based on your CSV snippet: conflict_index is the target
        hazard = float(row.get('CONFLICT_INDEX', row.get('conflict_index', 0)))
        # For baseline, we use the hazard as the nexus base (0-100 scale)
        return round(hazard * 100, 2)
    except:
        return 0.0

# --- 3. MAIN COMMAND CENTER ---
def main():
    parser = argparse.ArgumentParser(description="SOFIE Evolved v2.0")
    parser.add_argument('--scenario', type=str, default='baseline')
    args = parser.parse_args()

    print(f"\n--- SOFIE EVOLVED v2.0 | MARCH 2026 ---")
    print(f"SCENARIO: {args.scenario.upper()}")
    print(f"ROOT: {BASE_DIR}")

    # Initialize your Engine and Visualizer
    engine = DataEngineClass(root_dir=BASE_DIR)
    viz = VisualizerClass()
    
    # Correct path to your processed risk indices
    risk_data_path = os.path.join(BASE_DIR, "Data", "processed", "acled_risk_indices.csv")
    
    try:
        # A. Trigger the Maritime Sensor Suite (RSS feeds + Port CSV)
        maritime_intel = engine.run_all()
        live_alerts = engine.get_live_port_alerts()
        trade_exposure = engine.get_at_risk_countries()
        
        # B. Process Conflict & Stability
        if os.path.exists(risk_data_path):
            df = pd.read_csv(risk_data_path)
            # Standardize columns to uppercase for easier lookup
            df.columns = [c.upper() for c in df.columns]
            
            # Filter for the 2026 projection
            current_risks = df[df['YEAR'] == 2026].copy()
            current_risks['NEXUS_SCORE'] = current_risks.apply(calculate_nexus, axis=1)
            
            # Create the tension map data for the visualizer
            risk_map = current_risks.set_index('COUNTRY')['NEXUS_SCORE'].to_dict()
            
            # Calculate Global Stability Index
            avg_risk = current_risks['NEXUS_SCORE'].mean()
            stability_score = max(0, 100 - avg_risk)
        else:
            print(f"⚠️ Conflict data missing at {risk_data_path}. Using maritime baseline.")
            risk_map = {}
            stability_score = 50.0

        # C. Generate the Unified Intelligence Export
        # Extract titles from your RSS alert dictionaries
        alert_titles = [a['title'] for a in live_alerts if isinstance(a, dict)]
        if not alert_titles: alert_titles = ["System Online: No Critical Alerts"]

        export_path = viz.generate_unified_intel(
            score=stability_score,
            at_risk=risk_map,
            friction=engine.get_port_friction_map(),
            alerts=alert_titles,
            suffix=f"{args.scenario}_
