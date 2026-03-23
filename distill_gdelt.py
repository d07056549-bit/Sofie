import pandas as pd
import os

master_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Events\Gdelt\GDELT.MASTERREDUCEDV2.txt"
output_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\gdelt_historical_baseline.csv"

# THE MAGIC MAPPING:
# 0: Date, 2: CountryCode, 7: GoldsteinScale
col_map = {0: 'Date', 2: 'CountryCode', 7: 'GoldsteinScale'}

print("🚀 Distilling 88M Rows (Goldstein Impact Mode)...")

try:
    # Use 2.5M rows per chunk for speed
    chunks = pd.read_csv(
        master_path, sep='\t', header=None, 
        usecols=col_map.keys(), chunksize=2500000, low_memory=False,
        skiprows=1 # Skip the header line
    )

    processed_chunks = []

    for i, chunk in enumerate(chunks):
        chunk.columns = [col_map[c] for c in chunk.columns]
        
        # Numeric conversions
        chunk['Date'] = pd.to_numeric(chunk['Date'], errors='coerce')
        chunk['GoldsteinScale'] = pd.to_numeric(chunk['GoldsteinScale'], errors='coerce')
        
        # Filter for 2020+
        chunk = chunk.dropna(subset=['Date', 'CountryCode', 'GoldsteinScale'])
        chunk['Year'] = (chunk['Date'] // 10000)
        
        recent = chunk[chunk['Year'] >= 2020].copy()
        processed_chunks.append(recent[['CountryCode', 'GoldsteinScale']])
        
        print(f"   ...Processed {(i+1)*2.5:,.1f} Million rows")

    print("📊 Aggregating Deep Stability Memory...")
    df = pd.concat(processed_chunks)
    
    # Clean Country Codes
    df['CountryCode'] = df['CountryCode'].astype(str).str.strip().str.upper()
    df = df[df['CountryCode'] != ""]
    
    # Calculate average Goldstein per country
    stability = df.groupby('CountryCode')['GoldsteinScale'].mean()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    stability.to_csv(output_path)
    
    print(f"✅ MISSION SUCCESS! Baseline created for {len(stability)} countries.")

except Exception as e:
    print(f"❌ Error: {e}")
