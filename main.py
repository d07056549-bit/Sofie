import sys
import os
import pandas as pd
import numpy as np
import argparse
import traceback

# --- 1. THE MODULE PATH FIXER ---
# This forces Python to look in your Sofie folder for the 'src' folder
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now we try the imports
try:
    from src.utils.data_engine import DataEngine
    from src.utils.visualizer import Visualizer
    from src.utils.migration_engine import MigrationEngine 
except ModuleNotFoundError:
    print("❌ ERROR: Could not find the 'src' folder.")
    print(f"Looked in: {project_root}")
    print("Make sure you are running the command from: C:\\Users\\Empok\\Documents\\GitHub\\Sofie")
    sys.exit(1)

# --- 2. THE QUAD-NEXUS LOGIC ---
def calculate_nexus(row, displacement_map):
    """
    Calculates the 2026 Strategic Risk Score.
    40% Conflict | 30% Sentiment | 30% Displacement
    """
    try:
        # Pillar 1: Conflict (Hazard Index)
        hazard = float(row.get('HAZARD_INDEX', 0))
        
        # Pillar 2: Sentiment (Volatility)
        sentiment = abs(float(row.get('SENTIMENT_SCORE', 0)))
        
        # Pillar 3: Displacement (Humanitarian)
        iso_code = row.get('ISO', 'GLOBAL')
        country_name = row.get('COUNTRY', 'Unknown')
        
        # Lookup in displacement map (from MigrationEngine)
        displacement = float(displacement_map.get(iso_code, displacement_map.get(country_name, 0)))
        
        # Weighted Score Calculation
        nexus_base = (hazard * 0.4) + (sentiment * 0.3) + (displacement * 0.3)
        nexus_score = nexus_base * 100
        
        # Force Multiplier: High Conflict + High Displacement
        if hazard > 0.7 and displacement > 0.7:
            nexus_score = min(100.0, nexus_score * 1.1)
            
        return round(nexus_score, 2)
    except Exception:
        return 0.0

# --- 3. MAIN EXECUTION ---
def main():
    parser = argparse.ArgumentParser(description="SOFIE Evolved v2.0")
    parser.add_argument('--scenario', type=str, default='baseline', help='baseline or blackout')
    args = parser.parse_args()

    print(f"\n--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: March 23, 2026 | SCENARIO: {args.scenario.upper()}")
    print("=======================================================\n")

    # Initialize Components
    data_engine = DataEngine()
    visualizer = Visualizer()
    mig_engine = MigrationEngine() 
    
    try:
        # A. Load Mapping Overrides
        iso_fix = {
            'COD': 'Dem. Rep. Congo', 'CAF': 'Central African Rep.',
            'SSD': 'S. Sudan', 'VNM': 'Vietnam', 'PHL': 'Philippines',
            'USA': 'United States of America', 'TUR': 'Turkey',
            'SYR': 'Syrian Arab Rep.', 'VEN': 'Venezuela (Bolivarian Republic of)'
        }

        print(">>> ENGINE STARTING: Processing Global Streams...")
        
        # B. Load Streams
        maritime_data = data_engine.get_port_friction_map()
        market_stats = data_engine.get_market_baseline()
        displacement_map = mig_engine.get_displacement_risk()
        
        # C. Process Conflict Data
        acled_df = pd.read_csv("Data/processed/acled_risk_indices.csv")
        acled_df.columns = [c.upper() for c in acled_df.columns]
        
        # Apply Mapping Fix
        name_to_iso = {v: k for k, v in iso_fix.items()}
        if 'COUNTRY' in acled_df.columns:
            acled_df['ISO'] = acled_df['COUNTRY'].map(name_to_iso).fillna(acled_df['COUNTRY'])
        
        current_risks = acled_df[acled_df['YEAR'] == 2026].copy()

        # D. Calculate Quad-Nexus
        current_risks['NEXUS_SCORE'] = current_risks.apply(
            calculate_nexus, 
            axis=1, 
            args=(displacement_map,)
        )

        tension_map_data = current_risks.set_index('ISO')['NEXUS_SCORE'].to_dict()
        
        # E. System Stability Calculation
        global_intensity = current_risks['NEXUS_SCORE'].mean()
        stability_score = max(0, 100 - (global_intensity * 1.2))
        
        print(f"✅ MARITIME SENSOR: Online")
        print(f"🌍 QUAD-NEXUS ONLINE: Global Intensity at {global_intensity:.2f}%")
        print(f"📊 MARKET BASELINE: Brent Oil @ ${market_stats['oil']} | Gold @ ${market_stats['gold']}")

        # F. Generate Export
        file_suffix = f"{args.scenario}_{pd.Timestamp.now().strftime('%H%M')}"
        output_path = visualizer.generate_unified_intel(
            score=stability_score, 
            at_risk=tension_map_data,
            friction=maritime_data, 
            alerts=data_engine.get_live_port_alerts(),
            suffix=file_suffix
        )

        print(f"\n=======================================================")
        print(f"--- SITREP SUMMARY: MARCH 23, 2026 ---")
        status = "STABLE" if stability_score > 50 else "CRITICAL"
        print(f"STATUS: {status}. Stability Index: {stability_score:.2f}%")
