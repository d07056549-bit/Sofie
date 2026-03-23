def __init__(self, root_dir="."):
        """
        Initializes the Data Engine with Path-Agnostic sensor links.
        Focuses on Maritime and Stability datasets for Nexus v2.0.
        """
        import os
        self.root = root_dir
        
        # 1. DEFINE FILE NAMES
        maritime_filename = "Maritime Port Performance Project Dataset.csv"
        stability_filename = "stability_history.csv" # For your history tracking

        # 2. DEFINE SEARCH PATHS (Looking for the Maritime data)
        search_paths = [
            os.path.join(self.root, maritime_filename),
            os.path.join(self.root, "Data", "raw", maritime_filename),
            os.path.join(self.root, "Data", maritime_filename),
            os.path.join("..", maritime_filename)
        ]

        # 3. LINK TO THE FIRST VALID PATH FOUND
        self.maritime_path = next((p for p in search_paths if os.path.exists(p)), maritime_filename)
        self.history_path = os.path.join("exports", stability_filename)

        # 4. SENSOR STATUS CONSOLE LOG
        print("\n--- SENSOR STATUS REPORT ---")
        if os.path.exists(self.maritime_path):
            print(f"✅ SENSOR ONLINE: Maritime Logistics Linked to {self.maritime_path}")
        else:
            print(f"❌ SENSOR OFFLINE: {maritime_filename} NOT FOUND. Using Circuit Breaker Fallbacks.")

        if os.path.exists(self.history_path):
            print(f"✅ DATA LINKED: Stability History detected in /exports")
        else:
            print(f"⚠️ DATA INITIALIZING: Creating new History log on first run.")
        print("----------------------------\n")
