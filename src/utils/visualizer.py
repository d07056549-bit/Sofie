import matplotlib.pyplot as plt
import os

class SofieVisualizer:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        if not os.path.exists(self.output_path): os.makedirs(self.output_path)

    def generate_risk_chart(self, score, data):
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f"SOFIE INTELLIGENCE DASHBOARD | {score}", fontsize=16, fontweight='bold')

        # Gauge
        axs[0, 0].barh(['Stability'], [100], color='lightgrey')
        axs[0, 0].barh(['Stability'], [score], color='red' if score > 70 else 'orange')
        axs[0, 0].set_title("Overall Fragility Index")

        # Oil
        axs[0, 1].bar(['Oil Price'], [data['oil_price']], color='black')
        axs[0, 1].axhline(y=75, color='green', linestyle='--', label='Baseline')
        axs[0, 1].set_title(f"Energy: ${data['oil_price']}")

        # Friction
        axs[1, 0].bar(['Port Friction'], [data['port_friction']], color='darkred')
        axs[1, 0].set_title(f"Logistics: {data['port_friction']}x")

        # Debt Pie
        risk_count = data.get('sovereign_risk_entities', 96)
        axs[1, 1].pie([risk_count, 195-risk_count], labels=['At Risk', 'Stable'], colors=['red', 'grey'])
        axs[1, 1].set_title(f"Sovereign Risk ({risk_count} Nations)")

        plt.savefig(os.path.join(self.output_path, "stability_report_march_22.png"))
        plt.close()
