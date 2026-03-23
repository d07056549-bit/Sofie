import pandas as pd
import os

master_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Events\Gdelt\GDELT.MASTERREDUCEDV2.txt"
output_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\gdelt_historical_baseline.csv"

# The 17-column "Analyst" mapping
col_map = {0: 'Date', 4: 'CountryCode', 9: 'GoldsteinScale'}

print("⏳ Distilling 17-Column Reduced GDELT File...")

try:
    # 1. Read the file
    chunks = pd.read_csv(
        master_path, 
        sep='\t', 
        header=None, 
        usecols=col_map.keys(),
        chunksize=250000,
        low_memory=False
    )

    processed_chunks = []
    for i, chunk in enumerate(chunks):
        chunk.columns = [col_map[c] for c in chunk.columns]
        
        # --- FIX: Convert to numeric, skipping errors ---
        chunk['Date'] = pd.to_numeric(chunk['Date'], errors='coerce')
        chunk['GoldsteinScale'] = pd.to_numeric(chunk['GoldsteinScale'], errors='coerce')
        
        # Remove any rows that failed conversion
        chunk = chunk.dropna(subset=['Date', 'GoldsteinScale'])
        
        # Convert YYYYMMDD to just the Year
        chunk['Year'] = (chunk['Date'] // 10000).astype(int)
        
        # Filter for recent history (2020+)
        recent = chunk[chunk['Year'] >= 2020].copy()
        processed_chunks.append(recent[['CountryCode', 'GoldsteinScale']])
        
        if i % 4 == 0:
            print(f"   ...Processed {i*250000:,} rows")

    print("📊 Aggregating Historical Stability per Country...")
    df = pd.concat(processed_chunks)
    
    # Calculate average stability baseline
    stability_lookup = df.groupby('CountryCode')['GoldsteinScale'].mean()

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    stability_lookup.to_csv(output_path)
    print(f"✅ SUCCESS! Created baseline for {len(stability_lookup)} countries.")

except Exception as e:
    print(f"❌ Error: {e}")
