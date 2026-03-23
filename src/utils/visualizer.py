import os
import matplotlib.pyplot as plt
import geopandas as gpd

class SofieVisualizer:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)
        self.world_url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"

    def generate_unified_intel(self, score, at_risk, friction, suffix=""):
        # 1. Setup the Master Canvas (Dark Mode)
        fig = plt.figure(figsize=(20, 12), facecolor='#050505')
        gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1])
        
        # --- PANEL A: GEOPOLITICAL RISK MAP (Top Span) ---
        ax1 = fig.add_subplot(gs[0, :])
        world = gpd.read_file(self.world_url)
        world.plot(ax=ax1, color='#1a1a1a', edgecolor='#333333')
        world[world['NAME'].isin(at_risk)].plot(ax=ax1, color='#ff0033', alpha=0.7)
        ax1.set_title(f"TOP-LEVEL GEOPOLITICAL RISK | NEXUS {suffix}", color='cyan', fontsize=16, pad=20)
        ax1.set_axis_off()

        # --- PANEL B: LOGISTICS FRICTION HEATMAP (Bottom Left) ---
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.set_facecolor('#0a0a0a')
        for port, data in friction.items():
            color = '#ff0033' if data.get('friction', 0) > 3.0 else '#00ff66'
            ax2.scatter(data.get('lon', 0), data.get('lat', 0), s=150, c=color, edgecolors='white', zorder=3)
            ax2.text(data.get('lon', 0)+2, data.get('lat', 0), port.upper(), color='white', fontsize=7)
        ax2.set_title("MARITIME FRICTION NODES", color='white', fontsize=12)
        ax2.grid(color='white', alpha=0.05)

        # --- PANEL C: STABILITY INDEX GAUGE (Bottom Right) ---
        ax3 = fig.add_subplot(gs[1, 1])
        ax3.set_facecolor('#0a0a0a')
        color_gauge = '#00ff66' if score < 40 else '#ffcc00' if score < 70 else '#ff0033'
        
        # Simple Bar Gauge
        ax3.barh(["STABILITY"], [100], color='#222', height=0.4)
        ax3.barh(["STABILITY"], [score], color=color_gauge, height=0.4)
        ax3.text(score + 2, 0, f"{score}%", color=color_gauge, fontsize=24, fontweight='bold', va='center')
        ax3.set_xlim(0, 110)
        ax3.set_title("GLOBAL FRAGILITY INDEX", color='white', fontsize=12)
        ax3.get_yaxis().set_visible(False)

        # 2. Final Export
        plt.tight_layout(pad=5.0)
        filename = f"COMMAND_SITREP_MARCH_23_{suffix}.png"
        save_path = os.path.join(self.output_path, filename)
        plt.savefig(save_path, facecolor='#050505', dpi=150)
        plt.close()
        print(f"-> UNIFIED COMMAND SITREP EXPORTED: {filename}")
