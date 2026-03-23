import os
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import branca.colormap as cm
from matplotlib.colors import LinearSegmentedColormap

class SofieVisualizer:
    def __init__(self, output_path=r"C:\Users\Empok\Documents\GitHub\Sofie\Data\exports"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.world_url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
        
    def generate_unified_intel(self, score, at_risk, friction, alerts, suffix=""):
        # --- FIXED: WIDER GREEN BUFFER ---
        # 0.0 to 0.5 is now the "Green to Lime" zone. 
        # Yellow only starts appearing after 50%.
        colors = ["#1B5E20", "#4CAF50", "#CDDC39", "#FFC107", "#D50000"] # Deep Green, Green, Lime, Gold, Red
        nodes = [0.0, 0.3, 0.5, 0.7, 1.0] 
        sofie_cmap = LinearSegmentedColormap.from_list("sofie_tension", list(zip(nodes, colors)))

        # Standard Colors
        bg_main = '#FFFFFF'
        bg_panel = '#F8F9FA'
        text_color = '#212529'

        # 1. Create the Figure
        fig = plt.figure(figsize=(16, 11), facecolor=bg_main)
        
        # --- PANEL A: WORLD TENSION HEATMAP ---
        ax1 = fig.add_axes([0.05, 0.25, 0.70, 0.70])
        try:
            world = gpd.read_file(self.world_url)
            
            # Map the risk scores
            world['tension'] = world['NAME'].map(at_risk).fillna(0)

            # 2. Plot the Tension Layer using our CUSTOM CMAP
            # vmin/vmax ensures 0 is always Green and 100 is always Red
            world.plot(
                column='tension', 
                ax=ax1, 
                cmap=sofie_cmap, 
                edgecolor='#495057', 
                linewidth=0.3,
                vmin=0, vmax=100,
                legend=True,
                legend_kwds={'label': "Tension Level (%)", 'orientation': "horizontal", 'pad': 0.01}
            )
            
        except Exception as e:
            ax1.text(0.5, 0.5, f"MAP ERROR: {e}", ha='center', color='red')
        
        ax1.set_title(f"WORLD TENSION MAP | MARCH 2026 NEXUS", 
                      color=text_color, fontsize=24, pad=20, fontweight='bold')
        ax1.set_axis_off()

        # --- PANEL B: MARITIME FRICTION NODES ---
        ax2 = fig.add_axes([0.05, 0.05, 0.20, 0.15])
        ax2.set_facecolor(bg_panel)
        for port, data in friction.items():
            f_val = data.get('friction', 1.0)
            color = '#DC3545' if f_val > 1.2 else '#28A745'
            ax2.scatter(data.get('lon', 0), data.get('lat', 0), s=150, c=color, edgecolors='white', zorder=3)
            ax2.text(data.get('lon', 0)+1, data.get('lat', 0), port.upper()[:10], fontsize=8)
        
        ax2.set_title("MARITIME FRICTION NODES", color=text_color, fontsize=16, fontweight='bold')

        # --- PANEL C: STABILITY INDEX GAUGE ---
        ax3 = fig.add_axes([0.30, 0.05, 0.45, 0.15])
        ax3.set_facecolor(bg_panel)
        color_gauge = '#28A745' if score < 40 else '#FFC107' if score < 70 else '#DC3545'
        ax3.barh(["STABILITY"], [100], color='#E9ECEF', height=0.4)
        ax3.barh(["STABILITY"], [score], color=color_gauge, height=0.4)
        ax3.text(score + 2, 0, f"{score}%", color=color_gauge, fontsize=32, fontweight='bold', va='center')
        ax3.set_title("GLOBAL FRAGILITY INDEX", color=text_color, fontsize=16, fontweight='bold')
        ax3.set_xlim(0, 115)
        ax3.get_yaxis().set_visible(False)

        # --- PANEL D: LIVE PORT ALERTS (Sidebar) ---
        ax4 = fig.add_axes([0.78, 0.05, 0.18, 0.90])
        ax4.set_facecolor(bg_panel)
        ax4.set_xticks([]); ax4.set_yticks([])
        ax4.set_title("LIVE PORT ALERTS", color=text_color, fontsize=14, fontweight='bold', pad=15)

        y_pos = 0.95
        risk_keywords = ['threat', 'crisis', 'conflict', 'war', 'strike', 'delay', 'attack', 'blocked']
        for alert in alerts[:12]:
            title_text = alert.get('title', 'No Title')
            clean_title = (title_text[:50] + '..') if len(title_text) > 50 else title_text
            t_color = '#D00000' if any(w in clean_title.lower() for w in risk_keywords) else '#495057'
            ax4.text(0.05, y_pos, f"• {clean_title}", transform=ax4.transAxes, fontsize=9, 
                     color=t_color, fontweight='bold', va='top', wrap=True)
            y_pos -= 0.075

        # --- FINAL EXPORT ---
        filename = f"COMMAND_SITREP_MARCH_23_{suffix}.png"
        save_path = os.path.join(self.output_path, filename)
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor=bg_main)
        plt.close()
        print(f"✅ SITREP EXPORTED TO: {save_path}")
