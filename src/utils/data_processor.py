import os
import pandas as pd
import feedparser

class SofieDataEngine:
    def __init__(self, root_dir=r"C:\Users\Empok\Documents\GitHub\Sofie"):
        self.root = root_dir
        self.maritime_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Supply Chain\Port\Maritime Port Performance Project Dataset.csv"

    def get_live_port_alerts(self):
        """Scrapes the live maritime feed."""
        feed_url = "https://www.maritime-executive.com/rss"
        try:
            feed = feedparser.parse(feed_url)
            return [{"title": e.title, "summary": e.summary[:100]} for e in feed.entries[:5]]
        except:
            return [{"title": "Feed Offline", "summary": "Direct CSV data only."}]

    def run_all(self):
        print(">>> ENGINE STARTING: Processing Maritime Streams...")
        
        port_map = {}
        global_avg_friction = 1.0 # Default fallback
        
        if os.path.exists(self.maritime_path):
            print(f"✅ MARITIME SENSOR: Online")
            try:
                df = pd.read_csv(self.maritime_path)
                
                # Detect column names automatically
                name_col = 'Port Name' if 'Port Name' in df.columns else df.columns[0]
                fric_col = 'Friction' if 'Friction' in df.columns else 'Performance'
                lat_col = 'Latitude' if 'Latitude' in df.columns else 'Lat'
                lon_col = 'Longitude' if 'Longitude' in df.columns else 'Lon'

                for _, row in df.iterrows():
                    p_name = str(row[name_col])
                    val = float(row.get(fric_col, 1.0))
                    port_map[p_name] = {
                        "friction": val,
                        "lat": float(row.get(lat_col, 0.0)),
                        "lon": float(row.get(lon_col, 0.0))
                    }
                
                # Calculate the Global Average (This is what main.py needs for line 55)
                if port_map:
                    global_avg_friction = sum(p['friction'] for p in port_map.values()) / len(port_map)
                    
            except Exception as e:
                print(f"⚠️ Error reading CSV: {e}")
        else:
            print(f"❌ MARITIME SENSOR: Missing at {self.maritime_path}")

        # --- CRITICAL: Ensure 'friction' is a FLOAT, not a DICT ---
        return {
            "alerts": self.get_live_port_alerts(),
            "friction": float(global_avg_friction), # This number fixes the TypeError
            "port_map": port_map,                  # This dict is for the Visualizer
            "status": "Operational"
        }
