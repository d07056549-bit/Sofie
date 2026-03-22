def __init__(self, root_dir="."):
        # We'll use a more flexible pathing logic to find your 'Black Swan' folder
        self.root = root_dir
        
        # Check standard locations
        possible_cyber_paths = [
            os.path.join(self.root, "cybersecurity synthesized data.csv"),
            os.path.join(self.root, "Data/raw/Black Swan/cybersecurity synthesized data.csv"),
            os.path.join(self.root, "Data/raw/cybersecurity synthesized data.csv")
        ]
        
        # Find which one actually exists
        self.cyber_path = next((p for p in possible_cyber_paths if os.path.exists(p)), possible_cyber_paths[0])
        
        # Do the same for Maritime
        self.maritime_path = os.path.join(self.root, "Data/raw/Black Swan/Maritime Port Performance Project Dataset.csv")
        
        print(f"-> Data Engine linked to: {self.cyber_path}")
