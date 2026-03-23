import pandas as pd
import os

master_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Events\Gdelt\GDELT.MASTERREDUCEDV2.txt"
output_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\gdelt_historical_baseline.csv"

# The mapping we discovered: 0=Date, 2=CountryCode, 7=GoldsteinScale
col_map = {0: 'Date', 2: 'CountryCode', 7: 'GoldsteinScale'}

print("🚀 Distilling 88M Rows (History Baseline Mode)...")

try:
    # Use 5M rows per chunk to finish faster
    chunks = pd.read_csv(
        master_path, 
        sep='\t', 
        header=None, 
        usecols=col_map.keys(), 
        chunksize=5000000, 
        low_memory=False,
        skiprows=1  # This skips the word "Date" so the math doesn't crash
    )

    processed_chunks = []

    for i, chunk in enumerate(chunks):
        chunk.columns = [col_map[c] for c in chunk.columns]
        
        # 1. Force everything to numbers (non-numbers become NaN)
        chunk['GoldsteinScale'] = pd.to_numeric(chunk['GoldsteinScale'], errors='coerce')
        
        # 2. Cleanup: Drop missing data
        chunk = chunk.dropna(subset=['CountryCode', 'GoldsteinScale'])
        
        # 3. Only keep real country codes (2-3 characters)
        chunk = chunk[chunk['CountryCode'].astype(str).str.len().between(2, 3)]
        
        # 4. Store this chunk's processed data
        processed_chunks.append(chunk[['CountryCode', 'GoldsteinScale']])
        
        print(f"   ...Processed {(i+1)*5} Million rows")

    print("📊 Aggregating all 88 Million rows into a single baseline...")
    df = pd.concat(processed_chunks)
    
    # Final aggregation: Average Goldstein score per country
    stability = df.groupby('CountryCode')['GoldsteinScale'].mean()

    if len(stability) == 0:
        print("❌ Error: Aggregated data is empty. Check if Index 2 is truly the Country Code.")
    else:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        stability.to_csv(output_path)
        print(f"✅ MISSION SUCCESS! Baseline created for {len(stability)} countries.")

except Exception as e:
    print(f"❌ Error during distillation: {e}")
