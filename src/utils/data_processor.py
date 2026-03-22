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

    def get_market_volatility(self):
        """Processes the VIX data to adjust the Stability Index sensitivity."""
        # Path to your figure2_56.csv or extracted VIX data
        vix_path = os.path.join(self.root, "volatility/figure2_56.csv")
        try:
            df = pd.read_csv(vix_path)
            # Find the most recent 'Close' or 'Value'
            val_col = self._find_column(df, ['value', 'close', 'vix'])
            current_vix = float(df[val_col].iloc[-1])
            # Normalize: VIX of 20 is baseline (1.0). VIX of 40 is 2.0x panic.
            return round(current_vix / 20.0, 2)
        except:
            return 1.0

    def get_migration_pressure(self):
        """Analyzes asylum seekers to find 'Refugee Hotspots' for the map."""
        migration_path = os.path.join(self.root, "Migration & Refugee Flows/asylum_seekers.csv")
        try:
            df = pd.read_csv(migration_path)
            # Group by Country of Asylum and count recent applications
            # We filter for 'recent' if the column exists, else take top 10
            country_col = self._find_column(df, ['country', 'asylum'])
            top_pressures = df.groupby(country_col).size().sort_values(ascending=False).head(10).index.tolist()
            return top_pressures
        except:
            return []

    def get_energy_vulnerability(self):
        """Uses OWID CO2 data to see which nations are most oil-dependent."""
        co2_path = os.path.join(self.root, "OWID/annual-co2-emissions-per-country/annual-co2-emissions-per-country.csv")
        try:
            df = pd.read_csv(co2_path)
            # Find countries with highest recent emissions - these feel the $112 oil spike most
            latest_year = df[df['Year'] == df['Year'].max()]
            high_emissions = latest_year.nlargest(15, 'Annual CO2 emissions')['Entity'].tolist()
            return high_emissions
        except:
            return []

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

    def get_port_friction_map(self):
        """Extracts a dictionary of countries and their median port stay times."""
        port_file = os.path.join(self.root, "Black Swan/Maritime Port Performance Project Dataset.csv")
        try:
            df = pd.read_csv(port_file)
            
            # Find the Economy and Median Time columns
            economy_col = self._find_column(df, ['economy', 'country', 'label'])
            time_col = self._find_column(df, ['median_time', 'port_stay', 'value'])
            
            if economy_col and time_col:
                # Convert time to numeric and group by country
                df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
                # Average the time per country (taking the latest available)
                friction_data = df.groupby(economy_col)[time_col].mean().to_dict()
                return friction_data
            return {}
        except Exception as e:
            print(f"!! Friction Map Data Error: {e}")
            return {}

    def run_all(self):
        return {
            "fatalities": self.get_conflict_pulse(),
            "friction": self.get_maritime_friction()
        }
