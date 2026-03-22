import matplotlib.pyplot as plt
import pandas as pd
import os

class SofieVisualizer:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path
        # Ensure the export directory exists
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def generate_risk_chart(self, score, data):
        """Generates a multi-panel intelligence dashboard for the current scenario."""
        # Create a tall figure to accommodate the news feed at the bottom
        fig = plt.figure(figsize=(14, 16))
        gs = fig.add_gridspec(4, 2, height_ratios=[1, 1, 1, 0.6])
        
        fig.suptitle(f"SOFIE INTELLIGENCE DASHBOARD | GLOBAL FRAGILITY: {score}", 
                     fontsize=22, fontweight='bold', y=0.98)

        # If the score is over 100, we color the dashboard 'Neon Purple' (The Black Swan Color)
        bg_color = '#0f172a' # Default Navy
        if score > 100:
        bg_color = '#1e1b4b' # Deep Cosmic Purple
        print("OVERLOAD: Stability Index has exceeded human-readable limits.")

        # --- PANEL 1: STABILITY GAUGE (Top Left) ---
        ax1 = fig.add_subplot(gs[0, 0])
        color = '#d63031' if score > 70 else '#fdcb6e'
        ax1.barh(['Stability'], [100], color='#dfe6e9')
        ax1.barh(['Stability'], [score], color=color)
        ax1.set_xlim(0, 100)
        ax1.set_title("Current Fragility Index", fontsize=14, fontweight='bold')
        ax1.grid(axis='x', linestyle='--', alpha=0.3)

        # --- PANEL 2: ENERGY SHOCK (Top Right) ---
        ax2 = fig.add_subplot(gs[0, 1])
        oil_val = data.get('oil_price', 0)
        ax2.bar(['Brent Crude'], [oil_val], color='#2d3436')
        ax2.axhline(y=75, color='#00b894', linestyle='--', label='Pre-Crisis Baseline ($75)')
        ax2.set_ylim(0, 200)
        ax2.set_title(f"Energy Market: ${oil_val}/bbl", fontsize=14, fontweight='bold')
        ax2.legend()

        # --- PANEL 3: MARITIME FRICTION (Middle Left) ---
        ax3 = fig.add_subplot(gs[1, 0])
        friction = data.get('port_friction', 1.0)
        ax3.bar(['Port Friction'], [friction], color='#e17055')
        ax3.axhline(y=1.0, color='#0984e3', linestyle='--', label='Normal Flow')
        ax3.set_ylim(0, 6)
        ax3.set_title(f"Logistics Friction: {friction}x", fontsize=14, fontweight='bold')
        ax3.legend()

        # --- PANEL 4: SOVEREIGN RISK DISTRIBUTION (Middle Right) ---
        ax4 = fig.add_subplot(gs[1, 1])
        risk_count = data.get('sovereign_risk_entities', 96)
        
        # Fixed and closed the pie chart function
        ax4.pie([risk_count, 195-risk_count], 
                labels=['At Risk', 'Stable'], 
                colors=['#ff7675', '#b2bec3'], 
                autopct='%1.1f%%', 
                startangle=140, 
                explode=(0.05, 0)) 
        
        ax4.set_title(f"Sovereign Debt Risk ({risk_count} Entities)", fontsize=14, fontweight='bold')

        # --- PANEL 5: STABILITY TRENDLINE (Bottom Span) ---
        ax5 = fig.add_subplot(gs[2, :])
        history_file = os.path.join(self.output_path, "stability_history.csv")
        
        if os.path.exists(history_file):
            try:
                df = pd.read_csv(history_file)
                df = df.tail(15) # Show last 15 simulations
                ax5.plot(df['Timestamp'], df['Score'], marker='o', color='#6c5ce7', linewidth=3, markersize=8)
                ax5.fill_between(df['Timestamp'], df['Score'], color='#a29bfe', alpha=0.2)
                ax5.set_ylim(0, 110)
                ax5.set_title("Historical Stability Trend", fontsize=14, fontweight='bold')
                ax5.tick_params(axis='x', rotation=30)
                ax5.grid(True, linestyle=':', alpha=0.5)
            except Exception as e:
                ax5.text(0.5, 0.5, f"Error Loading Trend: {e}", ha='center')
        else:
            ax5.text(0.5, 0.5, "Waiting for initial simulation data...", ha='center')

        # --- PANEL 6: INTELLIGENCE FEED (Footer) ---
        ax6 = fig.add_subplot(gs[3, :])
        ax6.axis('off')
        
        news_file = "news_feed.txt"
        if os.path.exists(news_file):
            with open(news_file, "r") as f:
                headlines = f.readlines()[-5:] # Display the 5 most recent events
            feed_text = "".join(headlines)
        else:
            feed_text = "[WAITING] System is scanning for live intelligence updates..."
            
        ax6.text(0.01, 0.8, f"LIVE INTELLIGENCE FEED (MARCH 22, 2026):", 
                 fontsize=12, fontweight='bold', transform=ax6.transAxes)
        ax6.text(0.01, 0.1, feed_text, 
                 transform=ax6.transAxes, fontsize=10.5, family='monospace',
                 linespacing=1.8, verticalalignment='bottom', 
                 bbox=dict(boxstyle='round,pad=1', facecolor='#fdfdfd', edgecolor='#dfe6e9', alpha=0.8))

        # Final Formatting and Export
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        output_file = os.path.join(self.output_path, "stability_report_march_22.png")
        plt.savefig(output_file, dpi=120)
        plt.close()
        print(f"-> Multi-Panel Intelligence Dashboard Exported: {output_file}")
