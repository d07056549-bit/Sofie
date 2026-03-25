import pandas as pd
import numpy as np
import os
from src.utils.visualizer import SofieVisualizer

def main():
    print("🚀 INITIALIZING SOFIE STRATEGIC ENGINE...")
    
    # 1. Setup Paths
    # Updated to the directory you provided
    parquet_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\master\master.parquet"
    output_dir = "outputs"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    visualizer = SofieVisualizer(output_path=output_dir)
    
    # 2. Load Master Data
    try:
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Could not find parquet at: {parquet_path}")
            
        print(f"📊 Loading Master Dataset from: {parquet_path}")
        df = pd.read_parquet(parquet_path)
        print(f"✅ Data Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    except Exception as e:
        print(f"❌ Data Error: {e}")
        return

    # 3. Coordinate Mapping for ACLED Regions
    # This maps your 1,280 features to geographic points
    region_coords = {
        'acled_africa': [1.0, 17.0],
        'acled_middle_east': [29.0, 43.0],
        'acled_asia_pacific': [15.0, 120.0],
        'acled_europe_central_asia': [48.0, 68.0],
        'acled_latin_america_the_caribbean': [-15.0, -60.0],
        'acled_us_and_canada': [45.0, -100.0]
    }

    # 4. Calculate Baseline Tension
    print("🛰️  Analyzing Baseline Tension (ACLED Fatalities)...")
    at_risk_data = {}
    
    for region, coords in region_coords.items():
        col_name = f"{region}_FATALITIES"
        if col_name in df.columns:
            # We take the mean of fatalities to establish the baseline 'glow'
            avg_tension = df[col_name].mean()
            at_risk_data[region] = {
                'lat': coords[0],
                'lon': coords[1],
                'risk_score': float(avg_tension)
            }

    # 5. Generate Interactive Map
    print("🌍 Rendering Interactive Global Tension Map...")
    map_path = visualizer.generate_interactive_nexus(
        at_risk=at_risk_data,
        friction={}, 
        suffix="BASELINE_2100"
    )

    if map_path:
        print(f"\n✨ BASELINE SUCCESSFUL ✨")
        print(f"🔗 View Map: {os.path.abspath(map_path)}")
    else:
        print("⚠️ Map generation failed. Check visualizer.py syntax.")

if __name__ == "__main__":
    main()
