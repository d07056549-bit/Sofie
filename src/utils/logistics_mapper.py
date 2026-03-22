import matplotlib.pyplot as plt
import pandas as pd
import os

class LogisticsMapper:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)

    def generate_heatmap(self, friction_data):
        """Generates a high-fidelity logistics map without relying on deprecated datasets."""
        try:
            fig, ax = plt.subplots(figsize=(15, 8))
            ax.set_facecolor('#000d1a') # Deep Intelligence Blue
            
            # --- Draw a 'Digital Grid' instead of a heavy map ---
            for x in range(-180, 181, 30):
                ax.axvline(x, color='white', alpha=0.05, linewidth=0.5)
            for y in range(-90, 91, 30):
                ax.axhline(y, color='white', alpha=0.05, linewidth=0.5)
            
            # --- Plot Port Data with custom icons ---
            for port, data in friction_data.items():
                # Color logic: Green to Red based on friction
                color = 'red' if data['friction'] > 4.0 else 'orange' if data['friction'] > 2.5 else '#00ff00'
                
                # Plot the 'Node'
                ax.scatter(data['lon'], data['lat'], 
                           s=data['friction'] * 100, 
                           c=color, alpha=0.6, edgecolors='white', linewidth=1, zorder=3)
                
                # Add a 'Pulse' effect around high friction ports
                if data['friction'] > 3.5:
                    ax.scatter(data['lon'], data['lat'], s=data['friction'] * 400, 
                               c=color, alpha=0.1, zorder=2)
                
                # Label
                ax.text(data['lon'] + 3, data['lat'], f"{port.upper()}\n[{data['friction']} FRIC]", 
                        color='white', fontsize=9, fontfamily='monospace', va='center')

            ax.set_xlim(-180, 180)
            ax.set_ylim(-60, 85)
            ax.set_title("SOFIE LOGISTICS INTELLIGENCE: MARITIME NODE FRICTION", 
                         color='cyan', fontsize=12, loc='left', pad=20)
            
            # Remove axes for a clean 'Cyber' look
            ax.set_xticks([]); ax.set_yticks([])
            for spine in ax.spines.values(): spine.set_visible(False)
            
            # 4. Save
            plt.savefig(os.path.join(self.output_path, "logistics_heatmap_march_22.png"), 
                        bbox_inches='tight', facecolor='#000d1a')
            plt.close()
            print("-> Logistics Heatmap Exported: exports/logistics_heatmap_march_22.png")
            
        except Exception as e:
            print(f"!! LOGISTICS MAP FAILURE: {e}")
