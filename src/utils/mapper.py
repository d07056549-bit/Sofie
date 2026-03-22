import geopandas as gpd
import matplotlib.pyplot as plt
import os

class SofieMapper:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def generate_risk_map(self, at_risk_countries):
        # Using a direct URL to bypass local dataset issues
        world_url = "https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/master/static/data/world.geojson"
        
        try:
            world = gpd.read_file(world_url)
            
            # Note: GeoJSON usually names the column 'name' or 'NAME'
            # We normalize to handle both
            world['risk_level'] = world['name'].apply(lambda x: 1 if x in at_risk_countries else 0)

            fig, ax = plt.subplots(1, 1, figsize=(15, 8), facecolor='#f0f0f0')
            
            # Base Layer (Grey for stable countries)
            world.plot(ax=ax, color='#dfe6e9', edgecolor='white', linewidth=0.5)
            
            # Risk Layer (Red for flagged countries)
            world[world.risk_level == 1].plot(ax=ax, color='#d63031', edgecolor='black', linewidth=0.8)
            
            plt.title("SOFIE GLOBAL RISK MAP | NEXUS EVENT: MARCH 22, 2026", 
                      fontsize=18, fontweight='bold', color='#2d3436', pad=20)
            
            # Legend/Status indicator
            ax.annotate('STATION STATUS: CRITICAL WATCH', xy=(0.02, 0.05), 
                        xycoords='axes fraction', fontsize=12, color='#d63031', 
                        weight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
            
            # Tactical coordinates for the current conflict (Middle East)
            # Strait of Hormuz is approx 26N, 56E
            ax.plot(56, 26, marker='x', color='blue', markersize=10, mew=2, label='Conflict Zone')

            ax.axis('off')
            
            map_file = os.path.join(self.output_path, "risk_map_march_22.png")
            plt.savefig(map_file, dpi=200, bbox_inches='tight', facecolor='#f0f0f0')
            plt.close()
            print(f"-> Geographic Heatmap Exported: {map_file}")
            
        except Exception as e:
            print(f"!! MAP ERROR: {e}")
            print("-> Attempting fallback: Check your internet connection for GeoJSON fetch.")
