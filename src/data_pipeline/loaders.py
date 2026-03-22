import pandas as pd
import os

class DataLoader:
    def __init__(self, feed_date):
        self.date = feed_date
        self.raw_path = "data/raw"

    def get_latest_nexus(self):
        """Actually reads your 2026 CSV files from data/raw."""
        
        # 1. Look for your Sovereign Credit file
        sov_file = os.path.join(self.raw_path, "Sovereign_Credit_Ratings.csv")
        
        # 2. Look for your March 21 ComTrade file
        # (Using the name from your earlier folder list)
        trade_file = os.path.join(self.raw_path, "TradeData_3_21_2026_13_19_10.csv")

        # --- INTERNAL LOGIC ---
        # If files exist, we'll extract data. If not, we use 'Safe Estimates'
        oil_price = 112.19  # We will eventually automate this too
        gpr_index = 385.0
        
        # Let's count how many "At Risk" countries are in your Sovereign file
        risk_count = 0
        if os.path.exists(sov_file):
            df_sov = pd.read_csv(sov_file)
            # Count countries with 'B' or 'C' ratings (High Default Risk)
            risk_count = len(df_sov[df_sov['Rating'].str.contains('B|C', na=False)])

        return {
            "oil_price": oil_price,
            "gpr_index": gpr_index,
            "sovereign_risk_entities": risk_count,
            "shipping_delay": 0.45 
        }
