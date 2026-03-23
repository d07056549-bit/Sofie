import os
import matplotlib.pyplot as plt
import geopandas as gpd

class SofieVisualizer:
    def __init__(self, output_path=r"C:\Users\Empok\Documents\GitHub\Sofie\Data\exports"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.world_url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        
    def generate_unified_intel(self, score, at_risk, friction, suffix=""):
        # 1. Setup the Master Canvas (Pure White)
        bg_main = '#FFFFFF'
        bg_panel = '#F8F9FA' # Very light grey for panel separation
        text_color = '#212529' # Dark slate for text
        
        fig = plt.figure(figsize=(20, 12), facecolor=bg_main)
        gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1])
        
        # --- PANEL A: GEOPOLITICAL RISK MAP (Top Span) ---
        ax1 = fig.add_subplot(gs[0, :])
        ax1.set_facecolor(bg_main)
        
        world = gpd.read_file(self.world_url)
        # Professional Slate/Grey map palette
        world.plot(ax=ax1, color='#DEE2E6', edgecolor='#6C757D', linewidth=0.5) 
        world[world['NAME'].isin(at_risk)].plot(ax=ax1, color='#DC3545', alpha=0.8) # Strong Crimson
        
        ax1.set_title(f"TOP-LEVEL GEOPOLITICAL RISK | MARCH 23 NEXUS {suffix}", 
                      color=text_color, fontsize=22, pad=30, fontweight='bold')
        ax1.set_axis_off()

        # --- PANEL B: LOGISTICS FRICTION HEATMAP (Bottom Left) ---
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.set_facecolor(bg_panel)
        for port, data in friction.items():
            color = '#DC3545' if data.get('friction', 0) > 3.0 else '#28A745'
            ax2.scatter(data.get('lon', 0), data.get('lat', 0), s=200, c=color, edgecolors='white', zorder=3)
            ax2.text(data.get('lon', 0)+2, data.get('lat', 0), port.upper(), 
                     color=text_color, fontsize=9, fontweight='semibold')
        
        ax2.set_title("MARITIME FRICTION NODES", color=text_color, fontsize=16, pad=15)
        ax2.grid(color='#CED4DA', alpha=0.3)
        ax2.tick_params(axis='both', colors='#495057')

        # --- PANEL C: STABILITY INDEX GAUGE (Bottom Right) ---
        ax3 = fig.add_subplot(gs[1, 1])
        ax3.set_facecolor(bg_panel)
        color_gauge = '#28A745' if score < 40 else '#FFC107' if score < 70 else '#DC3545'
        
        # Stability Bar
        ax3.barh(["STABILITY"], [100], color='#E9ECEF', height=0.4)
        ax3.barh(["STABILITY"], [score], color=color_gauge, height=0.4)
        ax3.text(score + 2, 0, f"{score}%", color=color_gauge, fontsize=36, fontweight='bold', va='center')
        
        ax3.set_xlim(0, 110)
        ax3.set_title("GLOBAL FRAGILITY INDEX", color=text_color, fontsize=16, pad=15)
        ax3.get_yaxis().set_visible(False)
        ax3.tick_params(axis='x', colors='#495057')

        # 2. Final Export
        plt.tight_layout(pad=6.0)
        filename = f"COMMAND_SITREP_MARCH_23_{suffix}.png"
        plt.savefig(os.path.join(self.output_path, filename), facecolor=bg_main, dpi=150)
        plt.close()
        print(f"-> LIGHT MODE SITREP EXPORTED: {filename}")
