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
            # 1. Load data
            if file.endswith('.csv'):
                df = pd.read_csv(file, low_memory=False, encoding='utf-8', errors='replace')
            else:
                df = pd.read_excel(file)
            
            # 2. Flexible column mapping
            col_map = {c.lower(): c for c in df.columns}
            
            # Find YEAR
            year_col = next((col_map[k] for k in ['year', 'year_id', 'active_year'] if k in col_map), None)
            # Find COUNTRY
            country_col = next((col_map[k] for k in ['country', 'country_name', 'location', 'side_a'] if k in col_map), None)
            # Find FATALITIES (UCDP 'best' is the standard)
            fatality_col = next((col_map[k] for k in ['best', 'deaths_total', 'fatality_count', 'best_fatality_estimate'] if k in col_map), None)

            if year_col and country_col and fatality_col:
                # Standardize to simulation window (2024+)
                df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
                df = df[df[year_col] >= 2024].copy()
                
                if df.empty:
                    print(f"  - Ingested {os.path.basename(file)}: No data for 2024-2026.")
                    continue

                # Group and rename to avoid collisions
                summary = df.groupby([country_col, year_col])[fatality_col].sum().to_frame()
                summary.columns = [f"fatalities_{os.path.basename(file)[:10]}"]
                summary.index.names = ['country', 'year']
                
                df_list.append(summary)
                print(f"  + Ingested {os.path.basename(file)}: Found {len(summary)} records.")
            else:
                print(f"  - Skipping {os.path.basename(file)}: Missing critical columns (Found: {list(df.columns)[:5]}...)")

        except Exception as e:
            print(f"  - Error processing {os.path.basename(file)}: {e}")

    if not df_list:
        print("❌ ERROR: No valid UCDP data could be extracted.")
        return

    # 3. Merge and calculate
    # Outer join to capture all countries across all files
    ucdp_master = pd.concat(df_list, axis=1).fillna(0)
    
    # Sum all the different fatality columns into one total
    ucdp_master['total_fatalities'] = ucdp_master.sum(axis=1)
    
    # Calculate Risk Index using the global max as the ceiling
    max_f = ucdp_master['total_fatalities'].max()
    
    if max_f > 0:
        ucdp_master['ucdp_risk_index'] = (ucdp_master['total_fatalities'] / max_f * 100).round(2)
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
