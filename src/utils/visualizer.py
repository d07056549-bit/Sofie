import matplotlib.pyplot as plt
import os

class SofieVisualizer:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def generate_risk_chart(self, score, current_data):
        # --- BLACK SWAN VISUAL LOGIC ---
        # If the score is over 100, we shift to 'Overload' colors
        if score > 100:
            bg_color = '#1e1b4b' # Deep Cosmic Purple
            accent_color = '#f472b6' # Neon Pink
            title_prefix = "!!! BLACK SWAN OVERLOAD !!!"
        else:
            bg_color = '#0f172a' # Standard Deep Navy
            accent_color = '#ef4444' # Standard Red
            title_prefix = "GLOBAL FRAGILITY MONITOR"

        # Initialize the Plot
        fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
        ax.set_facecolor(bg_color)

        # Basic Gauge Logic (Simplified for brevity)
        plt.title(f"{title_prefix}\nMARCH 22, 2026", color='white', fontsize=14, fontweight='bold')
        
        # Add the score text in the center
        plt.text(0.5, 0.5, f"{score}", transform=ax.transAxes, 
                 fontsize=60, color=accent_color, ha='center', fontweight='bold')
        
        plt.text(0.5, 0.3, "STABILITY INDEX", transform=ax.transAxes, 
                 fontsize=12, color='white', ha='center')

        # Cleanup and Save
        ax.axis('off')
        report_file = os.path.join(self.output_path, "stability_report_march_22.png")
        plt.savefig(report_file, dpi=150, facecolor=bg_color)
        plt.close()
        print(f"-> Multi-Panel Intelligence Dashboard Exported: {report_file}")
