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
        # Style Settings
        plt.style.use('dark_background')
        bg_panel = '#0A0A0A'
        accent_color = '#00FF41'  # Matrix Green
        text_color = '#E0E0E0'
        
        fig = plt.figure(figsize=(24, 14), facecolor='black')
        
        # --- PANEL A: GLOBAL RISK MAP (ISO-BASED) ---
        ax1 = fig.add_axes([0.05, 0.25, 0.90, 0.70])
        try:
            import geopandas as gpd
            # Load map
            world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
            
            # --- START ISO FIX ---
            # Most Natural Earth files use 'ADM0_A3' or 'ISO_A3'
            iso_col = 'ISO_A3' if 'ISO_A3' in world.columns else 'ADM0_A3'
            
            # We map the 'at_risk' dictionary (which now contains ISO codes) 
            # to the map's ISO column.
            world['tension'] = world[iso_col].map(at_risk).fillna(0)
            # --- END ISO FIX ---

            world.plot(
                column='tension',
                ax=ax1,
                cmap='RdYlGn_r', # Red for High Tension, Green for Low
                linewidth=0.5,
                edgecolor='0.2',
                legend=False,
                missing_kwds={'color': '#1A1A1A'} # Dark gray for countries with no data
            )
        except Exception as e:
            ax1.text(0.5, 0.5, f"MAP SENSOR OFFLINE: {e}", ha='center', color='red')
        
        ax1.set_axis_off()
        ax1.set_title(f"SOFIE | QUAD-NEXUS STRATEGIC OVERLAY", color=accent_color, fontsize=28, fontweight='bold', pad=20)

        # --- PANEL B: MARITIME FRICTION NODES (Fixed & Robust) ---
        ax2 = fig.add_axes([0.05, 0.05, 0.20, 0.15])
        ax2.set_facecolor(bg_panel)
        
        # Plotting the ports
        for port, data in friction.items():
            try:
                lon, lat = float(data.get('lon', 0)), float(data.get('lat', 0))
                f_val = float(data.get('friction', 1.0))
                
                # Determine color based on friction level
                p_color = '#DC3545' if f_val > 1.2 else '#28A745'
                ax2.scatter(lon, lat, s=120, c=p_color, edgecolors='white', zorder=5)
                
                if f_val > 1.1: # Only label friction points
                    ax2.text(lon + 3, lat, port.upper()[:10], fontsize=8, color=text_color, fontweight='bold')
            except:
                continue

        ax2.set_xlim(-180, 180) # Force global scaling
        ax2.set_ylim(-60, 85)
        ax2.set_axis_off()
        ax2.set_title("MARITIME FRICTION NODES", color=text_color, fontsize=14, fontweight='bold')

        # --- PANEL C: STABILITY GAUGE ---
        ax3 = fig.add_axes([0.30, 0.05, 0.30, 0.15])
        ax3.set_facecolor(bg_panel)
        # Create a simple gauge bar
        ax3.barh(0, 100, color='#1A1A1A', height=0.4)
        ax3.barh(0, score, color=accent_color, height=0.4)
        ax3.text(50, 0, f"{score:.2f}%", ha='center', va='center', fontsize=30, color='black', fontweight='bold')
        ax3.set_axis_off()
        ax3.set_title("SYSTEM STABILITY INDEX", color=text_color, fontsize=14, fontweight='bold')

        # --- PANEL D: LIVE ALERTS (Universal Data Fix) ---
        ax4 = fig.add_axes([0.65, 0.05, 0.30, 0.15])
        ax4.set_facecolor(bg_panel)
        y_pos = 0.8
        ax4.text(0.05, 0.9, "ACTIVE STRATEGIC ALERTS:", color=accent_color, fontsize=12, fontweight='bold')
        
        if alerts and isinstance(alerts, list):
            for alert in alerts[:4]:
                # 1. Extract text if it's a dictionary, otherwise force to string
                if isinstance(alert, dict):
                    # Try to find a 'message' or 'event' key, else just stringify the dict
                    text = alert.get('message', alert.get('event', str(alert)))
                else:
                    text = str(alert)
                
                # 2. Safely slice the text for the display
                display_text = text[:50] + "..." if len(text) > 50 else text
                
                ax4.text(0.05, y_pos, f"> {display_text}", color=text_color, fontsize=10, family='monospace')
                y_pos -= 0.2
        else:
            ax4.text(0.05, 0.7, "> SENSORS SCANNING...", color=text_color, fontsize=10)
            
        ax4.set_axis_off()

        # Save output
        save_path = f"Data/exports/COMMAND_SITREP_{suffix}.png"
        plt.savefig(save_path, facecolor='black', edgecolor='none', dpi=100)
        plt.close()
        return save_path
