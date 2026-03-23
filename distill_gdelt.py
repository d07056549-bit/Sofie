import pandas as pd
import os

# Paths
master_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Events\Gdelt\GDELT.MASTERREDUCEDV2.txt"
output_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\gdelt_historical_baseline.csv"

# Standard GDELT Event Columns (Simplified for what we need)
# We map the index positions to the names we want
col_map = {
    3: 'Year',
    30: 'GoldsteinScale',
    34: 'CountryCode' # ActionGeo_CountryCode is usually column 34 or 53
}

os.makedirs(os.path.dirname(output_path), exist_ok=True)

print("⏳ Distilling Master GDELT File (No-Header Mode)...")

try:
    # We read without headers (header=None) and use integer indices
    chunks = pd.read_csv(
        master_path, 
        sep='\t', 
        header=None,
        usecols=col_map.keys(),
        chunksize=200000,
        low_memory=False
    )

    processed_chunks = []
    for i, chunk in enumerate(chunks):
        # Rename columns to friendly names
        chunk.columns = [col_map[c] for c in chunk.columns]
        
        # Filter for recent years
        recent = chunk[chunk['Year'] >= 2022] # Using 2022+ for a better baseline
        processed_chunks.append(recent)
        
        if i % 5 == 0:
            print(f"   ...Processed {i*200000:,} rows")

    print("📊 Aggregating data...")
    df = pd.concat(processed_chunks)
    
    # Calculate average stability (Goldstein) per country
    stability_lookup = df.groupby('CountryCode')['GoldsteinScale'].mean()

    # Save
    stability_lookup.to_csv(output_path)
    print(f"✅ SUCCESS! Created baseline at: {output_path}")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 TIP: If you get a 'Tokenization Error', the file might be comma-separated despite the .txt extension. Try changing sep='\\t' to sep=',' in the code.")
