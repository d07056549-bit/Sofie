import pandas as pd
import os

master_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Events\Gdelt\GDELT.MASTERREDUCEDV2.txt"
output_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\gdelt_historical_baseline.csv"

print("⏳ Distilling Reduced GDELT File...")

try:
    # 1. Read the first few lines to determine columns automatically
    df_preview = pd.read_csv(master_path, sep='\t', nrows=5, header=None)
    
    # 2. Identify columns by their data type
    # Year is usually an integer > 1979
    # Goldstein is a float between -10 and 10
    # Country code is a 2 or 3 letter string
    
    total_cols = len(df_preview.columns)
    print(f"🔍 Detected {total_cols} columns. Mapping data...")

    # Standard "Reduced" mapping often puts Year at 0, Goldstein at 1, Country at 2
    # We will try to read EVERYTHING and then filter
    df = pd.read_csv(master_path, sep='\t', header=None, low_memory=False)
    
    # Let's assume a common Reduced format: [Year, MonthDay, ID, Goldstein, Country...]
    # We'll assign names based on common Reduced schemas
    if total_cols >= 4:
        df.columns = [f'col_{i}' for i in range(total_cols)]
        # This is where we need the 'Peek' results to be 100% sure
        # But let's try a common guess:
        df = df.rename(columns={'col_0': 'Year', 'col_3': 'GoldsteinScale', 'col_4': 'CountryCode'})
    
    # Filter and Save
    recent = df[df['Year'] >= 2022]
    stability = recent.groupby('CountryCode')['GoldsteinScale'].mean()
    stability.to_csv(output_path)
    
    print(f"✅ Baseline created with {len(stability)} countries.")

except Exception as e:
    print(f"❌ Brute force failed: {e}")
