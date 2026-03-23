import pandas as pd
import os
import glob

def run_acled_processing():
    print("🧠 SOFIE INTELLIGENCE: Processing ACLED Conflict Data...")
    
    # Path where you put the ACLED files
    raw_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Conflict\ACLED"
    output_dir = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed"
    
    # Find all the 'number_of...' summary files
    files = glob.glob(os.path.join(raw_path, "number_of_*.csv"))
    
    if not files:
        print(f"❌ ERROR: No ACLED files found in {raw_path}")
        return

    df_list = []
    for file in files:
        temp_df = pd.read_csv(file)
        # We only care about current simulation years
        temp_df = temp_df[temp_df['YEAR'] >= 2025]
        
        # Determine if it's a fatality or event count
        metric = "fatality" if "fatality" in file.lower() else "event"
        # Extract a clean subtype name from the filename
        subtype = os.path.basename(file).split('_')[2]
        col_name = f"{metric}_{subtype}"
        
        # Rename columns to be specific to this file's data
        if 'EVENTS' in temp_df.columns:
            temp_df = temp_df.rename(columns={'EVENTS': col_name})
        if 'FATALITIES' in temp_df.columns:
            temp_df = temp_df.rename(columns={'FATALITIES': col_name})
            
        temp_df = temp_df.set_index(['COUNTRY', 'YEAR'])
        df_list.append(temp_df)

    # Combine all data into one master sheet
    acled_master = pd.concat(df_list, axis=1).fillna(0)
    
    # Calculate Risk (Fatalities weighted 4x higher than demonstration events)
    fatality_cols = [c for c in acled_master.columns if 'fatality' in c]
    event_cols = [c for c in acled_master.columns if 'event' in c]
    
    acled_master['raw_score'] = (acled_master[event_cols].sum(axis=1) * 0.5) + \
                                (acled_master[fatality_cols].sum(axis=1) * 2.0)
    
    # Normalize 0-100 (Ukraine usually sets the 100 benchmark)
    acled_master['conflict_index'] = (acled_master['raw_score'] / acled_master['raw_score'].max() * 100).round(2)
    
    # Save to the folder main.py is looking at
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "acled_risk_indices.csv")
    acled_master.to_csv(output_file)
    print(f"✅ SUCCESS: Master Conflict Index created at {output_file}")

if __name__ == "__main__":
    run_acled_processing()
