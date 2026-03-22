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
                # We take the sum of the last 4 entries as the 'current' pulse
                return int(df.tail(4)[fat_col].sum())
            return 0
        except:
            return 0

    def get_maritime_friction(self):
        """Processes Port Performance CSV to find average delay factors."""
        port_file = os.path.join(self.root, "Black Swan/Maritime Port Performance Project Dataset.csv")
        try:
            df = pd.read_csv(port_file)
            time_col = self._find_column(df, ['median_time', 'port_stay'])
            if time_col:
                avg_time = pd.to_numeric(df[time_col], errors='coerce').mean()
                # Normalize: 1.0 is baseline. Every 10 hours above 24h adds 0.1 friction.
                return round(1.0 + (max(0, avg_time - 24) / 10), 2)
            return 1.0
        except:
            return 1.0

    def get_market_volatility(self):
        """Processes VIX data (Volatility folder) for market panic."""
        vix_path = os.path.join(self.root, "volatility/figure2_56.csv")
        try:
            df = pd.read_csv(vix_path)
            val_col = self._find_column(df, ['value', 'close', 'vix'])
            current_vix = float(df[val_col].iloc[-1])
            # Normalize: VIX 20 is baseline (1.0).
            return round(current_vix / 20.0, 2)
        except:
            return 1.0

    def get_migration_pressure(self):
        """Identifies top asylum seeker destinations for risk mapping."""
        path = os.path.join(self.root, "Migration & Refugee Flows/asylum_seekers.csv")
        try:
            # low_memory=False avoids DtypeWarnings for large migration files
            df = pd.read_csv(path, low_memory=False)
            country_col = self._find_column(df, ['country', 'asylum'])
            if country_col:
                return df.groupby(country_col).size().sort_values(ascending=False).head(5).index.tolist()
            return []
        except:
            return []

    def get_cyber_black_swan(self):
        """Scans cyber data for systemic 'Critical' triggers."""
        path = os.path.join(self.root, "Black Swan/cybersecurity synthesized data.csv")
        try:
            df = pd.read_csv(path, low_memory=False)
            sev_col = self._find_column(df, ['severity', 'attack_severity'])
            if sev_col:
                # Check the 10 most recent logs for severity scores above 8
                recent_logs = df.tail(10)
                critical_events = recent_logs[recent_logs[sev_col] >= 9]
                if not critical_events.empty:
                    return True, len(critical_events)
            return False, 0
        except:
            return False, 0

    def get_mobility_black_swan(self):
        """Detects sudden civilian paralysis via Global Mobility reports."""
        path = os.path.join(self.root, "Black Swan/Global_Mobility_Report.csv")
        try:
            # Optimized read: focusing on transit and workplace deviations
            df = pd.read_csv(path, low_memory=False)
            transit_col = self._find_column(df, ['transit_stations'])
            if transit_col:
                # If global average movement drops 50% below baseline, trigger Swan
                avg_drop = df.tail(50)[transit_col].mean()
                if avg_drop < -50:
                    return True, abs(avg_drop)
            return False, 0
        except:
            return False, 0

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
        """Aggregates per-country port data for the Logistics Heatmap."""
        port_file = os.path.join(self.root, "Black Swan/Maritime Port Performance Project Dataset.csv")
        try:
            df = pd.read_csv(port_file)
            economy_col = self._find_column(df, ['economy', 'country', 'label'])
            time_col = self._find_column(df, ['median_time', 'value'])
            if economy_col and time_col:
                df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
                return df.groupby(economy_col)[time_col].mean().to_dict()
            return {}
        except:
            return {}

    def run_all(self):
        """Main entry point: Pulls all tactical sensors into the Nexus."""
        is_cyber_swan, cyber_sev = self.get_cyber_black_swan()
        is_phys_swan, phys_sev = self.get_mobility_black_swan()
        
        return {
            "fatalities": self.get_conflict_pulse(),
            "friction": self.get_maritime_friction(),
            "volatility": self.get_market_volatility(),
            "migration_hotspots": self.get_migration_pressure(),
            "black_swan_active": is_cyber_swan or is_phys_swan,
            "swan_intensity": (cyber_sev + (phys_sev / 10)) # Weighted severity
        }
