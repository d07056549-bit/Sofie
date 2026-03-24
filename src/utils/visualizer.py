import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# --- SAFE INTERACTIVE IMPORTS ---
try:
    import holoviews as hv
    import hvplot.pandas
    # Initialize HoloViews with Bokeh
    hv.extension('bokeh')
    INTERACTIVE_READY = True
except ImportError:
    INTERACTIVE_READY = False
    print("⚠️ hvplot/holoviews not detected. Interactive mode disabled.")

class SofieVisualizer:
    def __init__(self, output_path=r"C:\Users\Empok\Documents\GitHub\Sofie\Data\exports"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.world_url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"

    # --- THE MISSING METHOD (Line 228 Fix) ---
    def generate_unified_intel(self, score, at_risk, friction, alerts, suffix="", displacement_map=None):
        """Generates the Static PNG Sitrep Dashboard."""
        plt.style.use('dark_background')
        bg_panel = '#0A0A0A'
        accent_color = '#00FF41'  # Matrix Green
        text_color = '#E0E0E0'
        
        fig = plt.figure(figsize=(24, 14), facecolor='black')
        
        # Panel A: Global Risk Map
        ax1 = fig.add_axes([0.05, 0.25, 0.90, 0.70])
        try:
            world = gpd.read_file(self.world_url)
            iso_col = 'ISO_A3' if 'ISO_A3' in world.columns else 'ADM0_A3'
            world['tension'] = world[iso_col].map(at_risk).fillna(0)
            world.plot(column='tension', ax=ax1, cmap='RdYlGn_r', linewidth=0.5, edgecolor='0.2', missing_kwds={'color': '#1A1A1A'})
        except Exception as e:
            ax1.text(0.5, 0.5, f"MAP OFFLINE: {e}", ha='center', color='red')
        
        ax1.set_axis_off()
        ax1.set_title(f"SOFIE | STRATEGIC SITREP ({suffix})", color=accent_color, fontsize=28, fontweight='bold')

        # Panel B: Maritime Nodes
        ax2 = fig.add_axes([0.05, 0.05, 0.20, 0.15])
        ax2.set_facecolor(bg_panel)
        for port, data in friction.items():
            try:
                lon, lat = float(data.get('lon', 0)), float(data.get('lat', 0))
                f_val = float(data.get('friction', 1.0))
                p_color = '#DC3545' if f_val > 1.2 else '#28A745'
                ax2.scatter(lon, lat, s=120, c=p_color, edgecolors='white')
            except: continue
        ax2.set_axis_off()

        # Panel C: Stability Gauge
        ax3 = fig.add_axes([0.30, 0.05, 0.30, 0.15])
        ax3.barh(0, 100, color='#1A1A1A', height=0.4)
        ax3.barh(0, score, color=accent_color, height=0.4)
        ax3.text(50, 0, f"{score:.2f}%", ha='center', va='center', fontsize=30, color='black', fontweight='bold')
        ax3.set_axis_off()

        # Save Static PNG
        save_path = os.path.join(self.output_path, f"COMMAND_SITREP_{suffix}.png")
        plt.savefig(save_path, facecolor='black', edgecolor='none', dpi=100)
        plt.close()
        return save_path

    # --- NEW INTERACTIVE METHOD ---
    def generate_interactive_nexus(self, at_risk, friction, suffix=""):
        if not INTERACTIVE_READY:
            return None
        try:
            # 1. Prepare simple Lat/Lon data (NO manual math needed)
            f_data = []
            for port, info in friction.items():
                try:
                    f_data.append({
                        'Port': port,
                        'lat': float(info.get('lat', 0)),
                        'lon': float(info.get('lon', 0)),
                        'friction': float(info.get('friction', 1.0))
                    })
                except: continue
            
            df = pd.DataFrame(f_data)

            # 2. Use 'geo=True' and 'tiles'. 
            # hvPlot will auto-project these points to match the map!
            plot = df.hvplot.points(
                x='lon', y='lat',
                geo=True,             # <--- This is the magic key
                tiles='CartoDark',    # <--- This brings back the map
                c='friction', 
                cmap='hot',
                size=hv.dim('friction') * 15,
                hover_cols=['Port', 'friction'],
                width=1000, height=600,
                title=f"SOFIE INTERACTIVE NEXUS | {suffix}"
            )
            
            html_path = os.path.join(self.output_path, f"INTERACTIVE_NEXUS_{suffix}.html")
            hv.save(plot, html_path)
            print(f"✅ INTERACTIVE MAP RESTORED: {html_path}")
            return html_path

        except Exception as e:
            print(f"⚠️ Interactive Engine Error: {e}")
            # If geo=True fails because of an old version, fall back to basic
            return None
