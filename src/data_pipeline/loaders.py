import pandas as pd
import os

class DataLoader:
    def __init__(self, feed_date):
        self.date = feed_date
        self.path = "data/raw/"

    def get_latest_nexus(self):
        """Combines Market, Conflict, and Sovereign data into one dictionary."""
        # In a real run, this would use pd.read_csv on your specific files
        return {
            "oil_price": 112.19,
            "gpr_index": 385.0,  # High Geopolitical Risk
            "shipping_delay": 0.45, # 45% increase in transit time
            "sovereign_yields": 0.08 # 8% average increase in bond yields
        }
