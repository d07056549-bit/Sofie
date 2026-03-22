def __init__(self, root_dir="."):
        """
        Initializes the Data Engine with Path-Agnostic sensor links.
        Searches for critical CSV files across the project structure.
        """
        import os
        self.root = root_dir
        
        # 1. Define the filename for the Black Swan Cyber Sensor
        cyber_filename = "cybersecurity synthesized data.csv"
        
        # 2. Search Paths: Looks in root, Data subfolders, and parent directories
        search_paths = [
            os.path.join(self.root, cyber_filename), 
            os.path.join(self.root, "Data", "raw", "Black Swan", cyber_filename),
            os.path.join(self.root, "Data", "raw", cyber_filename),
            os.path.join("..", cyber_filename)
        ]
        
        # 3. Link to the first valid path found, or default to root
        self.cyber_path = next((p for p in search_paths if os.path.exists(p)), cyber_filename)
        
        # 4. Maritime Sensor Path
        self.maritime_path = os.path.join(self.root, "Maritime Port Performance Project Dataset.csv")
        
        # 5. SENSOR STATUS CONSOLE LOG
        # This tells you immediately upon 'python main.py' if your data is being read
        if os.path.exists(self.cyber_path):
            print(f"✅ SENSOR ONLINE: Black Swan Cyber Linked to {self.cyber_path}")
        else:
            print(f"❌ SENSOR OFFLINE: {cyber_filename} not found. Using Circuit Breaker Fallbacks.")

        if os.path.exists(self.maritime_path):
            print(f"✅ SENSOR ONLINE: Maritime Logistics Linked to {self.maritime_path}")
        else:
            print(f"⚠️ SENSOR DEGRADED: Maritime Dataset not found.")
