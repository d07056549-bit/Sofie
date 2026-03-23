import os
import requests
import matplotlib.pyplot as plt
import geopandas as gpd

class SofieMapper:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)
        # Define the source URL here so it's globally available in the class
        self.world_url = "https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/master/static/data/world.json"

    def generate_risk_map(self, at_risk_list, suffix=""):
        try:
            # 1. Load the world map
            world = gpd.read_file(self.world_url)
            
            # 2. Setup the Plot
            fig, ax = plt.subplots(figsize=(15, 7), facecolor='#0d0d0d')
            world.plot(ax=ax, color='#1a1a1a', edgecolor='#333333')
            
            # 3. Highlight At-Risk Countries
            # (Matches the names in your data_engine list)
            world[world['name'].isin(at_risk_list)].plot(ax=ax, color='red', alpha=0.6)
            
            ax.set_title(f"SOFIE GEOPOLITICAL TENSION MAP | MARCH 23", color='white', fontsize=12)
            ax.set_axis_off()
            
            # 4. Save with Suffix
            filename = f"risk_map_march_23_{suffix}.png"
            output_file = os.path.join(self.output_path, filename)
            
            plt.savefig(output_file, facecolor='#0d0d0d', bbox_inches='tight')
            plt.close()
            print(f"-> Geographic Heatmap Exported: {filename}")
            
        except Exception as e:
            print(f"!! MAPPER FAILURE: {e}")
