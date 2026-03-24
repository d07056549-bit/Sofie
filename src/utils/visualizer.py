import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Safe Interactive Imports
try:
    import holoviews as hv
    import hvplot.pandas
    INTERACTIVE_READY = True
except ImportError:
    INTERACTIVE_READY = False
    print("⚠️ hvplot/holoviews not detected. Interactive mode disabled.")

hv.extension('bokeh')

class SofieVisualizer:
    def __init__(self, output_path=r"C:\Users\Empok\Documents\GitHub\Sofie\Data\exports"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.world_url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
        
    def generate_interactive_nexus(self, at_risk, friction, suffix=""):
        if not INTERACTIVE_READY:
            return None
            
        try:
            # Prepare data
            f_data = []
            for port, info in friction.items():
                f_data.append({
                    'Port': port,
                    'lat': float(info.get('lat', 0)),
                    'lon': float(info.get('lon', 0)),
                    'friction': float(info.get('friction', 1.0))
                })
            df = pd.DataFrame(f_data)

            # Generate Plot
            plot = df.hvplot.points(
                x='lon', y='lat', c='friction', cmap='hot',
                size=hv.dim('friction') * 15, hover_cols=['Port', 'friction'],
                tiles='CartoDark', width=1000, height=600
            )
            
            html_path = f"Data/exports/INTERACTIVE_NEXUS_{suffix}.html"
            hv.save(plot, html_path)
            print(f"✅ INTERACTIVE DASHBOARD: {html_path}")
            return html_path
        except Exception as e:
            print(f"⚠️ Interactive Engine Error: {e}")
            return None
