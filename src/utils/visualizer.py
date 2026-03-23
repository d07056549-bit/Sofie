import matplotlib.pyplot as plt
import os
class SofieVisualizer:
    def __init__(self, output_path=r"C:\Users\Empok\Documents\GitHub\Sofie\Data\exports"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        # The new stable URL we just found:
        self.world_url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
        
   def generate_unified_intel(self, score, at_risk, friction, alerts, suffix=""):
        import matplotlib.pyplot as plt
        import os
        
       # 1. Create the Figure
        fig = plt.figure(figsize=(20, 12), facecolor='#FFFFFF')
        
      # --- PANEL A: Global Stability Gauge (Top Left) ---
        # [left, bottom, width, height]
        ax1 = fig.add_axes([0.05, 0.7, 0.25, 0.25]) 
        ax1.set_title("GLOBAL STABILITY INDEX", fontweight='bold', pad=15)
        # ... (gauge code follows) ...

       # --- PANEL B: Top Risk Entities (Middle Left) ---
        ax2 = fig.add_axes([0.05, 0.4, 0.25, 0.25])
        ax2.set_title("TOP RISK ENTITIES", fontweight='bold')
        # ... (risk list code follows) ...

      # 2. Load the Map (Panel C)
        try:
            # This uses the stable S3 Amazon link we just swapped
            world = gpd.read_file(self.world_url)
            ax3 = fig.add_axes([0.35, 0.1, 0.45, 0.85])
            world.plot(ax=ax3, color='#E9ECEF', edgecolor='#DEE2E6')
            ax3.set_axis_off()
        except Exception as e:
            print(f"⚠️ Map Download Failed: {e}. Drawing blank theater.")
            ax3 = fig.add_axes([0.35, 0.1, 0.45, 0.85])
            ax3.set_title("GEOSPATIAL LAYER: OFFLINE")

      # --- PANEL D: LIVE PORT ALERTS (Sidebar) ---
        ax4 = fig.add_axes([0.82, 0.1, 0.15, 0.8]) 
        ax4.set_facecolor('#F8F9FA')
        ax4.set_title("LIVE PORT ALERTS", fontsize=14, fontweight='bold', pad=20)
        
        y_pos = 0.9
        for alert in alerts[:6]: # Show top 6 news items
            ax4.text(0.05, y_pos, f"• {alert['title'][:40]}...", 
                    transform=ax4.transAxes, fontsize=9, verticalalignment='top', wrap=True)
            y_pos -= 0.12
            
        ax4.get_xaxis().set_visible(False)
        ax4.get_yaxis().set_visible(False)
        
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
        filename = f"COMMAND_SITREP_MARCH_23_{suffix}.png"
        save_path = os.path.join(self.output_path, filename)
        plt.savefig(os.path.join(self.output_path, filename), dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"-> LIGHT MODE SITREP EXPORTED: {filename}")
