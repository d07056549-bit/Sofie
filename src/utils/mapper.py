import os
import matplotlib.pyplot as plt
import geopandas as gpd

class SofieMapper:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)
        # RELIABLE URL FOR WORLD DATA
        self.world_url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"

    def generate_risk_map(self, at_risk_list, suffix=""):
        try:
            # 1. Load the world map from the reliable ZIP URL
            world = gpd.read_file(self.world_url)
            
            # 2. Setup the Plot
            fig, ax = plt.subplots(figsize=(15, 7), facecolor='#0d0d0d')
            world.plot(ax=ax, color='#1a1a1a', edgecolor='#333333')
            
            # 3. Highlight At-Risk Countries
            # Note: Ensure country names in your data match Natural Earth names (e.g. 'United States of America')
            world[world['NAME'].isin(at_risk_list)].plot(ax=ax, color='red', alpha=0.6)
            
            ax.set_title(f"SOFIE GEOPOLITICAL TENSION MAP | MARCH 23", color='cyan', fontsize=12, loc='left')
            ax.set_axis_off()
            
            # 4. Save with Suffix
            filename = f"risk_map_march_23_{suffix}.png"
            output_file = os.path.join(self.output_path, filename)
            
            plt.savefig(output_file, facecolor='#0d0d0d', bbox_inches='tight', dpi=150)
            plt.close()
            print(f"-> Geographic Heatmap Exported: {filename}")
            
        except Exception as e:
            print(f"!! MAPPER FAILURE: {e}")
