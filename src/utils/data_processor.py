from circuitbreaker import circuit
import pandas as pd
import os

class SofieDataEngine:
    def __init__(self):
        self.cyber_path = "cybersecurity synthesized data.csv"
        self.maritime_path = "Maritime Port Performance Project Dataset.csv"

    # --- FALLBACKS (The 'Safety Net') ---
    def fallback_cyber(self):
        print("⚠️ CIRCUIT OPEN: Cyber data unavailable. Using baseline safety.")
        return False, 0.0

    def fallback_maritime(self):
        print("⚠️ CIRCUIT OPEN: Maritime data unavailable. Using baseline friction.")
        return 1.05 # Default 5% friction

    # --- PROTECTED SENSORS ---
    @circuit(failure_threshold=3, recovery_timeout=60, fallback_function=fallback_cyber)
    def get_cyber_black_swan(self):
        df = pd.read_csv(self.cyber_path)
        # We look for High Severity (9 or 10)
        critical_hits = df[df['attack_severity'] >= 9]
        if not critical_hits.empty:
            return True, critical_hits['attack_severity'].mean()
        return False, 0.0

    @circuit(failure_threshold=3, recovery_timeout=60, fallback_function=fallback_maritime)
    def get_maritime_friction(self):
        df = pd.read_csv(self.maritime_path)
        # Calculate average port delay/time
        return df['Median_time_in_port_days_Value'].mean()
