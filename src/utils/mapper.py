import geopandas as gpd
import matplotlib.pyplot as plt
import os
from geodatasets import get_path # <--- NEW REPLACEMENT

class SofieMapper:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def generate_risk_map(self, at_risk_countries):
        # The new way to get the world map in GeoPandas 1.0+
        path = get_path("naturalearth.lowres")
        world = gpd.read_file(path)
        
        # Match country names to your risk list
        # Note: We use .str.contains or direct match depending on your data
        world['risk_level'] = world['name'].apply(lambda x: 1 if x in at_risk_countries else 0)

        fig, ax = plt.subplots(1, 1, figsize=(15, 8))
        
        # Plotting
        # Grey = Stable/Neutral, Red = At Risk
        world.plot(column='risk_level', ax=ax, cmap='OrRd', edgecolors='black', 
                   linewidth=0.5, legend=False, missing_kwds={'color': 'lightgrey'})
        
        plt.title("SOFIE GLOBAL RISK MAP | NEXUS EVENT: MARCH 22, 2026", 
                  fontsize=16, fontweight='bold', pad=20)
        
        # Add a small note about the 48-hour ultimatum
        ax.annotate('STATION STATUS: CRITICAL WATCH', xy=(0.05, 0.05), 
                    xycoords='axes fraction', fontsize=10, color='red', weight='bold')
        
        ax.axis('off')
        
        map_file = os.path.join(self.output_path, "risk_map_march_22.png")
        plt.savefig(map_file, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"-> Geographic Heatmap Exported: {map_file}")
