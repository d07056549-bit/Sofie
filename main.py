import os
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
from src.utils.data_processor import SofieDataEngine

def calculate_nexus_score(live_stats):
    """
    Calculates a stochastic stability score.
    Higher values = Lower Stability (Risk).
    """
    # 1. Base Score (The deterministic part)
    # Scaled against fatalities, port friction, and market volatility
    base = (live_stats['fatalities'] / 20) + (live_stats['friction'] * 10) + (live_stats['volatility'] * 15)
    
    # 2. Stochastic Scaling (The 'Cauchy' Factor)
    # If a Black Swan is active, gamma (spread) increases to reflect systemic shock
    is_swan = live_stats.get('black_swan_active', False)
    swan_sev = live_stats.get('swan_severity', 0.1)
    
    gamma = swan_sev if is_swan else 0.5
    
    # Generate a Cauchy Shock (Heavy-Tailed)
    # Unlike a Normal distribution, Cauchy allows for 'extreme' outliers (Black Swans)
    shock = abs(np.random.standard_cauchy()) * gamma
    
    final_score = base + shock
    
    # Clip between 0-150 for the index display
    return round(np.clip(final_score, 0, 150), 2)

def update_history(scenario, score):
    """Logs the new score to stability_history.csv"""
    history_path = "stability_history.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    new_data = pd.DataFrame([[timestamp, scenario, score]], columns=["Timestamp", "Scenario", "Score"])
    
    if os.path.exists(history_path):
        new_data.to_csv(history_path, mode='a', header=False, index=False)
    else:
        new_data.to_csv(history_path, index=False)

def main():
    parser = argparse.ArgumentParser(description="SOFIE EVOLVED v2.0 - Stability Monitor")
    parser.add_argument("--scenario", type=str, default="baseline", help="Scenario to run")
    args = parser.parse_args()

    # Initialize Data Engine
    engine = SofieDataEngine()
    
    print("=======================================================")
    print("--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: {datetime.now().strftime('%B %d, %Y | TIME: %H:%M')} GMT")
    print("=======================================================")

    try:
        # 1. Fetch live metrics (Cyber, Maritime, Market)
        live_stats = engine.run_all()
        
        # 2. Calculate the Stochastic Stability Index
        stability_score = calculate_nexus_score(live_stats)
        
        # 3. Determine Status
        status = "CRITICAL" if stability_score > 90 else "UNSTABLE" if stability_score > 70 else "STABLE"
        
        # 4. Log to CSV
        update_history(args.scenario, stability_score)

        print("-------------------------------------------------------")
        print(f"STABILITY INDEX: {stability_score}")
        print(f"STATUS: {status}")
        if live_stats['black_swan_active']:
            print(f"!!! BLACK SWAN DETECTED: Severity {live_stats['swan_severity']} !!!")
        print("=======================================================")
        print(f"--- SITREP SUMMARY: {datetime.now().strftime('%B %d, %Y').upper()} ---")
        print("ULTIMATUM EXPIRES IN <34 HOURS.")

    except Exception as e:
        print(f"CRITICAL SYSTEM ERROR: {e}")

if __name__ == "__main__":
    main()
