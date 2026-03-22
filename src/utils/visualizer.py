import matplotlib.pyplot as plt

class SofieVisualizer:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path

    def generate_risk_chart(self, score):
        """Creates a 'Speedometer' of Global Risk."""
        plt.figure(figsize=(8, 4))
        colors = ['green', 'yellow', 'orange', 'red']
        
        # Simple Gauge Bar
        plt.barh(['Global Stability'], [100], color='lightgrey')
        bar_color = 'red' if score > 70 else 'orange'
        plt.barh(['Global Stability'], [score], color=bar_color)
        
        plt.title(f"Sofie v2.0 | Global Risk Level: {score}")
        plt.xlabel("Fragility Index (100 = Total Collapse)")
        plt.xlim(0, 100)
        
        file_name = f"{self.output_path}stability_report_march_22.png"
        plt.savefig(file_name)
        print(f"-> Map Exported: {file_name}")
