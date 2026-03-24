import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap

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
        """Generates a Folium-based HeatMap focusing on global tension zones."""
        try:
            import folium
            from folium.plugins import HeatMap
            import os

            # 1. Initialize Map with Dark Matter tiles
            # Folium handles Lat/Lon naturally, fixing the "one dot" error
            m = folium.Map(
                location=[20, 0], 
                zoom_start=2, 
                tiles='CartoDB dark_matter'
            )

            # 2. Process at_risk data into HeatMap format
            heat_data = []
            for region, data in at_risk.items():
                try:
                    lat = float(data.get('lat', 0))
                    lon = float(data.get('lon', 0))
                    # Weight the 'glow' by the risk score
                    weight = float(data.get('risk_score', 1.0))
                    heat_data.append([lat, lon, weight])
                except:
                    continue

            # 3. Add the HeatMap layer
            if heat_data:
                HeatMap(
                    data=heat_data,
                    radius=25, 
                    blur=15, 
                    min_opacity=0.3,
                    gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
                ).add_to(m)

            # 4. Save the HTML file
            html_path = os.path.join(self.output_path, f"TENSION_MAP_{suffix}.html")
            m.save(html_path)
            
            print(f"✅ TENSION MAP GENERATED: {html_path}")
            return html_path

        except Exception as e:
            print(f"⚠️ Tension Engine Error: {e}")
            return None
