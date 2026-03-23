import os
import pandas as pd
import feedparser

class SofieDataEngine:
    def __init__(self, root_dir=r"C:\Users\Empok\Documents\GitHub\Sofie"):
        # We use a clean absolute path to avoid the "Data/raw\Data" double-nesting
        self.root = root_dir
        self.maritime_path = os.path.join(self.root, "Data", "Maritime Port Performance Project Dataset.csv")

    def get_live_port_alerts(self):
        """Scrapes the live maritime feed."""
        feed_url = "https://www.maritime-executive.com/rss"
        try:
            feed = feedparser.parse(feed_url)
            return [{"title": e.title, "summary": e.summary[:100]} for e in feed.entries[:5]]
        except:
            return [{"title": "Feed Offline", "summary": "Direct CSV data only."}]

    def run_all(self):
        print(">>> ENGINE STARTING: Processing Maritime & Trade Streams...")
        
        # 1. Initialize empty friction dict (The "Backfill")
        friction_results = {}
        
        # 2. Check and Load Maritime Data
        if os.path.exists(self.maritime_path):
            print(f"✅ MARITIME SENSOR: Online")
            try:
                df = pd.read_csv(self.maritime_path)
                # Map the CSV data into the format main.py expects: {PortName: FrictionValue}
                # Assuming your CSV has 'Port Name' and 'Friction' columns
                for _, row in df.iterrows():
                    port_name = str(row.get('Port Name', 'Unknown'))
                    friction_results[port_name] = row.get('Friction', 1.0) # Default to 1.0 if missing
            except Exception as e:
                print(f"⚠️ Error reading CSV: {e}")
        else:
            print(f"❌ MARITIME SENSOR: Missing at {self.maritime_path}")

        # 3. Return EVERYTHING main.py needs
        return {
            "alerts": self.get_live_port_alerts(),
            "friction": friction_results,  # THIS FIXES THE KeyError: 'friction'
            "status": "Operational"
        }
