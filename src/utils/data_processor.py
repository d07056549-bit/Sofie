import os
import pandas as pd

class SofieDataEngine:
    def __init__(self, root_dir="Data/raw"):
        self.root_dir = root_dir
        self.paths = {
            "cyber": os.path.join(root_dir, "Black Swan", "cybersecurity synthesized data.csv"),
            "maritime": os.path.join(root_dir, "Black Swan", "Maritime Port Performance Project Dataset.csv")
        }

    def run_all(self):
        """Pulls raw stats for the main stability calculation."""
        stats = {'friction': 1.0, 'fatalities': 0, 'volatility': 1.0}
        
        # Check Cybersecurity Data
        if os.path.exists(self.paths["cyber"]):
            df = pd.read_csv(self.paths["cyber"])
            stats['volatility'] = df['Complexity Score'].mean() if 'Complexity Score' in df else 1.5
        
        # Check Maritime Data
        if os.path.exists(self.paths["maritime"]):
            df = pd.read_csv(self.paths["maritime"])
            stats['friction'] = df['Wait Time (Hours)'].mean() / 24 if 'Wait Time (Hours)' in df else 1.2
            
        return stats

    def get_at_risk_countries(self):
        """RESTORING: Returns a list of nations under high tension."""
        # Fallback list for the March 22 Nexus
        return ["Netherlands", "Singapore", "USA", "United Kingdom", "Taiwan"]

    def get_port_friction_map(self):
        """RESTORING: Returns dictionary of port locations and their current friction."""
        # Simple coordinate mapping for the LogisticsMapper to use
        return {
            "Rotterdam": {"lat": 51.9, "lon": 4.4, "friction": 4.5},
            "Singapore": {"lat": 1.3, "lon": 103.8, "friction": 3.8},
            "Long Beach": {"lat": 33.7, "lon": -118.2, "friction": 2.9}
        }
