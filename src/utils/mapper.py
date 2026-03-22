import geopandas as gpd
import matplotlib.pyplot as plt
import os
import requests
import json

class SofieMapper:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def generate_risk_map(self, at_risk_countries):
        # Reliable Raw GeoJSON URL
        world_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
        
        try:
            # 1. Manually fetch the data to ensure no "Unexpected Character" HTML errors
            response = requests.get(world_url, timeout=10)
            if response.status_code != 200:
                raise Exception(f"GitHub returned status {response.status_code}")
            
            # 2. Load the GeoJSON content
            data = response.json()
            world = gpd.GeoDataFrame.from_features(data, crs="EPSG:4326")
            
            # 3. Match country names (The 'name' column is standard in this dataset)
            world['risk_level'] = world['name'].apply(lambda x: 1 if x in at_risk_countries else 0)

            fig, ax = plt.subplots(1, 1, figsize=(15, 8), facecolor='#1e1e1e')
            
            # Base Layer (Dark mode for the War Room)
            world.plot(ax=ax, color='#2d3436', edgecolor='#636e72', linewidth=0.5)
            
            # Risk Layer (Neon Red for high alert)
            world[world.risk_level == 1].plot(ax=ax, color='#ff7675', edgecolor='white', linewidth=1)
            
            plt.title("SOFIE GLOBAL RISK MAP | NEXUS EVENT: MARCH 22, 2026", 
                      fontsize=18, fontweight='bold', color='white', pad=20)
            
            # Conflict Indicator (Strait of Hormuz)
            ax.plot(56, 26, marker='x', color='#0984e3', markersize=12, mew=3, label='Hormuz Blockade')
            # Conflict Indicator (Diego Garcia)
            ax.plot(72, -7, marker='x', color='#0984e3', markersize=12, mew=3, label='Diego Garcia Strike')

            # Status Box
            ax.annotate('DEFCON: 2 - REGIONAL ESCALATION', xy=(0.02, 0.05), 
                        xycoords='axes fraction', fontsize=12, color='#ff7675', 
                        weight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.8))

            ax.axis('off')
            
            map_file = os.path.join(self.output_path, "risk_map_march_22.png")
            plt.savefig(map_file, dpi=200, bbox_inches='tight', facecolor='#1e1e1e')
            plt.close()
            print(f"-> Geographic Heatmap Exported: {map_file}")
            
        except Exception as e:
            print(f"!! MAP ENGINE FAILURE: {e}")
            print("-> Proceeding with standard exports only.")
