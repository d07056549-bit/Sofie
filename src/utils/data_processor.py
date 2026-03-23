import os
import feedparser
import pandas as pd

class SofieDataEngine:
    def __init__(self, root_dir="."):
        self.root = root_dir
        # We only define what we actually HAVE
        self.paths = {
            "maritime": os.path.join(self.root, "Data", "Maritime Port Performance Project Dataset.csv")
        }

    def get_live_port_alerts(self):
        """Scrapes the live maritime feed"""
        feed_url = "https://www.maritime-executive.com/rss"
        try:
            feed = feedparser.parse(feed_url)
            return [{"title": e.title, "summary": e.summary[:100]} for e in feed.entries[:5]]
        except:
            return [{"title": "Feed Offline", "summary": "Direct CSV data only."}]

    def run_all(self):
        """Cleaned version: No more cyber checks"""
        print(">>> ENGINE STARTING: Processing Maritime & Trade Streams...")
        
        # Check for our actual data file
        if os.path.exists(self.paths["maritime"]):
            print("✅ MARITIME SENSOR: Online")
        else:
            print("❌ MARITIME SENSOR: Data File Missing at " + self.paths["maritime"])

        # This now returns alerts to the visualizer
        return {
            "alerts": self.get_live_port_alerts(),
            "status": "Operational"
        }
