import pandas as pd
import os
import glob

def run_ucdp_processing():
    print("🧠 SOFIE INTELLIGENCE: Ingesting UCDP Conflict Data...")
    
    raw_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Conflict\UCDP"
    output_dir = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed"
    
    # Search for both CSV and Excel
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
            # Loader logic based on extension
            if file.endswith('.csv'):
                df = pd.read_csv(file, low_memory=False)
            else:
                df = pd.read_excel(file)
            
            df.columns = [c.lower() for c in df.columns]
            
            # Standard UCDP Columns are usually 'year' and 'country' or 'side_a'/'side_b'
            # We look for 'year' and 'country'
            if 'year' in df.columns and 'country' in df.columns:
                # Filter for recent simulation years
                df = df[df['year'] >= 2024]
                
                # UCDP Fatality columns: 'best' is the most reliable estimate
                # We use 'best' fatalities if available, otherwise 'deaths_total'
                val_col = None
                for col in ['best', 'deaths_total', 'fatality_count']:
                    if col in df.columns:
                        val_col = col
                        break
                
                if val_col:
                    # Group and Sum
                    summary = df.groupby(['country', 'year'])[val_col].sum().to_frame('ucdp_fatalities')
                    df_list.append(summary)
                    print(f"  + Ingested {os.path.basename(file)}: Found {len(summary)} data points.")
                else:
                    print(f"  - Skipping {os.path.basename(file)}: No fatality columns found.")
            else:
                print(f"  - Skipping {os.path.basename(file)}: Missing 'year' or 'country' columns.")

        except Exception as e:
            print(f"  - Error processing {os.path.basename(file)}: {e}")

    if not df_list:
        print("❌ ERROR: No valid UCDP data extracted.")
        return

    # Merge UCDP data
    ucdp_master = pd.concat(df_list, axis=1).fillna(0)
    
    # Calculate UCDP Risk Index (0-100)
    max_fatalities = ucdp_master['ucdp_fatalities'].max()
    if max_fatalities > 0:
        ucdp_master['ucdp_risk_index'] = (ucdp_master['ucdp_fatalities'] / max_fatalities * 100).round(2)
    else:
        ucdp_master['ucdp_risk_index'] = 0

    # Save to Processed folder
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "ucdp_risk_indices.csv")
    ucdp_master.to_csv(output_file)
    
    print(f"\n✅ SUCCESS: UCDP Geopolitical Intelligence Online.")
    print(f"📍 Master Data: {output_file}")

if __name__ == "__main__":
    run_ucdp_processing()
