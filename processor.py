import pandas as pd
import os
import glob

def run_acled_processing():
    print("🧠 SOFIE INTELLIGENCE: Processing ACLED Excel Data...")
    
    # Path where your .xlsx files are located
    raw_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Conflict\ACLED"
    output_dir = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed"
    
    # Search specifically for Excel files
    files = glob.glob(os.path.join(raw_path, "*.xlsx"))
    
    if not files:
        print(f"❌ ERROR: No Excel (.xlsx) files found in {raw_path}")
        return

    print(f"📂 Found {len(files)} Excel workbooks. Starting ingestion...")
    df_list = []
    
    for file in files:
        try:
            # Read the Excel file (assumes data is on the first sheet)
            temp_df = pd.read_excel(file)
            
            # Standardize column names
            temp_df.columns = [c.upper() for c in temp_df.columns]
            
            if 'YEAR' not in temp_df.columns or 'COUNTRY' not in temp_df.columns:
                print(f"  - Skipping {os.path.basename(file)}: Missing YEAR or COUNTRY columns.")
                continue

            # Filter for recent simulation data (2025-2026)
            temp_df = temp_df[temp_df['YEAR'] >= 2025]
            
            # Determine metric type and subtype from filename
            fname = os.path.basename(file).lower()
            metric = "FATALITY" if "fatalities" in fname else "EVENT"
            
            if "demonstration" in fname: subtype = "DEMO"
            elif "targeting_civilians" in fname: subtype = "CIVILIAN_TARGET"
            elif "political_violence" in fname: subtype = "POL_VIOLENCE"
            else: subtype = "GENERAL"
            
            col_name = f"{metric}_{subtype}"
            
            # Identify the data column
            data_col = 'EVENTS' if 'EVENTS' in temp_df.columns else 'FATALITIES'
            
            if data_col in temp_df.columns:
                temp_df = temp_df.rename(columns={data_col: col_name})
                temp_df = temp_df[['COUNTRY', 'YEAR', col_name]].set_index(['COUNTRY', 'YEAR'])
                df_list.append(temp_df)
                print(f"  + Ingested: {os.path.basename(file)}")
                
        except Exception as e:
            print(f"  - Error reading {os.path.basename(file)}: {e}")

    if not df_list:
        print("❌ ERROR: No valid data could be extracted from the Excel files.")
        return

    # Merge all regional and metric data
    acled_master = pd.concat(df_list, axis=1).fillna(0)
    
    # Calculate Risk Score (Weights: Fatalities 2.0, Events 0.5)
    f_cols = [c for c in acled_master.columns if 'FATALITY' in c]
    e_cols = [c for c in acled_master.columns if 'EVENT' in c]
    
    acled_master['RAW_SCORE'] = (acled_master[e_cols].sum(axis=1) * 0.5) + \
                                (acled_master[f_cols].sum(axis=1) * 2.0)
    
    # Normalize 0-100
    acled_master['conflict_index'] = (acled_master['RAW_SCORE'] / acled_master['RAW_SCORE'].max() * 100).round(2)
    
    # Save the final CSV for main.py
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "acled_risk_indices.csv")
    acled_master.to_csv(output_file)
    
    print(f"\n✅ SUCCESS: Geopolitical Master Index created.")
    print(f"📍 Location: {output_file}")

if __name__ == "__main__":
    run_acled_processing()
