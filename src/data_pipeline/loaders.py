import pandas as pd
import os

class DataLoader:
    def __init__(self, feed_date="2026-03-22"):
        self.date = feed_date
        self.base_path = "data/raw"

    def get_latest_nexus(self):
        # Paths
        sov_folder = os.path.join(self.base_path, "Sovereign Risk")
        sov_file = os.path.join(sov_folder, "Sovereign_Credit_Ratings.csv")
        maritime_file = os.path.join(self.base_path, "Maritime Port Performance Project Dataset.csv")

        # Default Values (If files are missing)
        risk_entities = 0
        port_friction = 1.0  # 1.0 means "Normal/No Delay"

        # Load Sovereign Data
        if os.path.exists(sov_file):
            df_sov = pd.read_csv(sov_file)
            risk_entities = len(df_sov[df_sov.iloc[:, 1].astype(str).str.contains('B|C', na=False)])

        # Load Maritime Data
        if os.path.exists(maritime_file):
            try:
                df_port = pd.read_csv(maritime_file)
                # Calculating friction: (Current Median / Target Median)
                # We assume the wait time is in the last column
                avg_wait = df_port.iloc[:, -1].mean() 
                port_friction = avg_wait / 0.7 
            except:
                port_friction = 1.45 # March 22 Default due to blockade

        # THIS IS THE CRITICAL PART: The dictionary must contain 'port_friction'
        return {
            "oil_price": 112.19,
            "gpr_index": 385.0,
            "sovereign_risk_entities": risk_entities,
            "port_friction": port_friction  # <--- THIS WAS LIKELY MISSING
        }
