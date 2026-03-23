import os
import matplotlib.pyplot as plt
import geopandas as gpd

class SofieVisualizer:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)
        self.world_url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"

    def generate_unified_intel(self, score, at_risk, friction, suffix=""):
        # 1. Setup the Master Canvas (Gunmetal Grey instead of pure black)
        master_bg = '#212529'
        panel_bg = '#343a40'
        
        fig = plt.figure(figsize=(20, 12), facecolor=master_bg)
        gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1])
        
        # --- PANEL A: GEOPOLITICAL RISK MAP (Top Span) ---
        ax1 = fig.add_subplot(gs[0, :])
        ax1.set_facecolor(master_bg) # Sync map background to master
        
        world = gpd.read_file(self.world_url)
        # Use lighter, higher-contrast land and borders
        world.plot(ax=ax1, color='#495057', edgecolor='#ADB5BD') 
        world[world['NAME'].isin(at_risk)].plot(ax=ax1, color='#FF4B4B', alpha=0.9) # Saturated red
        
        # 'Loc=center' and bigger padding for the title
        ax1.set_title(f"TOP-LEVEL GEOPOLITICAL RISK | MARCH 23 NEXUS {suffix}", 
                      color='white', fontsize=20, pad=30, fontweight='bold', loc='center')
        ax1.set_axis_off()

        # --- PANEL B: LOGISTICS FRICTION HEATMAP (Bottom Left) ---
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.set_facecolor(panel_bg)
        for port, data in friction.items():
            color = '#FF4B4B' if data.get('friction', 0) > 3.0 else '#00E676'
            ax2.scatter(data.get('lon', 0), data.get('lat', 0), s=200, c=color, edgecolors='white', zorder=3)
            # Use white text for labels
            ax2.text(data.get('lon', 0)+2, data.get('lat', 0), port.upper(), 
                     color='white', fontsize=8, fontweight='bold')
        ax2.set_title("MARITIME FRICTION NODES", color='white', fontsize=14, pad=15)
        ax2.grid(color='#ADB5BD', alpha=0.1) # Lighter grid lines
        ax2.tick_params(axis='both', colors='white') # White axis numbers

        # --- PANEL C: STABILITY INDEX GAUGE (Bottom Right) ---
        ax3 = fig.add_subplot(gs[1, 1])
        ax3.set_facecolor(panel_bg)
        color_gauge = '#00E676' if score < 40 else '#FFD600' if score < 70 else '#FF4B4B'
        
        # Simple Bar Gauge
        ax3.barh(["STABILITY"], [100], color='#212529', height=0.4)
        ax3.barh(["STABILITY"], [score], color=color_gauge, height=0.4)
        ax3.text(score + 2, 0, f"{score}%", color=color_gauge, fontsize=32, fontweight='bold', va='center')
        ax3.set_xlim(0, 110)
        ax3.set_title("GLOBAL FRAGILITY INDEX", color='white', fontsize=14, pad=15)
        ax3.get_yaxis().set_visible(False)
        ax3.tick_params(axis='x', colors='white') # White numbers on bottom

        # 2. Final Export
        plt.tight_layout(pad=6.0) # Increased padding between panels
        filename = f"COMMAND_SITREP_MARCH_23_{suffix}.png"
        plt.savefig(os.path.join(self.output_path, filename), facecolor=master_bg, dpi=150)
        plt.close()
        print(f"-> HIGH-CONTRAST SITREP EXPORTED: {filename}")
