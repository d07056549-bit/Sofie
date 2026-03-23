import pandas as pd
import os

master_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Events\Gdelt\GDELT.MASTERREDUCEDV2.txt"
output_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\gdelt_historical_baseline.csv"

# Based on your peek: 
# 0 is Date, 4 is NumEvents, 5 is NumArts. 
# In this 17-col format, Index 1 is usually the Country Code!
col_map = {0: 'Date', 1: 'CountryCode', 5: 'NumArts'}

print("⏳ Distilling Volume-Based GDELT File...")

try:
    # Process in large chunks for speed
    chunks = pd.read_csv(
        master_path, sep='\t', header=None, 
        usecols=col_map.keys(), chunksize=2000000, low_memory=False,
        skiprows=1 # Skip that 'Date NumEvents' header row we saw in the peek
    )

    processed_chunks = []

    for i, chunk in enumerate(chunks):
        chunk.columns = [col_map[c] for c in chunk.columns]
        
        # Convert to numeric
        chunk['Date'] = pd.to_numeric(chunk['Date'], errors='coerce')
        chunk['NumArts'] = pd.to_numeric(chunk['NumArts'], errors='coerce')
        
        # Extract Year and Filter for 2020+
        chunk = chunk.dropna(subset=['Date', 'CountryCode'])
        chunk['Year'] = (chunk['Date'] // 10000)
        
        recent = chunk[chunk['Year'] >= 2020].copy()
        processed_chunks.append(recent[['CountryCode', 'NumArts']])
        
        print(f"   ...Processed {(i+1)*2:,} Million rows")

    print("📊 Calculating News Volume Baseline per Country...")
    df = pd.concat(processed_chunks)
    
    # Baseline = Average number of articles per mention for that country
    stability = df.groupby('CountryCode')['NumArts'].mean()

    if len(stability) == 0:
        print("❌ Still 0 countries. Try changing col_map index 1 to 2 or 3.")
    else:
        stability.to_csv(output_path)
        print(f"✅ SUCCESS! Created baseline for {len(stability)} countries.")

except Exception as e:
    print(f"❌ Error: {e}")
