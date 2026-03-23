import os
import matplotlib.pyplot as plt
import geopandas as gpd

class SofieMapper:
    def __init__(self, output_path=r"C:\Users\Empok\Documents\GitHub\Sofie\Data\exports"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.world_url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"

    def generate_risk_map(self, at_risk_list, suffix=""):
        try:
            world = gpd.read_file(self.world_url)
            fig, ax = plt.subplots(figsize=(15, 7), facecolor='#0d0d0d')
            world.plot(ax=ax, color='#1a1a1a', edgecolor='#333333')
            
            if at_risk_list:
                world[world['NAME'].isin(at_risk_list)].plot(ax=ax, color='red', alpha=0.6)
            
            ax.set_title(f"SOFIE RISK MAP | {suffix}", color='cyan', fontsize=12)
            ax.set_axis_off()
            
            filename = f"risk_map_march_23_{suffix}.png"
            plt.savefig(os.path.join(self.output_path, filename), facecolor='#0d0d0d')
            plt.close()
            print(f"-> Geographic Heatmap Exported: {filename}")
        except Exception as e:
            print(f"!! MAPPER FAILURE: {e}")
