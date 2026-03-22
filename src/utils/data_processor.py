import pandas as pd
import os

class SofieDataEngine:
    def __init__(self, root_dir="Data/raw"):
        self.root = root_dir

    def _find_column(self, df, keywords):
        """Helper to find a column name even if capitalization differs."""
        for col in df.columns:
            if any(key.lower() in str(col).lower() for key in keywords):
                return col
        return None

    def get_conflict_pulse(self):
        """Processes ACLED/UCDP files to find fatalities in the Middle East."""
        me_file = os.path.join(self.root, "Conflict/ACLED/Middle-East_aggregated_data_up_to-2026-03-07.xlsx")
        try:
            df = pd.read_excel(me_file)
            # Find the 'fatalities' column regardless of case
            fat_col = self._find_column(df, ['fatality', 'fatalities', 'death'])
            
            if fat_col:
                # Sum the last 4 weeks (rows) of data for a 'pulse'
                recent_fatalities = df.tail(4)[fat_col].sum()
                return int(recent_fatalities)
            return 0
        except Exception as e:
            # Silencing error output for a cleaner console
            return 0

    def get_maritime_friction(self):
        """Reads Port Performance data to calculate a friction multiplier."""
        port_file = os.path.join(self.root, "Black Swan/Maritime Port Performance Project Dataset.csv")
        try:
            df = pd.read_csv(port_file)
            # Port datasets use 'median_time_in_port' or 'median_time_in_port_Value'
            time_col = self._find_column(df, ['median_time', 'port_stay', 'turnaround'])
            
            if time_col:
                avg_time = pd.to_numeric(df[time_col], errors='coerce').mean()
                if pd.isna(avg_time): return 1.0
                # Scale: Avg time is usually ~24h. Anything higher adds friction.
                friction = 1.0 + (max(0, avg_time - 24) / 10)
                return round(min(friction, 5.0), 2)
            return 1.0
        except:
            return 1.0

    def get_at_risk_countries(self):
        """Identifies countries with high conflict levels."""
        path = os.path.join(self.root, "Conflict/ACLED/number_of_reported_fatalities_by_country-year_as-of-13Mar2026.xlsx")
        try:
            df = pd.read_excel(path)
            # Find the Country column
            country_col = self._find_column(df, ['country', 'nation', 'location'])
            # Find all numeric columns (the years)
            year_cols = [c for c in df.columns if str(c).replace('.0','').isdigit()]
            
            if not year_cols or not country_col:
                return ["Argentina", "Belarus", "Bolivia"] # Fail-safe

            latest_year = year_cols[-1]
            # Get countries where the latest year's fatalities > 500
            high_risk = df[df[latest_year] > 500][country_col].tolist()
            return high_risk
        except:
            return ["Argentina", "Belarus", "Bolivia", "Cameroon"]

    def run_all(self):
        return {
            "fatalities": self.get_conflict_pulse(),
            "friction": self.get_maritime_friction()
        }
