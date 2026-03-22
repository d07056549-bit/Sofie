import matplotlib.pyplot as plt
import os

class SofieVisualizer:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def generate_risk_chart(self, score, data):
        # Create a figure with 2 rows and 2 columns
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f"SOFIE INTELLIGENCE DASHBOARD | MARCH 22, 2026\nGlobal Fragility Index: {score}", fontsize=16, fontweight='bold')

        # --- TOP LEFT: Global Stability Gauge ---
        bar_color = 'red' if score > 70 else 'orange'
        axs[0, 0].barh(['Stability'], [100], color='lightgrey')
        axs[0, 0].barh(['Stability'], [score], color=bar_color)
        axs[0, 0].set_title("Overall Fragility Index")
        axs[0, 0].set_xlim(0, 100)

        # --- TOP RIGHT: Energy Shock ---
        # Baseline is $75 (Pre-Crisis)
        oil_val = data.get('oil_price', 0)
        axs[0, 1].bar(['Current Oil'], [oil_val], color='black')
        axs[0, 1].axhline(y=75, color='green', linestyle='--', label='Baseline ($75)')
        axs[0, 1].set_title(f"Energy Price: ${oil_val}/bbl")
        axs[0, 1].set_ylabel("USD per Barrel")
        axs[0, 1].legend()

        # --- BOTTOM LEFT: Logistics Friction ---
        # 1.0 is normal flow. 
        friction = data.get('port_friction', 1.0)
        f_color = 'darkred' if friction > 2.0 else 'orange'
        axs[1, 0].bar(['Port Friction'], [friction], color=f_color)
        axs[1, 0].axhline(y=1.0, color='blue', linestyle='--', label='Normal Flow')
        axs[1, 0].set_title(f"Maritime Friction: {friction:.2f}x")
        axs[1, 0].set_ylim(0, max(4, friction + 1))
        axs[1, 0].legend()

        # --- BOTTOM RIGHT: Sovereign Vulnerability ---
        entities = data.get('sovereign_risk_entities', 0)
        axs[1, 1].pie([entities, 195-entities], 
                      labels=['At Risk', 'Stable'], 
                      colors=['red', 'lightgrey'], 
                      autopct='%1.1f%%', startangle=140)
        axs[1, 1].set_title(f"Sovereign Debt Risk ({entities} Entities)")

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        file_name = os.path.join(self.output_path, "stability_report_march_22.png")
        plt.savefig(file_name)
        plt.close()
        print(f"-> Dashboard Exported: {file_name}")
