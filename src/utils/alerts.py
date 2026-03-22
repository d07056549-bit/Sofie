import pandas as pd
import os

class SofieAlerts:
    def __init__(self, sov_path="data/raw/Sovereign Risk/Sovereign_Credit_Ratings.csv"):
        self.sov_path = sov_path

    def get_top_threats(self):
        """Identifies the 5 countries most likely to default this week."""
        if os.path.exists(self.sov_path):
            df = pd.read_csv(self.sov_path)
            # Filter for the absolute worst ratings (C, CCC, etc.)
            critical = df[df.iloc[:, 1].astype(str).str.contains('C', na=False)].head(5)
            
            print("\n--- ⚠️ SOFIE CRITICAL WATCHLIST ---")
            for index, row in critical.iterrows():
                print(f"!! ALERT: {row.iloc[0]} | Rating: {row.iloc[1]} | Status: DEBT AT RISK")
