import geopandas as gpd
import matplotlib.pyplot as plt
import os
import requests

class LogisticsMapper:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def generate_heatmap(self, friction_dict):
        world_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
        
        try:
            # 1. Fetch map
            response = requests.get(world_url)
            data = response.json()
            world = gpd.GeoDataFrame.from_features(data, crs="EPSG:4326")
            
            # 2. Map the friction data (Median hours in port)
            # We assume friction_dict key is country name
            world['port_delay'] = world['name'].map(friction_dict).fillna(0)

            fig, ax = plt.subplots(1, 1, figsize=(15, 8), facecolor='#0f172a') # Deep Navy
            
            # Base Map
            world.plot(ax=ax, color='#1e293b', edgecolor='#334155', linewidth=0.5)
            
            # Heatmap Layer (Yellow to Purple/Red for delays)
            # High delays = 'Inferno' or 'YlOrRd'
            world[world.port_delay > 0].plot(
                column='port_delay', 
                ax=ax, 
                cmap='YlOrRd', 
                legend=True,
                legend_kwds={'label': "Median Hours in Port", 'orientation': "horizontal", 'shrink': 0.5},
                edgecolor='black',
                linewidth=0.3
            )
            
            plt.title("GLOBAL LOGISTICS FRICTION | PORT PERFORMANCE MARCH 2026", 
                      fontsize=18, fontweight='bold', color='white', pad=20)
            
            ax.axis('off')
            
            map_file = os.path.join(self.output_path, "logistics_heatmap_march_22.png")
            plt.savefig(map_file, dpi=200, bbox_inches='tight', facecolor='#0f172a')
            plt.close()
            print(f"-> Logistics Heatmap Exported: {map_file}")
            
        except Exception as e:
            print(f"!! LOGISTICS MAP FAILURE: {e}")
