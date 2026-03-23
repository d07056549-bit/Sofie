import pandas as pd
import os
import glob

def run_acled_processing():
    print("🧠 SOFIE INTELLIGENCE: Processing ACLED Conflict Data...")
    
    # Define potential paths where the data might be
    possible_paths = [
        ".",  # Current folder
        os.path.join("Data", "raw", "Conflict", "ACLED") # Standard SOFIE path
    ]
    
    # Search for any CSV file containing these keywords from your uploads
    keywords = ['number_of', 'fatalities', 'events', 'aggregated']
    files = []
    
    for path in possible_paths:
        if os.path.exists(path):
            all_csvs = glob.glob(os.path.join(path, "*.csv"))
            for f in all_csvs:
                if any(key in f.lower() for key in keywords):
                    files.append(f)
    
    # Remove duplicates
    files = list(set(files))

    if not files:
        print("❌ ERROR: No matching ACLED CSV files found.")
        print(f"Current Directory: {os.getcwd()}")
        print("Files present:", os.listdir('.')[:10]) # Show first 10 files for debugging
        return

    print(f"📂 Found {len(files)} relevant data files. Starting ingestion...")
    df_list = []
    
    for file in files:
        try:
            temp_df = pd.read_csv(file)
            # Standardize column names to uppercase for consistency
            temp_df.columns = [c.upper() for c in temp_df.columns]
            
            if 'YEAR' not in temp_df.columns or 'COUNTRY' not in temp_df.columns:
                continue

            # Filter for recent data (2025-2026)
            temp_df = temp_df[temp_df['YEAR'] >= 2025]
            
            # Determine metric type
            metric = "FATALITY" if "FATALITY" in "".join(temp_df.columns) else "EVENT"
            filename = os.path.basename(file).lower()
            subtype = "total"
            if "civilian" in filename: subtype = "civilian"
            elif "political" in filename: subtype = "political"
            elif "demonstration" in filename: subtype = "demonstration"
            
            col_name = f"{metric}_{subtype.upper()}"
            
            # Identify data column (usually EVENTS or FATALITIES)
            data_col = next((c for c in ['EVENTS', 'FATALITIES'] if c in temp_df.columns), None)
            if data_col:
                temp_df = temp_df.rename(columns={data_col: col_name})
                temp_df = temp_df[['COUNTRY', 'YEAR', col_name]].set_index(['COUNTRY', 'YEAR'])
                df_list.append(temp_df)
                
        except Exception as e:
            print(f"⚠️ Skipping {file}: {e}")

    if not df_list:
        print("❌ ERROR: Could not extract valid conflict metrics from the files.")
        return

    # Combine data
    acled_master = pd.concat(df_list, axis=1).fillna(0)
    
    # Calculate Risk Score
    # We prioritize Fatalities (weight 2.0) over Events (weight 0.5)
    f_cols = [c for c in acled_master.columns if 'FATALITY' in c]
    e_cols = [c for c in acled_master.columns if 'EVENT' in c]
    
    acled_master['RAW_SCORE'] = (acled_master[e_cols].sum(axis=1) * 0.5) + \
                                (acled_master[f_cols].sum(axis=1) * 2.0)
    
    # Normalize 0-100
    max_score = acled_master['RAW_SCORE'].max()
    acled_master['conflict_index'] = (acled_master['RAW_SCORE'] / max_score * 100).round(2)
    
    # Save to the processed folder
    output_dir = os.path.join("Data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "acled_risk_indices.csv")
    
    acled_master.to_csv(output_file)
    print(f"✅ SUCCESS: Geopolitical Master Index created at {output_file}")

if __name__ == "__main__":
    run_acled_processing()
