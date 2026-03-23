import pandas as pd
import os
import glob

def process_acled_intelligence(raw_dir="Data/raw/Conflict/ACLED"):
    """
    Ingests 10+ ACLED CSVs and generates a master Conflict Risk Index.
    """
    print("🧠 SOFIE INTELLIGENCE: Processing ACLED Conflict Data...")
    
    # 1. Load Summary Files (Fatalities, Events, etc.)
    summary_files = glob.glob(os.path.join(raw_dir, "number_of_*.csv"))
    df_list = []

    for file in summary_files:
        temp_df = pd.read_csv(file)
        # Filter for the most recent timeline (2025-2026)
        temp_df = temp_df[temp_df['YEAR'] >= 2025]
        
        # Create unique metric names based on file content
        metric = "fatality" if "fatality" in file.lower() else "event"
        subtype = file.split('_')[2] 
        col_name = f"{metric}_{subtype}"
        
        temp_df = temp_df.rename(columns={'EVENTS': col_name, 'FATALITIES': col_name})
        temp_df = temp_df.set_index(['COUNTRY', 'YEAR'])
        df_list.append(temp_df)

    # 2. Merge into a Master Geopolitical DataFrame
    if not df_list:
        print("⚠️ No ACLED files found in the specified directory.")
        return None

    acled_master = pd.concat(df_list, axis=1).fillna(0)
    
    # 3. Calculate Composite Risk Score (Weighted)
    # Fatalities weigh 4x more than standard demonstration events
    fatality_cols = [c for c in acled_master.columns if 'fatality' in c]
    event_cols = [c for c in acled_master.columns if 'event' in c]
    
    acled_master['total_fatality_score'] = acled_master[fatality_cols].sum(axis=1)
    acled_master['total_event_score'] = acled_master[event_cols].sum(axis=1)
    
    # Formula: Risk = (Events * 0.5) + (Fatalities * 2.0)
    acled_master['raw_score'] = (acled_master['total_event_score'] * 0.5) + (acled_master['total_fatality_score'] * 2.0)
    
    # Normalize to 0-100 scale based on the most volatile region (likely Ukraine)
    max_val = acled_master['raw_score'].max()
    acled_master['conflict_index'] = (acled_master['raw_score'] / max_val * 100).round(2)
    
    # 4. Save for SOFIE Engine
    output_path = "Data/processed/acled_risk_indices.csv"
    os.makedirs("Data/processed", exist_ok=True)
    acled_master.to_csv(output_path)
    
    print(f"✅ SUCCESS: {len(acled_master)} country-year records processed.")
    print(f"📊 TOP RISK NODES: {acled_master.sort_values('conflict_index', ascending=False).index[0]}")
    return output_path

if __name__ == "__main__":
    process_acled_intelligence()
