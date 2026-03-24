import holoviews as hv
import hvplot.pandas  # This adds .hvplot() to your GeoDataFrames
import geoviews as gv
from holoviews import opts

hv.extension('bokeh')

class SofieVisualizer:
    def __init__(self, output_path=r"C:\Users\Empok\Documents\GitHub\Sofie\Data\exports"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.world_url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
        
    def generate_interactive_nexus(self, at_risk, friction, suffix=""):
        """Generates an interactive HTML dashboard using HoloViews."""
        try:
            # 1. Load and Prepare Map Data
            world = gpd.read_file(self.world_url)
            iso_col = 'ISO_A3' if 'ISO_A3' in world.columns else 'ADM0_A3'
            world['tension'] = world[iso_col].map(at_risk).fillna(0)
            
            # 2. Create Interactive Choropleth
            # hover_cols allows you to see the country name and score on mouse-over
            map_plot = world.hvplot(
                geo=True, 
                c='tension', 
                cmap='RdYlGn_r', 
                hover_cols=['name', 'tension'],
                title=f"SOFIE Interactive Risk Overlay ({suffix})",
                alpha=0.7,
                clim=(0, 1)
            )

            # 3. Create Maritime Friction Points
            # Convert friction dict to DataFrame for hvPlot
            friction_df = pd.DataFrame.from_dict(friction, orient='index').reset_index()
            friction_df.columns = ['Port', 'lat', 'lon', 'friction']
            
            points_plot = friction_df.hvplot.points(
                x='lon', y='lat', 
                geo=True, 
                color='red', 
                size=hv.dim('friction')*10, # Scale size by friction
                hover_cols=['Port', 'friction']
            )

            # 4. Combine and Save
            interactive_map = (map_plot * points_plot).opts(
                opts.Polygons(width=900, height=500, bgcolor='black'),
                opts.Points(tools=['hover'])
            )
            
            html_path = f"Data/exports/INTERACTIVE_NEXUS_{suffix}.html"
            hv.save(interactive_map, html_path)
            print(f"✅ INTERACTIVE DASHBOARD: {html_path}")
            return html_path

        except Exception as e:
            print(f"⚠️ HoloViews Engine Failure: {e}")
            return None
