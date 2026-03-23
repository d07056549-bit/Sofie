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
        fig = plt.figure(figsize=(16, 11), facecolor='#121212')
        
        # --- PANEL A: GEOPOLITICAL RISK MAP (Top/Center) ---
        ax1 = fig.add_axes([0.05, 0.25, 0.70, 0.70])
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
        ax2 = fig.add_axes([0.05, 0.05, 0.20, 0.15])
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
        ax4.set_facecolor('#F8F9FA') # Clean light grey
        ax4.set_xticks([])
        ax4.set_yticks([])
        ax4.set_title("LIVE PORT ALERTS", color='#212529', fontsize=14, fontweight='bold', pad=15)

        y_pos = 0.95
        risk_keywords = ['threat', 'crisis', 'conflict', 'war', 'strike', 'delay', 'attack', 'blocked']
        
        # This loop is where the magic happens
        for alert in alerts[:10]: # Draw up to 10 alerts
            title_text = alert.get('title', 'No Title Available')
            clean_title = (title_text[:55] + '..') if len(title_text) > 55 else title_text
            
            # Sentiment Color Logic
            text_color = '#495057' # Default dark grey
            if any(word in clean_title.lower() for word in risk_keywords):
                text_color = '#D00000' # High Alert Red

            # DRAWING THE TEXT
            ax4.text(0.05, y_pos, f"• {clean_title}", 
                    transform=ax4.transAxes, 
                    fontsize=9, 
                    color=text_color, 
                    fontweight='bold',
                    va='top', 
                    ha='left',
                    wrap=True)
            
            y_pos -= 0.09
            
        ax4.get_xaxis().set_visible(False)
        ax4.get_yaxis().set_visible(False)

        # --- FINAL EXPORT ---
        filename = f"COMMAND_SITREP_MARCH_23_{suffix}.png"
        save_path = os.path.join(self.output_path, filename)
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor=bg_main)
        plt.close()
        
        print(f"✅ SITREP EXPORTED TO: {save_path}")
