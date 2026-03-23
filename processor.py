import pandas as pd
import os
import glob

def run_acled_processing():
    print("🧠 SOFIE INTELLIGENCE: Processing ACLED Conflict Data...")
    
    # This version looks in the current folder AND the subfolder
    search_patterns = [
        "number_of_*.csv",
        os.path.join("Data", "raw", "Conflict", "ACLED", "number_of_*.csv")
    ]
    
    files = []
    for pattern in search_patterns:
        files.extend(glob.glob(pattern))
    
    if not files:
        print("❌ ERROR: No ACLED 'number_of_' files found.")
        print("Please ensure your CSV files are in the same folder as this script.")
        return

    print(f"📂 Found {len(files)} files. Starting ingestion...")
    df_list = []
    
    for file in files:
        try:
            temp_df = pd.read_csv(file)
            # Filter for recent data (2025-2026)
            temp_df = temp_df[temp_df['YEAR'] >= 2025]
            
            # Identify metric type from filename
            metric = "fatality" if "fatality" in file.lower() else "event"
            # Get a clean name like 'demonstration' or 'political'
            parts = os.path.basename(file).split('_')
            subtype = parts[2] if len(parts) > 2 else "total"
            col_name = f"{metric}_{subtype}"
            
            if 'EVENTS' in temp_df.columns:
                temp_df = temp_df.rename(columns={'EVENTS': col_name})
            elif 'FATALITIES' in temp_df.columns:
                temp_df = temp_df.rename(columns={'FATALITIES': col_name})
                
            temp_df = temp_df.set_index(['COUNTRY', 'YEAR'])
            df_list.append(temp_df)
        except Exception as e:
            print(f"⚠️ Skipping {file} due to error: {e}")

    # Combine data
    acled_master = pd.concat(df_list, axis=1).fillna(0)
    
    # Calculate Risk Score
    fatality_cols = [c for c in acled_master.columns if 'fatality' in c]
    event_cols = [c for c in acled_master.columns if 'event' in c]
    
    acled_master['raw_score'] = (acled_master[event_cols].sum(axis=1) * 0.5) + \
                                (acled_master[fatality_cols].sum(axis=1) * 2.0)
    
    # Normalize 0-100
    max_score = acled_master['raw_score'].max()
    acled_master['conflict_index'] = (acled_master['raw_score'] / max_score * 100).round(2)
    
    # Ensure output directory exists
    output_dir = os.path.join("Data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "acled_risk_indices.csv")
    acled_master.to_csv(output_file)
    print(f"✅ SUCCESS: Master Index saved to {output_file}")

if __name__ == "__main__":
    run_acled_processing()
