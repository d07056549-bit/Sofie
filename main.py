import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Layer 1: Sensing (Standard Data Engine)
from src.utils.data_processor import SofieDataEngine

# Global Export Path
EXPORT_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def calculate_stability(live_stats):
    """
    RESTORED: Linear Stability Calculation.
    No Cauchy shocks. No extreme multipliers.
    """
    # Base indicators from sensors
    fatalities = live_stats.get('fatalities', 0) / 20
    friction = live_stats.get('friction', 1.0) * 10
    volatility = live_stats.get('volatility', 1.0) * 15
    
    # Simple summation with a small random noise factor (normal distribution)
    noise = np.random.normal(0, 2)
    base_score = fatalities + friction + volatility + noise
    
    return round(np.clip(base_score, 0, 100), 2)

def generate_report(score):
    """Restores the original clean dashboard look."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Color logic: Green to Red
    color = 'red' if score > 75 else 'orange' if score > 45 else 'green'
    
    ax.barh(['Stability Index'], [score], color=color, alpha=0.8)
    ax.set_xlim(0, 100)
    ax.set_title(f"SOFIE SYSTEM MONITOR | {datetime.now().strftime('%H:%M')} GMT", color='cyan')
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    
    status = "CRITICAL" if score > 75 else "UNSTABLE" if score > 45 else "STABLE"
    plt.text(5, -0.1, f"STATUS: {status}", fontsize=12, color=color, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(EXPORT_DIR, "stability_report.png"))
    plt.close()

def update_history(scenario, score):
    """Logs data to exports/stability_history.csv"""
    history_path = os.path.join(EXPORT_DIR, "stability_history.csv")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = pd.DataFrame([[timestamp, scenario, score]], columns=["Timestamp", "Scenario", "Score"])
    
    if os.path.exists(history_path):
        new_entry.to_csv(history_path, mode='a', header=False, index=False)
    else:
        new_entry.to_csv(history_path, index=False)

def main():
    parser = argparse.ArgumentParser(description="SOFIE STABLE v1.0")
    parser.add_argument("--scenario", type=str, default="baseline")
    args = parser.parse_args()

    engine = SofieDataEngine()
    
    print("=======================================================")
    print("--- SOFIE STABLE | SYSTEM RESTORED ---")
    print("=======================================================")

    try:
        # 1. Pull Data
        live_stats = engine.run_all()
        
        # 2. Calculate Stable Score
        score = calculate_stability(live_stats)
        
        # 3. Determine Status
        status = "CRITICAL" if score > 75 else "UNSTABLE" if score > 45 else "STABLE"
        
        # 4. Save and Plot
        update_history(args.scenario, score)
        generate_report(score)

        print(f"STABILITY INDEX: {score}")
        print(f"STATUS: {status}")
        print(f"✅ REPORT GENERATED: exports/stability_report.png")
        print("=======================================================")

    except Exception as e:
        print(f"SYSTEM ERROR: {e}")

if __name__ == "__main__":
    main()
