import pandas as pd
import os

class SofieDataEngine:
    def __init__(self, root_dir="Data/raw"):
        self.root = root_dir

    def _find_column(self, df, keywords):
        """Helper to find a column name regardless of capitalization."""
        for col in df.columns:
            if any(key.lower() in str(col).lower() for key in keywords):
                return col
        return None

    def get_conflict_pulse(self):
        """Processes ACLED fatalities for the Middle East."""
        me_file = os.path.join(self.root, "Conflict/ACLED/Middle-East_aggregated_data_up_to-2026-03-07.xlsx")
        try:
            df = pd.read_excel(me_file)
            fat_col = self._find_column(df, ['fatality', 'fatalities', 'death'])
            if fat_col:
                return int(df.tail(4)[fat_col].sum())
            return 0
        except:
            return 0

    def get_maritime_friction(self):
        """Processes Port Performance CSV."""
        port_file = os.path.join(self.root, "Black Swan/Maritime Port Performance Project Dataset.csv")
        try:
            df = pd.read_csv(port_file)
            time_col = self._find_column(df, ['median_time', 'port_stay'])
            if time_col:
                avg_time = pd.to_numeric(df[time_col], errors='coerce').mean()
                return round(1.0 + (max(0, avg_time - 24) / 10), 2)
            return 1.0
        except:
            return 1.0

    def get_market_volatility(self):
        """Processes VIX data (Volatility folder)."""
        vix_path = os.path.join(self.root, "volatility/figure2_56.csv")
        try:
            df = pd.read_csv(vix_path)
            val_col = self._find_column(df, ['value', 'close', 'vix'])
            current_vix = float(df[val_col].iloc[-1])
            # Normalize: VIX 20 = 1.0. Higher is more panic.
            return round(current_vix / 20.0, 2)
        except:
            return 1.0

    def get_migration_pressure(self):
        """Identifies top asylum seeker destinations."""
        path = os.path.join(self.root, "Migration & Refugee Flows/asylum_seekers.csv")
        try:
            df = pd.read_csv(path)
            country_col = self._find_column(df, ['country', 'asylum'])
            return df.groupby(country_col).size().sort_values(ascending=False).head(5).index.tolist()
        except:
            return []

    def get_at_risk_countries(self):
        """Dynamic Risk List from ACLED Fatalities."""
        path = os.path.join(self.root, "Conflict/ACLED/number_of_reported_fatalities_by_country-year_as-of-13Mar2026.xlsx")
        try:
            df = pd.read_excel(path)
            country_col = self._find_column(df, ['country', 'nation'])
            year_cols = [c for c in df.columns if str(c).replace('.0','').isdigit()]
            if year_cols:
                latest = year_cols[-1]
                return df[df[latest] > 500][country_col].tolist()
            return ["Argentina", "Belarus"]
        except:
            return ["Argentina", "Belarus", "Bolivia"]

    def get_port_friction_map(self):
        """Data for the Logistics Heatmap."""
        port_file = os.path.join(self.root, "Black Swan/Maritime Port Performance Project Dataset.csv")
        try:
            df = pd.read_csv(port_file)
            economy_col = self._find_column(df, ['economy', 'country'])
            time_col = self._find_column(df, ['median_time', 'value'])
            if economy_col and time_col:
                df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
                return df.groupby(economy_col)[time_col].mean().to_dict()
            return {}
        except:
            return {}

    def run_all(self):
        """Combines all sensors into a single dictionary."""
        return {
            "fatalities": self.get_conflict_pulse(),
            "friction": self.get_maritime_friction(),
            "volatility": self.get_market_volatility(),
            "migration_hotspots": self.get_migration_pressure()
        }
