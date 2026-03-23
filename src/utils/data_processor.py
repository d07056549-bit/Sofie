import os
import pandas as pd
import feedparser

class SofieDataEngine:
    def __init__(self, root_dir=r"C:\Users\Empok\Documents\GitHub\Sofie"):
        self.root = root_dir
        self.maritime_path = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Supply Chain\Port\Maritime Port Performance Project Dataset.csv"

    def get_live_port_alerts(self):
        """Fetches maritime news strictly from live RSS feeds."""
        import feedparser
        
        feeds = [
            "https://gcaptain.com/feed/",
            "https://www.maritime-executive.com/rss"
        ]
        
        all_alerts = []
        try:
            for url in feeds:
                feed = feedparser.parse(url)
                for entry in feed.entries[:8]: # Grab top 8
                    all_alerts.append({
                        'title': entry.title,
                        'source': 'Live Feed'
                    })
        except Exception:
            # If the web fails, we use a hardcoded "System Status" so it's not blank
            all_alerts = [{'title': "SYSTEM: Live Feed Offline. Check Network Connection.", 'source': 'System'}]
            
        return all_alerts
    def get_at_risk_countries(self):
        """
        Analyzes TradeData CSVs to find countries with the highest 
        economic exposure (Top 5 by primaryValue).
        """
        # List of the trade files you uploaded
        trade_files = [
            r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\TradeData_3_21_2026_13_19_10.csv",
            r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\TradeData_3_21_2026_13_20_4.csv",
            r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\TradeData_3_21_2026_13_21_3.csv"
        ]
        
        at_risk = []
        try:
            # We'll look at the most recent trade file for our 'At Risk' list
            latest_trade = trade_files[0] 
            if os.path.exists(latest_trade):
                df = pd.read_csv(latest_trade)
                # Group by country and sum their trade value
                top_trade = df.groupby('reporterDesc')['primaryValue'].sum().sort_values(ascending=False).head(5)
                
                for country, value in top_trade.items():
                    # Format value to Billions for the dashboard
                    billions = value / 1_000_000_000
                    at_risk.append(f"{country} (${billions:.1f}B Trade)")
            
            # Fallback if no trade files found
            if not at_risk:
                at_risk = ["Global Shipping Hubs", "Suez Canal Transit", "Panama Canal Sector"]
                
        except Exception as e:
            print(f"⚠️ Trade Analysis Error: {e}")
            at_risk = ["Regional Port Clusters"]

        return at_risk

    def get_port_friction_map(self):
        """
        Returns the processed port data for the visualizer.
        """
        # If we already ran run_all, we use that data. 
        # If not, we run a quick scan.
        if hasattr(self, 'last_port_map'):
            return self.last_port_map
        
        # Fallback: Run the processor once to build the map
        results = self.run_all()
        self.last_port_map = results.get('port_map', {})
        return self.last_port_map

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
       
        self.last_port_map = port_map
        
        return {
            "alerts": self.get_live_port_alerts(),
            "friction": float(global_avg_friction),
            "port_map": port_map,
            "fatalities": 0,
            "status": "Operational"
        }
