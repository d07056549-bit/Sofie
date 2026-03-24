import holoviews as hv
import hvplot.pandas
import pandas as pd

hv.extension('bokeh')

class SofieVisualizer:
    def __init__(self, output_path=r"C:\Users\Empok\Documents\GitHub\Sofie\Data\exports"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.world_url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
        
    def generate_interactive_nexus(self, at_risk, friction, suffix=""):
        """
        Cartopy-Free Interactive Dashboard.
        Uses Bokeh + hvPlot for high-speed interactive mapping.
        """
        try:
            # 1. Prepare Maritime Data for Plotting
            # Convert friction dict to a DataFrame
            f_data = []
            for port, info in friction.items():
                f_data.append({
                    'Port': port,
                    'lat': float(info.get('lat', 0)),
                    'lon': float(info.get('lon', 0)),
                    'friction': float(info.get('friction', 1.0))
                })
            df_friction = pd.DataFrame(f_data)

            # 2. Create Interactive Scatter Plot (The 'Nodes')
            # Since we can't use 'geo=True' without Cartopy, 
            # we use a standard scatter with a 'tiles' background.
            plot = df_friction.hvplot.points(
                x='lon', y='lat',
                c='friction',
                cmap='hot',
                size=hv.dim('friction') * 15,
                hover_cols=['Port', 'friction'],
                title=f"SOFIE | INTERACTIVE MARITIME NODES ({suffix})",
                tiles='CartoDark', # This provides the world map background!
                width=1000, height=600,
                xlim=(-180, 180), ylim=(-60, 85)
            )

            # 3. Save as HTML
            html_path = f"Data/exports/INTERACTIVE_NEXUS_{suffix}.html"
            hv.save(plot, html_path)
            
            print(f"✅ INTERACTIVE DASHBOARD GENERATED (Cartopy-Free): {html_path}")
            return html_path

        except Exception as e:
            print(f"⚠️ Interactive Engine Offline: {e}")
            return None
