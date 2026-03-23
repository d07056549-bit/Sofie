import pandas as pd
import os
import glob

def run_acled_processing():
    print("🧠 SOFIE INTELLIGENCE: Ingesting Regional & Summary Excel Data...")
    
    raw_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Conflict\ACLED"
    output_dir = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed"
    
    files = glob.glob(os.path.join(raw_path, "*.xlsx"))
    if not files:
        print(f"❌ ERROR: No Excel files found in {raw_path}")
        return

    df_list = []
    
    for file in files:
        try:
            # Load the Excel file
            df = pd.read_excel(file)
            df.columns = [c.upper() for c in df.columns]
            fname = os.path.basename(file).lower()

            # --- LOGIC A: Handle Regional Aggregated Files (WEEK column) ---
            if 'WEEK' in df.columns:
                # Convert WEEK string (e.g., '2026-03-07') to a YEAR integer
                df['YEAR'] = pd.to_datetime(df['WEEK']).dt.year
                print(f"  + Parsed Timeline for: {os.path.basename(file)}")

            # --- LOGIC B: Data Extraction ---
            if 'YEAR' in df.columns and 'COUNTRY' in df.columns:
                # Filter for current/near-future simulation years
                df = df[df['YEAR'] >= 2025]
                
                # Determine metric name
                metric_type = "FATALITIES" if "fatalities" in fname else "EVENTS"
                # Label based on file type
                if "africa" in fname: label = "AFRICA_RISK"
                elif "middle-east" in fname: label = "ME_RISK"
                elif "asia-pacific" in fname: label = "APAC_RISK"
                elif "europe" in fname: label = "EUR_RISK"
                elif "latin" in fname: label = "LATAM_RISK"
                elif "demonstration" in fname: label = "DEMO_RISK"
                else: label = "GEN_RISK"

                # Group data to ensure one row per country per year
                # We sum the values in case the regional file has multiple entries per country
                val_col = 'FATALITIES' if 'FATALITIES' in df.columns else 'EVENTS'
                summary = df.groupby(['COUNTRY', 'YEAR'])[val_col].sum().to_frame(label)
                
                df_list.append(summary)
                print(f"    - Successfully mapped {len(summary)} country nodes.")
            else:
                print(f"  - Skipping {os.path.basename(file)}: Missing critical columns.")

        except Exception as e:
            print(f"  - Error processing {os.path.basename(file)}: {e}")

    if not df_list:
        print("❌ ERROR: No data could be compiled.")
        return

    # Merge everything into one massive intelligence matrix
    # Using 'outer' join to keep all countries even if they only appear in one file
    master_intel = pd.concat(df_list, axis=1).fillna(0)

    # 📈 CALCULATE COMPOSITE CONFLICT INDEX
    # We weigh FATALITIES (Risk to Life) and EVENTS (Stability Friction)
    risk_cols = master_intel.columns
    master_intel['RAW_INTEL_SCORE'] = master_intel[risk_cols].sum(axis=1)
    
    # Normalize to 0-100 scale
    max_val = master_intel['RAW_INTEL_SCORE'].max()
    master_intel['conflict_index'] = (master_intel['RAW_INTEL_SCORE'] / max_val * 100).round(2)

    # Save to Processed folder
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "acled_risk_indices.csv")
    master_intel.to_csv(output_file)
    
    print(f"\n✅ SUCCESS: Integrated Geopolitical Intelligence Online.")
    print(f"📍 Master Data: {output_file}")

if __name__ == "__main__":
    run_acled_processing()
