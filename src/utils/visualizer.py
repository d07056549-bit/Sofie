import matplotlib.pyplot as plt
import os
import geopandas as gpd

class SofieVisualizer:
    def __init__(self, output_path=r"C:\Users\Empok\Documents\GitHub\Sofie\Data\exports"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        # The new stable URL we just found:
        self.world_url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
        
    def generate_unified_intel(self, score, at_risk, friction, alerts, suffix=""):
        import matplotlib.pyplot as plt
        import geopandas as gpd
        import os

        # Standard Colors for Light Mode
        bg_main = '#FFFFFF'
        bg_panel = '#F8F9FA'
        text_color = '#212529'

        # 1. Create the Figure
        fig = plt.figure(figsize=(24, 14), facecolor=bg_main)
        
        # --- PANEL A: GEOPOLITICAL RISK MAP (Top/Center) ---
        ax1 = fig.add_axes([0.05, 0.45, 0.72, 0.45])
        try:
            world = gpd.read_file(self.world_url)
            world.plot(ax=ax1, color='#DEE2E6', edgecolor='#ADB5BD', linewidth=0.5) 
            # Highlight at-risk countries in Crimson
            world[world['NAME'].isin(at_risk)].plot(ax=ax1, color='#DC3545', alpha=0.8)
        except:
            ax1.text(0.5, 0.5, "MAP LAYER OFFLINE", ha='center')
        
        ax1.set_title(f"TOP-LEVEL GEOPOLITICAL RISK | MARCH 2026 NEXUS {suffix.upper()}", 
                      color=text_color, fontsize=24, pad=20, fontweight='bold')
        ax1.set_axis_off()

        # --- PANEL B: MARITIME FRICTION NODES (Bottom Left) ---
        ax2 = fig.add_axes([0.05, 0.1, 0.35, 0.3])
        ax2.set_facecolor(bg_panel)
        # Draw the ports from your CSV data
        for port, data in friction.items():
            f_val = data.get('friction', 1.0)
            color = '#DC3545' if f_val > 1.2 else '#28A745'
            ax2.scatter(data.get('lon', 0), data.get('lat', 0), s=150, c=color, edgecolors='white', zorder=3)
            ax2.text(data.get('lon', 0)+1, data.get('lat', 0), port.upper()[:10], fontsize=8)
        
        ax2.set_title("MARITIME FRICTION NODES", color=text_color, fontsize=16, fontweight='bold')
        ax2.grid(color='#CED4DA', alpha=0.3)

        # --- PANEL C: STABILITY INDEX GAUGE (Bottom Center) ---
        ax3 = fig.add_axes([0.45, 0.1, 0.32, 0.3])
        ax3.set_facecolor(bg_panel)
        color_gauge = '#28A745' if score < 40 else '#FFC107' if score < 70 else '#DC3545'
        ax3.barh(["STABILITY"], [100], color='#E9ECEF', height=0.4)
        ax3.barh(["STABILITY"], [score], color=color_gauge, height=0.4)
        ax3.text(score + 2, 0, f"{score}%", color=color_gauge, fontsize=32, fontweight='bold', va='center')
        ax3.set_title("GLOBAL FRAGILITY INDEX", color=text_color, fontsize=16, fontweight='bold')
        ax3.set_xlim(0, 115)
        ax3.get_yaxis().set_visible(False)

        # --- PANEL D: LIVE PORT ALERTS (Far Right Sidebar) ---
        ax4 = fig.add_axes([0.82, 0.05, 0.15, 0.9]) 
        ax4.set_facecolor('#F1F3F5')
        ax4.set_title("LIVE PORT ALERTS", color='#212529', fontsize=16, fontweight='bold', pad=20)
        
        y_pos = 0.92
        # Keywords that trigger a "Risk" warning (Red)
        risk_keywords = ['strike', 'conflict', 'war', 'shut', 'closed', 'delay', 'attack', 'piracy', 'incident']
        # Keywords that trigger a "Growth" sign (Green)
        growth_keywords = ['expansion', 'new', 'growth', 'opened', 'launch', 'investment', 'record']

        for alert in alerts[:8]:
            title = alert['title'].lower()
            
            # Determine Color based on sentiment
            text_color = '#212529' # Default Black
            if any(word in title for word in risk_keywords):
                text_color = '#DC3545' # Red for Risk
            elif any(word in title for word in growth_keywords):
                text_color = '#28A745' # Green for Growth

            # Draw the title with the new color
            ax4.text(0.05, y_pos, f"• {alert['title'][:45]}...", 
                    transform=ax4.transAxes, fontsize=10, 
                    color=text_color, fontweight='bold', 
                    verticalalignment='top', wrap=True)
            y_pos -= 0.11
            
        ax4.get_xaxis().set_visible(False)
        ax4.get_yaxis().set_visible(False)

        # --- FINAL EXPORT ---
        filename = f"COMMAND_SITREP_MARCH_23_{suffix}.png"
        save_path = os.path.join(self.output_path, filename)
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor=bg_main)
        plt.close()
        
        print(f"✅ SITREP EXPORTED TO: {save_path}")
