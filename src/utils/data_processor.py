import pandas as pd
import numpy as np
import os
from circuitbreaker import circuit

class SofieDataEngine:
    def __init__(self, root_dir="."):
        # This allows the engine to find files even if they are in subfolders
        self.root = os.path.abspath(root_dir)
        
        # Search for the Cyber file in common locations
        cyber_filename = "cybersecurity synthesized data.csv"
        maritime_filename = "Maritime Port Performance Project Dataset.csv"
        
        search_locations = [
            self.root,
            os.path.join(self.root, "Data", "raw"),
            os.path.join(self.root, "Data", "raw", "Black Swan")
        ]
        
        self.cyber_path = self._find_file(cyber_filename, search_locations)
        self.maritime_path = self._find_file(maritime_filename, search_locations)

    def _find_file(self, name, locations):
        for loc in locations:
            path = os.path.join(loc, name)
            if os.path.exists(path):
                print(f"✅ SENSOR ONLINE: Found {name} at {path}")
                return path
        print(f"❌ SENSOR OFFLINE: Could not find {name}. Using fallbacks.")
        return None

    # --- FALLBACKS ---
    def fallback_cyber(self, *args, **kwargs): return False, 0.0
    def fallback_maritime(self, *args, **kwargs): return 5.14 # The '77.71' historical value

    @circuit(failure_threshold=1, recovery_timeout=60, fallback_function=fallback_cyber)
    def get_cyber_black_swan(self):
        if not self.cyber_path: return False, 0.0
        df = pd.read_csv(self.cyber_path, low_memory=False)
        critical_hits = df[df['attack_severity'] >= 9]
        if not critical_hits.empty:
            return True, float(critical_hits['attack_severity'].mean())
        return False, 0.0

    @circuit(failure_threshold=1, recovery_timeout=60, fallback_function=fallback_maritime)
    def get_maritime_friction(self):
        if not self.maritime_path: return 5.14
        df = pd.read_csv(self.maritime_path, low_memory=False)
        # We need to ensure we are reading the right column for '77' range scores
        val = pd.to_numeric(df['Median_time_in_port_days_Value'], errors='coerce').mean()
        return round(val, 2) if not np.isnan(val) else 5.14

    def run_all(self):
        is_swan, swan_sev = self.get_cyber_black_swan()
        return {
            "fatalities": 150,
            "friction": self.get_maritime_friction(),
            "volatility": 1.25,
            "black_swan_active": is_swan,
            "swan_severity": swan_sev
        }
