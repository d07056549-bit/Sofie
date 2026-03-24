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
        try:
            import folium
            from folium.plugins import MousePosition
            
            # 1. Initialize a Global Map with a Dark Theme
            # Folium uses Lat/Lon natively - no more manual math!
            m = folium.Map(
                location=[20, 0], 
                zoom_start=2, 
                tiles='CartoDB dark_matter'
            )

            # 2. Add Maritime Nodes (The 803 ports)
            for port, info in friction.items():
                try:
                    lat = float(info.get('lat', 0))
                    lon = float(info.get('lon', 0))
                    f_val = float(info.get('friction', 1.0))

                    # Logic: Red dots for high-friction ($200 oil), Green for stable
                    dot_color = '#00FF41' if f_val <= 1.1 else '#FF4B4B' if f_val >= 1.5 else '#FFA500'

                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=f_val * 4, 
                        color=dot_color,
                        fill=True,
                        fill_color=dot_color,
                        fill_opacity=0.7,
                        popup=f"Port: {port}<br>Friction: {f_val:.2f}",
                        tooltip=port
                    ).add_to(m)
                except: continue

            # 3. Save to HTML
            html_path = os.path.join(self.output_path, f"INTERACTIVE_NEXUS_{suffix}.html")
            m.save(html_path)
            
            print(f"✅ SYSTEM SWAP SUCCESSFUL: {html_path} (Folium Engine)")
            return html_path

        except Exception as e:
            print(f"⚠️ Folium Engine Error: {e}")
            return None
