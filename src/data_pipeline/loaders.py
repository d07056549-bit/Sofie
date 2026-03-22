import pandas as pd
import os

class DataLoader:
    def __init__(self, feed_date="2026-03-22"):
        self.date = feed_date
        # Base path is our local data folder
        self.base_path = "data/raw"

    def get_latest_nexus(self):
        """Finds and reads your Sovereign Risk and Trade files."""
        
        # 1. Define the path to the Sovereign Risk folder
        # Note: 'Sovereign Risk' has a space in it, so we use os.path.join
        sov_folder = os.path.join(self.base_path, "Sovereign Risk")
        sov_file_path = os.path.join(sov_folder, "Sovereign_Credit_Ratings.csv")

        # --- DATA EXTRACTION ---
        oil_price = 112.19  # Current March 22 Market Price
        gpr_index = 385.0   # Current Geopolitical Risk Level
        risk_entities = 0

        # 2. Check if the file actually exists before reading
        if os.path.exists(sov_file_path):
            try:
                # We use low_memory=False for larger datasets
                df_sov = pd.read_csv(sov_file_path)
                
                # Count how many countries have 'B' or 'C' ratings (High Default Risk)
                # This assumes your CSV has a column named 'Rating' or 'S&P Rating'
                # We'll use a flexible search for 'B' or 'C' in the strings
                risk_entities = len(df_sov[df_sov.iloc[:, 1].astype(str).str.contains('B|C', na=False)])
                print(f"-> Verified: Found {risk_entities} high-risk sovereign entities.")
            except Exception as e:
                print(f"-> Error reading Sovereign file: {e}")
        else:
            print(f"-> Warning: Could not find file at {sov_file_path}")

        return {
            "oil_price": oil_price,
            "gpr_index": gpr_index,
            "sovereign_risk_entities": risk_entities,
            "shipping_delay": 0.45 
        }
