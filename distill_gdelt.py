import pandas as pd
import os

master_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Events\Gdelt\GDELT.MASTERREDUCEDV2.txt"
output_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\gdelt_historical_baseline.csv"

# The 17-column "Analyst" mapping
# We use SQLDATE (YYYYMMDD) at Index 0 to get the Year
# We use Actor1CountryCode at Index 4
# We use GoldsteinScale at Index 9
col_map = {0: 'Date', 4: 'CountryCode', 9: 'GoldsteinScale'}

print("⏳ Distilling 17-Column Reduced GDELT File...")

try:
    # 1. Read the file with the 17-column mapping
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
        
        # Convert YYYYMMDD to just the Year
        chunk['Year'] = (chunk['Date'] // 10000)
        
        # Filter for recent history (2020+)
        recent = chunk[chunk['Year'] >= 2020].copy()
        processed_chunks.append(recent[['CountryCode', 'GoldsteinScale']])
        
        if i % 4 == 0:
            print(f"   ...Processed {i*250000:,} rows")

    print("📊 Aggregating Historical Stability per Country...")
    df = pd.concat(processed_chunks)
    
    # Drop rows where country code or goldstein is missing
    df = df.dropna(subset=['CountryCode', 'GoldsteinScale'])
    
    # Calculate average stability baseline
    stability_lookup = df.groupby('CountryCode')['GoldsteinScale'].mean()

    # Save the small reference file
    stability_lookup.to_csv(output_path)
    print(f"✅ SUCCESS! Created baseline for {len(stability_lookup)} countries.")
    print(f"📍 Baseline saved to: {output_path}")

except Exception as e:
    print(f"❌ Error: {e}")
