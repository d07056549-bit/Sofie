import pandas as pd
import numpy as np
import argparse
import traceback
from src.utils.data_engine import DataEngine
from src.utils.visualizer import Visualizer
from src.utils.migration_engine import MigrationEngine 

# ==========================================
# 1. CORE LOGIC: THE QUAD-NEXUS FORMULA
# ==========================================
def calculate_nexus(row, displacement_map):
    """
    Calculates the 2026 Strategic Risk Score.
    Weights: 40% Conflict, 30% Market Sentiment, 30% Humanitarian Pressure.
    """
    try:
        # Pillar 1: Conflict (ACLED Hazard Index)
        hazard = float(row.get('HAZARD_INDEX', 0))
        
        # Pillar 2: Sentiment (Volatility Intensity)
        sentiment = abs(float(row.get('SENTIMENT_SCORE', 0)))
        
        # Pillar 3: Displacement (UNHCR Migration Data)
        iso_code = row.get('ISO', 'GLOBAL')
        country_name = row.get('COUNTRY', 'Unknown')
        
        # Check displacement_map using ISO first, then Name
        displacement = float(displacement_map.get(iso_code, displacement_map.get(country_name, 0)))
        
        # --- Weighted Aggregate ---
        nexus_base = (hazard * 0.4) + (sentiment * 0.3) + (displacement * 0.3)
        nexus_score = nexus_base * 100
        
        # Force Multiplier: High Conflict + High Displacement = Systemic Failure
        if hazard > 0.7 and displacement > 0.7:
            nexus_score = min(100.0, nexus_score * 1.1)
            
        return round(nexus_score, 2)
    except:
        return 0.0

# ==========================================
# 2. MAIN EXECUTION LOOP
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="SOFIE Evolved v2.0 | Strategic Intel Engine")
    parser.add_argument('--scenario', type=str, default='baseline', help='baseline or blackout')
    args = parser.parse_args()

    live_date = "March 23, 2026"
    print(f"\n--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: {live_date} | SCENARIO: {args.scenario.upper()}")
    print("=======================================================\n")

    # Initialize Components
    data_engine = DataEngine()
    visualizer = Visualizer()
    mig_engine = MigrationEngine() 
    
    try:
        # --- A. ENHANCED ISO & NAME MAPPING ---
        iso_fix = {
            'COD': 'Dem. Rep. Congo',
            'COG': 'Congo',
            'CAF': 'Central African Rep.',
            'SSD': 'S. Sudan',
            'CIV': "Côte d'Ivoire",
            'GNQ': 'Eq. Guinea',
            'LSO': 'Lesotho',
            'VNM': 'Vietnam',
            'PHL': 'Philippines',
            'USA': 'United States of America',
            'TUR': 'Turkey',
            'SYR': 'Syrian Arab Rep.',
            'VEN': 'Venezuela (Bolivarian Republic of)'
        }

        # --- B. PROCESSING STREAMS ---
        print(">>> ENGINE STARTING: Processing Global Streams...")
        maritime_data = data_engine.get_port_friction_map()
        market_stats = data_engine.get_market_baseline()
        displacement_map = mig_engine.get_displacement_risk()
        
        # Load Conflict Data
        acled_df = pd.read_csv("Data/processed/acled_risk_indices.csv")
        acled_df.columns = [c.upper() for c in acled_df.columns]
        
        # --- C. APPLY ISO BRIDGE ---
        name_to_iso = {v: k for k, v in iso_fix.items()}
        # If the CSV has a 'COUNTRY' column, map it to ISO
        if 'COUNTRY' in acled_df.columns:
            acled_df['ISO'] = acled_df['COUNTRY'].map(name_to_iso).fillna(acled_df['COUNTRY'])
        
        current_risks = acled_df[acled_df['YEAR'] == 2026].copy()

        # --- D. CALCULATE QUAD-NEXUS ---
        current_risks['NEXUS_SCORE'] = current_risks.apply(
            calculate_nexus, 
            axis=1, 
            args=(displacement_map,)
        )

        # Prepare data for Visualizer
        tension_map_data = current_risks.set_index('ISO')['NEXUS_SCORE'].to_dict()
        
        # --- E. SYSTEM STABILITY CALCULATION ---
        global_intensity = current_risks['NEXUS_SCORE'].mean()
        stability_score = max(0, 100 - (global_intensity * 1.2))
        
        print(f"✅ MARITIME SENSOR: Online")
        print(f"🌍 QUAD-NEXUS ONLINE: Global Intensity at {global_intensity:.2f}%")
        print(f"📊 MARKET BASELINE: Brent Oil @ ${market_stats['oil']} | Gold @ ${market_stats['gold']}")

        # --- F. GENERATE COMMAND SITREP ---
        file_suffix = f"{args.scenario}_{pd.Timestamp.now().strftime('%H%M')}"
        output_path = visualizer.generate_unified_intel(
            score=stability_score,
            at_risk=tension_map_data,
            friction=maritime_data,
            alerts=data_engine.get_live_port_alerts(),
            suffix=file_suffix
        )

        # --- G. LOGS & SUMMARY ---
        print(f"\n=======================================================")
        print(f"--- SITREP SUMMARY: {live_date.upper()} ---")
        status = "STABLE" if stability_score > 50 else "CRITICAL"
        print(f"STATUS: {status}. Stability Index: {stability_score:.2f}%")
        print(f"SITREP EXPORTED: {output_path}")
        print("=======================================================")
        print("--- RUN COMPLETE ---\n")

    except Exception as e:
        print(f"❌ SYSTEM CRITICAL ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
