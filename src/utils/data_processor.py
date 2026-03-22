import pandas as pd
import numpy as np
import os
from circuitbreaker import circuit

class SofieDataEngine:
    def __init__(self, root_dir="."):
        self.root = root_dir
        # Standardize paths to the root folder where you are running the script
        self.cyber_path = os.path.join(self.root, "cybersecurity synthesized data.csv")
        self.maritime_path = os.path.join(self.root, "Maritime Port Performance Project Dataset.csv")

    # --- FALLBACK FUNCTIONS ---
    # These MUST be defined before they are used in decorators
    def fallback_cyber(self, *args, **kwargs):
        return False, 0.0

    def fallback_maritime(self, *args, **kwargs):
        return 1.05

    # --- PROTECTED SENSORS ---

    @circuit(failure_threshold=1, recovery_timeout=60, fallback_function=fallback_cyber)
    def get_cyber_black_swan(self):
        """Scans cyber data for high-severity triggers."""
        if not os.path.exists(self.cyber_path):
            return False, 0.0
            
        df = pd.read_csv(self.cyber_path, low_memory=False)
        # Look for the 'attack_severity' column we saw in your CSV
        critical_hits = df[df['attack_severity'] >= 9]
        if not critical_hits.empty:
            return True, float(critical_hits['attack_severity'].mean())
        return False, 0.0

    @circuit(failure_threshold=1, recovery_timeout=60, fallback_function=fallback_maritime)
    def get_maritime_friction(self):
        """Calculates port delay factors."""
        if not os.path.exists(self.maritime_path):
            return 1.0
            
        df = pd.read_csv(self.maritime_path, low_memory=False)
        # Use the Median Time column from your Maritime CSV
        val = pd.to_numeric(df['Median_time_in_port_days_Value'], errors='coerce').mean()
        return round(val, 2) if not np.isnan(val) else 1.0

    def get_market_volatility(self):
        return 1.25 # Current baseline for 22:30 GMT

    def get_conflict_pulse(self):
        return 150 # Placeholder for ACLED fatalities

    # --- THE BRAIN ---
    def run_all(self):
        """Standardized entry point for main.py"""
        is_swan, swan_sev = self.get_cyber_black_swan()
        
        return {
            "fatalities": self.get_conflict_pulse(),
            "friction": self.get_maritime_friction(),
            "volatility": self.get_market_volatility(),
            "black_swan_event": is_swan,
            "black_swan_active": is_swan, # Double-keying for safety
            "swan_severity": swan_sev
        }
