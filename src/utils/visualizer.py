import matplotlib.pyplot as plt
import os

class SofieVisualizer:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        # SAFETY CHECK: If the 'exports' folder doesn't exist, create it!
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            print(f"-> System: Created missing directory '{self.output_path}'")

    def generate_risk_chart(self, score):
        """Creates a 'Speedometer' of Global Risk."""
        plt.figure(figsize=(8, 4))
        
        # Simple Gauge Bar logic
        plt.barh(['Global Stability'], [100], color='lightgrey')
        bar_color = 'red' if score > 70 else 'orange'
        plt.barh(['Global Stability'], [score], color=bar_color)
        
        plt.title(f"Sofie v2.0 | Global Risk Level: {score}")
        plt.xlabel("Fragility Index (100 = Total Collapse)")
        plt.xlim(0, 100)
        
        # Save to the exports folder
        file_name = os.path.join(self.output_path, "stability_report_march_22.png")
        plt.savefig(file_name)
        plt.close() # Clean up the memory
        print(f"-> Map Exported: {file_name}")
