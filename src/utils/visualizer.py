import matplotlib.pyplot as plt
import pandas as pd
import os

class SofieVisualizer:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def generate_risk_chart(self, score, data):
        # We are moving to a 3-row layout to fit the trendline
        fig = plt.figure(figsize=(12, 14))
        gs = fig.add_gridspec(3, 2)
        
        fig.suptitle(f"SOFIE INTELLIGENCE DASHBOARD | INDEX: {score}", fontsize=18, fontweight='bold')

        # --- ROW 1: Gauge & Energy ---
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.barh(['Stability'], [100], color='lightgrey')
        ax1.barh(['Stability'], [score], color='red' if score > 70 else 'orange')
        ax1.set_title("Current Fragility Gauge")

        ax2 = fig.add_subplot(gs[0, 1])
        ax2.bar(['Oil Price'], [data['oil_price']], color='black')
        ax2.axhline(y=75, color='green', linestyle='--', label='Baseline')
        ax2.set_title(f"Energy: ${data['oil_price']}/bbl")
        ax2.legend()

        # --- ROW 2: Logistics & Debt ---
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.bar(['Port Friction'], [data['port_friction']], color='darkred')
        ax3.set_title(f"Maritime Friction: {data['port_friction']}x")

        ax4 = fig.add_subplot(gs[1, 1])
        risk_count = data.get('sovereign_risk_entities', 96)
        ax4.pie([risk_count, 195-risk_count], labels=['At Risk', 'Stable'], colors=['#ff4d4d', '#d3d3d3'], autopct='%1.1f%%')
        ax4.set_title("Global Default Risk")

        # --- ROW 3: THE TRENDLINE (NEW) ---
        ax5 = fig.add_subplot(gs[2, :]) # Span both columns
        history_file = os.path.join(self.output_path, "stability_history.csv")
        
        if os.path.exists(history_file):
            df = pd.read_csv(history_file)
            # Take the last 10 runs to keep it clean
            df = df.tail(10)
            ax5.plot(df['Timestamp'], df['Score'], marker='o', linestyle='-', color='blue', linewidth=2)
            ax5.fill_between(df['Timestamp'], df['Score'], color='blue', alpha=0.1)
            ax5.set_ylim(0, 110)
            ax5.set_title("Stability Trend (Last 10 Runs)")
            ax5.tick_params(axis='x', rotation=45)
            ax5.grid(True, linestyle='--', alpha=0.6)
        else:
            ax5.text(0.5, 0.5, "Insufficient History Data", ha='center')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.output_path, "stability_report_march_22.png"))
        plt.close()
        print(f"-> Multi-Trend Dashboard Exported.")
