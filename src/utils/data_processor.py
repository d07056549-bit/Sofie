from circuitbreaker import circuit
import pandas as pd
import numpy as np
import os

class SofieDataEngine:
    def __init__(self, root_dir="."):
        self.root = root_dir
        # Paths to your specific files
        self.cyber_path = os.path.join(self.root, "cybersecurity synthesized data.csv")
        self.maritime_path = os.path.join(self.root, "Maritime Port Performance Project Dataset.csv")
        self.vix_path = os.path.join(self.root, "stability_history.csv") # Using history as a proxy for this test

    # --- FALLBACKS (The 'Safety Valves') ---
    def fallback_cyber(self):
        return False, 0.0

    def fallback_maritime(self):
        return 1.05 

    def fallback_generic(self):
        return 0.0

    # --- PROTECTED SENSORS ---

    @circuit(failure_threshold=3, recovery_timeout=60, fallback_function=fallback_cyber)
    def get_cyber_black_swan(self):
        """Scans cyber data for high-severity triggers."""
        if not os.path.exists(self.cyber_path):
            raise FileNotFoundError
        df = pd.read_csv(self.cyber_path, low_memory=False)
        critical_hits = df[df['attack_severity'] >= 9]
        if not critical_hits.empty:
            # Severity count acts as the multiplier base
            return True, float(len(critical_hits))
        return False, 0.0

    @circuit(failure_threshold=3, recovery_timeout=60, fallback_function=fallback_maritime)
    def get_maritime_friction(self):
        """Calculates port delay factors."""
        if not os.path.exists(self.maritime_path):
            raise FileNotFoundError
        df = pd.read_csv(self.maritime_path, low_memory=False)
        # We look for the median time in port
        val = pd.to_numeric(df['Median_time_in_port_days_Value'], errors='coerce').mean()
        return round(val, 2) if not np.isnan(val) else 1.0

    def get_market_volatility(self):
        # Placeholder for VIX logic
        return 1.2 

    def get_conflict_pulse(self):
        # Placeholder for ACLED logic
        return 150 

    # --- THE BRAIN ---
    def run_all(self):
        """Collects all stats into the dictionary main.py expects."""
        is_swan, swan_sev = self.get_cyber_black_swan()
        
        return {
            "fatalities": self.get_conflict_pulse(),
            "friction": self.get_maritime_friction(),
            "volatility": self.get_market_volatility(),
            "black_swan_event": is_swan,
            "swan_severity": swan_sev
        }
