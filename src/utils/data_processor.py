import pandas as pd
import os

class SofieDataEngine:
    def __init__(self, root_dir="Data/raw"):
        self.root = root_dir

    def get_conflict_pulse(self):
        """Processes ACLED/UCDP files to find total deaths/events this week."""
        # Focus on the most recent Middle East data you have
        me_file = os.path.join(self.root, "Conflict/ACLED/Middle-East_aggregated_data_up_to-2026-03-07.xlsx")
        try:
            df = pd.read_excel(me_file)
            # Use the latest week's fatalities
            recent_fatalities = df.iloc[-1]['fatalities'] 
            return recent_fatalities
        except:
            return 0

    def get_maritime_friction(self):
        """Reads Port Performance data to calculate a friction multiplier."""
        port_file = os.path.join(self.root, "Black Swan/Maritime Port Performance Project Dataset.csv")
        try:
            df = pd.read_csv(port_file)
            # Compare current median time vs global average
            avg_time = df['median_time_in_port'].mean()
            # If current times in your region are 2x the average, friction = 2.0
            return round(avg_time / 1.5, 2) 
        except:
            return 1.0

    def get_at_risk_countries(self):
        # Look at the 'fatalities' file
        path = os.path.join(self.root, "Conflict/ACLED/number_of_reported_fatalities_by_country-year_as-of-13Mar2026.xlsx")
        df = pd.read_excel(path)
        # Grab any country with > 500 fatalities in 2026
        high_risk = df[df['2026'] > 500]['Country'].tolist()
        return high_risk

    def run_all(self):
        return {
            "fatalities": self.get_conflict_pulse(),
            "friction": self.get_maritime_friction()
        }
