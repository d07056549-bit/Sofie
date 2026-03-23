import pandas as pd
import os

# Paths
master_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Events\Gdelt\GDELT.MASTERREDUCEDV2.txt"
output_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\gdelt_historical_baseline.csv"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

print("⏳ Distilling Master GDELT File (this may take a minute)...")

try:
    # We use chunksize because GDELT files are often multi-gigabyte
    # This reads 100,000 lines at a time so your RAM doesn't explode
    chunks = pd.read_csv(
        master_path, 
        sep='\t', 
        usecols=['Year', 'ActionGeo_CountryCode', 'GoldsteinScale'],
        chunksize=100000,
        low_memory=False
    )

    processed_chunks = []
    for i, chunk in enumerate(chunks):
        # Filter for recent years only
        recent = chunk[chunk['Year'] >= 2024]
        processed_chunks.append(recent)
        if i % 10 == 0:
            print(f"   ...Processed {i} chunks")

    # Combine the filtered chunks
    df = pd.concat(processed_chunks)

    # Group by country to get their 'Historical Stability Average'
    # Goldstein Scale: -10 (Conflict/War) to +10 (Peace/Cooperation)
    stability_lookup = df.groupby('ActionGeo_CountryCode')['GoldsteinScale'].mean()

    # Save the lightweight version
    stability_lookup.to_csv(output_path)
    print(f"✅ Created local stability baseline at: {output_path}")

except Exception as e:
    print(f"❌ Error distilling GDELT file: {e}")
