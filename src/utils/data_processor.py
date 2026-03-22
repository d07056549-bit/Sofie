import pandas as pd
import os

class SofieDataEngine:
    def __init__(self, root_dir="Data/raw"):
        self.root = root_dir

    def get_conflict_pulse(self):
        """Processes ACLED/UCDP files to find fatalities in the Middle East."""
        me_file = os.path.join(self.root, "Conflict/ACLED/Middle-East_aggregated_data_up_to-2026-03-07.xlsx")
        try:
            # ACLED regional files usually have a 'fatalities' column per row
            df = pd.read_excel(me_file)
            # Get the sum of fatalities from the most recent 4 weeks of data
            recent_fatalities = df.tail(4)['fatalities'].sum()
            return int(recent_fatalities)
        except Exception as e:
            print(f"!! Conflict Pulse Error: {e}")
            return 0

    def get_maritime_friction(self):
        """Reads Port Performance data to calculate a friction multiplier."""
        port_file = os.path.join(self.root, "Black Swan/Maritime Port Performance Project Dataset.csv")
        try:
            df = pd.read_csv(port_file)
            # Find the average 'median_time_in_port'
            avg_time = df['median_time_in_port'].mean()
            # If the data is empty or malformed, return baseline 1.0
            if pd.isna(avg_time): return 1.0
            # Logic: If port times are > 30 hours, friction starts scaling up
            friction = 1.0 + (max(0, avg_time - 24) / 12)
            return round(min(friction, 5.0), 2)
        except:
            return 1.0

    def get_at_risk_countries(self):
        """Identifies countries with high conflict levels from the fatalities file."""
        path = os.path.join(self.root, "Conflict/ACLED/number_of_reported_fatalities_by_country-year_as-of-13Mar2026.xlsx")
        try:
            df = pd.read_excel(path)
            
            # DYNAMIC COLUMN PICKER:
            # Find all numeric columns (years) and pick the very last one
            year_cols = [c for c in df.columns if str(c).isdigit()]
            latest_year = year_cols[-1] # This will pick 2025 or 2026 automatically
            
            print(f"-> Analyzing data for year: {latest_year}")
            
            # Filter countries with > 500 fatalities in the latest recorded year
            high_risk = df[df[latest_year] > 500]['Country'].tolist()
            return high_risk
        except Exception as e:
            print(f"!! Risk List Error: {e}")
            return ["Argentina", "Belarus", "Bolivia"] # Fallback defaults

    def run_all(self):
        return {
            "fatalities": self.get_conflict_pulse(),
            "friction": self.get_maritime_friction()
        }
