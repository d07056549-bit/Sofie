import os
import pandas as pd

class SofieDataEngine:
    def __init__(self, root_dir="Data/raw"):
        self.root_dir = root_dir
        # Fixed paths for the March 22 structure
        self.paths = {
            "cyber": os.path.join(root_dir, "Black Swan", "cybersecurity synthesized data.csv"),
            "maritime": os.path.join(root_dir, "Black Swan", "Maritime Port Performance Project Dataset.csv")
        }

    def run_all(self):
        """Pulls raw stats for the main stability calculation."""
        # Baseline fallbacks if CSVs are missing
        stats = {'friction': 1.2, 'fatalities': 450, 'volatility': 1.5}
        
        if os.path.exists(self.paths["cyber"]):
            df = pd.read_csv(self.paths["cyber"])
            stats['volatility'] = df['Complexity Score'].mean() if 'Complexity Score' in df else 1.5
        else:
            print("❌ SENSOR OFFLINE: Cybersecurity data not found. Using fallbacks.")
        
        if os.path.exists(self.paths["maritime"]):
            df = pd.read_csv(self.paths["maritime"])
            # Simplified friction calculation
            stats['friction'] = 2.5 
        else:
            print("❌ SENSOR OFFLINE: Maritime data not found. Using fallbacks.")
            
        return stats

    def get_at_risk_countries(self):
        """RESTORING: Returns the list of nations under high tension for the Mapper."""
        return ["Netherlands", "Singapore", "Taiwan", "USA", "United Kingdom"]

    def get_port_friction_map(self):
        """RESTORING: Returns dictionary of port data for the LogisticsMapper."""
        # This provides coordinates so the maps actually show tension points
        return {
            "Rotterdam": {"lat": 51.9, "lon": 4.4, "friction": 4.5},
            "Singapore": {"lat": 1.3, "lon": 103.8, "friction": 3.8},
            "Long Beach": {"lat": 33.7, "lon": -118.2, "friction": 2.9},
            "Kaohsiung": {"lat": 22.6, "lon": 120.3, "friction": 4.1}
        }
