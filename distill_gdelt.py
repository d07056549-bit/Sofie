import pandas as pd
import os

master_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Events\Gdelt\GDELT.MASTERREDUCEDV2.txt"
output_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\gdelt_historical_baseline.csv"

# Let's try to find the Country Code by looking at columns 4, 5, 7, and 12 
# (Common spots for country data in reduced files)
col_map = {0: 'Date', 4: 'Country1', 5: 'Country2', 9: 'GoldsteinScale'}

print("⏳ Re-Distilling 87M Rows (Diagnostic Mode)...")

try:
    chunks = pd.read_csv(
        master_path, sep='\t', header=None, 
        usecols=col_map.keys(), chunksize=500000, low_memory=False
    )

    processed_chunks = []
    
    # Peek at the first chunk to see what we're working with
    first_chunk = next(chunks)
    print("\n--- DATA PEEK (First 5 Rows) ---")
    print(first_chunk.head())
    print("-------------------------------\n")

    # Reset chunks and start loop
    chunks = pd.read_csv(
        master_path, sep='\t', header=None, 
        usecols=col_map.keys(), chunksize=1000000, low_memory=False
    )

    for i, chunk in enumerate(chunks):
        chunk.columns = [col_map[c] for c in chunk.columns]
        
        # Proper way to create a new column without the warning
        chunk = chunk.copy() 
        chunk['Date'] = pd.to_numeric(chunk['Date'], errors='coerce')
        chunk['GoldsteinScale'] = pd.to_numeric(chunk['GoldsteinScale'], errors='coerce')
        
        # Extract Year safely
        chunk = chunk.dropna(subset=['Date'])
        chunk['Year'] = (chunk['Date'] // 10000).astype(int)
        
        # Only keep 2020+
        recent = chunk[chunk['Year'] >= 2020]
        
        # Use Country1 as the primary, but if it's empty, we'll try to find any string
        processed_chunks.append(recent[['Country1', 'GoldsteinScale']])
        
        if i % 5 == 0:
            print(f"   ...Processed {i+1} Million rows")

    print("📊 Aggregating...")
    df = pd.concat(processed_chunks)
    
    # CLEANING: Drop rows where Country is NaN or just whitespace
    df = df.dropna(subset=['Country1'])
    df = df[df['Country1'].astype(str).str.strip() != ""]
    
    stability = df.groupby('Country1')['GoldsteinScale'].mean()

    if len(stability) == 0:
        print("❌ Still found 0 countries. Check the 'DATA PEEK' above to see which column has the codes!")
    else:
        stability.to_csv(output_path)
        print(f"✅ SUCCESS! Created baseline for {len(stability)} countries.")

except Exception as e:
    print(f"❌ Error: {e}")
