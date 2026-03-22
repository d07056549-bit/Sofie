import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import os

class LogisticsMapper:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)

    def generate_heatmap(self, friction_data):
        """Generates a port-specific friction heatmap without aspect errors."""
        try:
            # 1. Silence the downcasting warning
            pd.set_option('future.no_silent_downcasting', True)
            
            # 2. Load World Map
            world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
            
            fig, ax = plt.subplots(figsize=(15, 10))
            
            # Set explicit aspect to prevent the 'finite and positive' crash
            ax.set_aspect('equal') 
            
            world.plot(ax=ax, color='#1a1a1a', edgecolor='#333333')
            
            # 3. Plot Port Data
            for port, data in friction_data.items():
                color = 'red' if data['friction'] > 4.0 else 'orange' if data['friction'] > 2.5 else 'lime'
                ax.scatter(data['lon'], data['lat'], 
                           s=data['friction'] * 50, 
                           c=color, alpha=0.7, edgecolors='white', linewidth=0.5)
                ax.text(data['lon'] + 2, data['lat'], port, color='white', fontsize=8, alpha=0.8)

            ax.set_title("GLOBAL MARITIME LOGISTICS & PORT FRICTION", color='cyan', fontsize=14)
            ax.set_axis_off()
            
            # 4. Save
            plt.savefig(os.path.join(self.output_path, "logistics_heatmap_march_22.png"), 
                        bbox_inches='tight', facecolor='#0d0d0d')
            plt.close()
            print("-> Logistics Heatmap Exported: exports/logistics_heatmap_march_22.png")
            
        except Exception as e:
            print(f"!! LOGISTICS MAP FAILURE: {e}")
