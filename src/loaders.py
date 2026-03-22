import os
import pandas as pd

class SofieLoader:
    def __init__(self, raw_path="data/raw"):
        self.raw_path = raw_path

    def check_inventory(self):
        """Checks which critical 2026 data files are present."""
        files = os.listdir(self.raw_path)
        print(f"--- Sofie Data Inventory (March 22, 2026) ---")
        print(f"Found {len(files)} files in {self.raw_path}")
        return files

    def load_market_data(self, filename):
        """Loads a specific market CSV (like Brent or Gold)."""
        file_path = os.path.join(self.raw_path, filename)
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            print(f"Error: {filename} not found.")
            return None

if __name__ == "__main__":
    # This part lets you test the script by itself
    loader = SofieLoader()
    loader.check_inventory()
