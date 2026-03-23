import os
import matplotlib.pyplot as plt

class LogisticsMapper:
    def __init__(self, output_path="exports/"):
        self.output_path = os.path.abspath(output_path)
        os.makedirs(self.output_path, exist_ok=True)

    def generate_heatmap(self, friction_data, suffix=""):
        try:
            fig, ax = plt.subplots(figsize=(15, 8))
            ax.set_facecolor('#000d1a') 
            
            for port, data in friction_data.items():
                color = 'red' if data.get('friction', 0) > 3.0 else '#00ff00'
                ax.scatter(data.get('lon', 0), data.get('lat', 0), s=200, c=color, edgecolors='white')

            ax.set_title(f"MARITIME FRICTION | {suffix}", color='cyan')
            
            filename = f"logistics_heatmap_march_23_{suffix}.png"
            plt.savefig(os.path.join(self.output_path, filename), facecolor='#000d1a')
            plt.close()
            print(f"-> Logistics Heatmap Exported: {filename}")
        except Exception as e:
            print(f"!! LOGISTICS FAILURE: {e}")
