import os
import matplotlib.pyplot as plt
import geopandas as gpd

class LogisticsMapper:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)

    # MUST have 'suffix=""' to match the main.py call
    def generate_heatmap(self, friction_data, suffix=""):
        try:
            fig, ax = plt.subplots(figsize=(15, 8))
            ax.set_facecolor('#000d1a') 
            
            # Sub-logic: Plotting the maritime grid
            for x in range(-180, 181, 30): ax.axvline(x, color='white', alpha=0.05)
            for y in range(-90, 91, 30): ax.axhline(y, color='white', alpha=0.05)
            
            for port, data in friction_data.items():
                color = 'red' if data['friction'] > 3.0 else '#00ff00'
                ax.scatter(data['lon'], data['lat'], s=200, c=color, edgecolors='white', zorder=3)
                ax.text(data['lon']+2, data['lat'], port.upper(), color='white', fontsize=8)

            ax.set_xlim(-180, 180); ax.set_ylim(-60, 85)
            ax.set_title(f"MARITIME FRICTION NODES | {suffix}", color='cyan', loc='left')
            
            # Filename MUST include suffix
            filename = f"logistics_heatmap_march_23_{suffix}.png"
            plt.savefig(os.path.join(self.output_path, filename), facecolor='#000d1a', bbox_inches='tight')
            plt.close()
            print(f"-> Logistics Heatmap Exported: {filename}")
            
        except Exception as e:
            print(f"!! LOGISTICS MAP FAILURE: {e}")
