import pandas as pd
import numpy as np
import os
from src.utils.visualizer import SofieVisualizer

def main():
    # 1. Initialization
    print("🚀 Initializing SOFIE Baseline Scenario...")
    visualizer = SofieVisualizer(output_path="outputs")
    
    # 2. Load Master Dataset
    try:
        df = pd.read_parquet('master.parquet')
        print(f"📊 Dataset Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    except Exception as e:
        print(f"❌ Failed to load master.parquet: {e}")
        return

    # 3. Define Baseline (Normalcy Period)
    # We define 'Baseline' as the average state of the world before 2024
    # We'll pull conflict (ACLED) and mobility data to define the 'tension'
    print("🛰️  Calculating Baseline Tension Scores...")
    
    # Identify conflict-related columns from your master_feature_list
    conflict_cols = [col for col in df.columns if 'FATALITIES' in col or 'EVENTS' in col]
    mobility_cols = [col for col in df.columns if 'mobility' in col]
    
    # Create a baseline snapshot (averaging values)
    baseline_df = df.mean().to_dict()

    # 4. Map Scenario Logic: 2100 Project
    # We pass the baseline data to the interactive engine
    print("🌍 Generating Interactive Tension Map (Folium Engine)...")
    
    # We send baseline_df as 'at_risk' to generate the heatmap
    interactive_path = visualizer.generate_interactive_nexus(
        at_risk=baseline_df, 
        friction={}, # Empty for baseline, used for $200 oil scenario later
        suffix="BASELINE_2100"
    )

    if interactive_path:
        print(f"✅ SUCCESS: Baseline Map saved to {interactive_path}")
    else:
        print("⚠️ Map generation failed. Check visualizer logs.")

    print("\n--- SITREP COMPLETE ---")

if __name__ == "__main__":
    main()
