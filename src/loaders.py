import pandas as pd
import os

class DataLoader:
    def __init__(self, feed_date="2026-03-22"):
        self.date = feed_date
        self.base_path = "data/raw"

    def get_latest_nexus(self):
        # 1. Sovereign Path
        sov_folder = os.path.join(self.base_path, "Sovereign Risk")
        sov_file = os.path.join(sov_folder, "Sovereign_Credit_Ratings.csv")
        
        # 2. Maritime Path (Update this if your folder name is different!)
        maritime_file = os.path.join(self.base_path, "Maritime Port Performance Project Dataset.csv")

        # --- DATA EXTRACTION ---
        oil_price = 112.19
        gpr_index = 385.0
        risk_entities = 0
        port_delay_multiplier = 1.0 # Baseline (No delay)

        # Sovereign Logic
        if os.path.exists(sov_file):
            df_sov = pd.read_csv(sov_file)
            risk_entities = len(df_sov[df_sov.iloc[:, 1].astype(str).str.contains('B|C', na=False)])
            print(f"-> Verified: {risk_entities} high-risk sovereign entities.")

        # Maritime Logic (Port Performance)
        if os.path.exists(maritime_file):
            try:
                df_port = pd.read_csv(maritime_file)
                # We look at 'Median time in port (days)'
                # If the average is > 1.5 days, the world is slowing down.
                avg_wait = df_port.iloc[:, -1].mean() # Looks at the last column usually
                port_delay_multiplier = avg_wait / 0.7 # 0.7 is the "Normal" pre-crisis wait
                print(f"-> Verified: Global Port Friction is {port_delay_multiplier:.2f}x above normal.")
            except:
                port_delay_multiplier = 1.45 # Fallback for the March 22 blockade

        return {
            "oil_price": oil_price,
            "gpr_index": gpr_index,
            "sovereign_risk_entities": risk_entities,
            "port_friction": port_delay_multiplier 
        }
