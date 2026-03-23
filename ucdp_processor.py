import pandas as pd
import os
import glob

def run_ucdp_processing():
    print("🧠 SOFIE INTELLIGENCE: Ingesting UCDP Conflict Data...")
    
    raw_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Conflict\UCDP"
    output_dir = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed"
    
    extensions = ['*.csv', '*.xlsx']
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(raw_path, ext)))

    if not files:
        print(f"❌ ERROR: No UCDP files found in {raw_path}")
        return

    print(f"📂 Found {len(files)} UCDP files. Starting ingestion...")
    df_list = []
    
    for file in files:
        try:
            # 1. Load data without the invalid 'errors' keyword
            if file.endswith('.csv'):
                # Using encoding_errors for newer pandas, or standard fallback
                df = pd.read_csv(file, low_memory=False, encoding='utf-8', encoding_errors='replace')
            else:
                df = pd.read_excel(file)
            
            # 2. Flexible column mapping
            df.columns = [c.lower() for c in df.columns]
            col_list = list(df.columns)
            
            # Find YEAR
            year_col = next((k for k in ['year', 'year_id', 'active_year'] if k in col_list), None)
            # Find COUNTRY
            country_col = next((k for k in ['country', 'country_name', 'location', 'side_a'] if k in col_list), None)
            # Find FATALITIES
            fatality_col = next((k for k in ['best', 'deaths_total', 'fatality_count', 'best_fatality_estimate'] if k in col_list), None)

            if year_col and country_col and fatality_col:
                # Standardize to simulation window (2024+)
                df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
                # We include 2024 as the "Current State" baseline for the 2026 sim
                df = df[df[year_col] >= 2024].copy()
                
                if df.empty:
                    print(f"  - {os.path.basename(file)}: No data found for 2024-2026.")
                    continue

                # Group and rename to avoid collisions
                summary = df.groupby([country_col, year_col])[fatality_col].sum().to_frame()
                
                # Create a clean column name based on the file type
                clean_name = os.path.basename(file).split('_')[0].lower()
                summary.columns = [f"ucdp_{clean_name}_fatalities"]
                summary.index.names = ['country', 'year']
                
                df_list.append(summary)
                print(f"  + Ingested {os.path.basename(file)}: Found {len(summary)} records.")
            else:
                print(f"  - Skipping {os.path.basename(file)}: Missing columns. (Found: {col_list[:3]})")

        except Exception as e:
            print(f"  - Error processing {os.path.basename(file)}: {e}")

    if not df_list:
        print("❌ ERROR: No valid UCDP data could be extracted.")
        return

    # 3. Merge and calculate
    ucdp_master = pd.concat(df_list, axis=1).fillna(0)
    
    # Calculate Total Fatalities across all UCDP sources
    fatality_cols = [c for c in ucdp_master.columns if 'fatalities' in c]
    ucdp_master['total_fatalities'] = ucdp_master[fatality_cols].sum(axis=1)
    
    # Calculate Risk Index (normalized 0-100)
    # We use .max().max() or similar to ensure we get a scalar number
    global_max = ucdp_master['total_fatalities'].max()
    
    if global_max > 0:
        ucdp_master['ucdp_risk_index'] = (ucdp_master['total_fatalities'] / global_max * 100).round(2)
    else:
        ucdp_master['ucdp_risk_index'] = 0.0

    # 4. Save
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "ucdp_risk_indices.csv")
    ucdp_master.to_csv(output_file)
    
    print(f"\n✅ SUCCESS: UCDP Geopolitical Intelligence Online.")
    print(f"📍 Master Data: {output_file}")

if __name__ == "__main__":
    run_ucdp_processing()
