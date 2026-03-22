import geopandas as gpd
import matplotlib.pyplot as plt
import os

class SofieMapper:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path

    def generate_risk_map(self, at_risk_countries):
        # Load low-resolution world map
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        
        # Create a 'Risk' column: 1 for At Risk, 0 for Stable
        world['risk_level'] = world['name'].apply(lambda x: 1 if x in at_risk_countries else 0)

        fig, ax = plt.subplots(1, 1, figsize=(15, 10))
        world.plot(column='risk_level', ax=ax, cmap='OrRd', edgecolors='black', 
                   legend=False, missing_kwds={'color': 'lightgrey'})
        
        plt.title("SOFIE GLOBAL DEBT CONTAGION MAP | MARCH 22, 2026", fontsize=16, fontweight='bold')
        ax.axis('off')
        
        map_file = os.path.join(self.output_path, "risk_map_march_22.png")
        plt.savefig(map_file, dpi=150)
        plt.close()
        print(f"-> Geographic Heatmap Exported: {map_file}")
