import os
import time
import numpy as np
import pandas as pd
from datetime import datetime
from src.utils.data_processor import SofieDataEngine

def apply_stochastic_shock(base_score, volatility_factor):
    """
    LAYER 1: Cauchy 'Fat-Tail' Math.
    Simulates unpredictable market jumps.
    """
    # standard_cauchy creates the 'Black Swan' outliers.
    # We scale it by the swan_severity to control impact.
    shock = np.random.standard_cauchy() * volatility_factor
    final_score = base_score + shock
    
    # Cap the index between 0 (Peace) and 150 (Total Collapse)
    return round(np.clip(final_score, 0, 150), 2)

def main():
    print("=" * 55)
    print("--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    now = datetime.now()
    print(f"DATE: {now.strftime('%B %d, %Y')} | TIME: {now.strftime('%H:%M')} GMT")
    print("=" * 55)

    # Initialize the Data Engine (with Circuit Breakers)
    engine = SofieDataEngine()
    
    # --- DATA ACQUISITION ---
    # run_all() returns a dictionary of all tactical sensors
    live_stats = engine.run_all()

    # --- BASELINE CALCULATION ---
    # Components of the Stability Index
    conflict_friction = live_stats.get('fatalities', 0) * 0.05
    maritime_friction = (live_stats.get('friction', 1.0) - 1.0) * 10
    market_volatility = live_stats.get('volatility', 20.0) / 4
    
    raw_base_score = 40.0 + conflict_friction + maritime_friction + market_volatility

    # --- TIME-BASED LOGIC (March 22nd Escalation) ---
    # If past 22:00 GMT, add the 'Monday Morning' Market Opening panic
    if now.hour >= 22:
        raw_base_score += 5.0

    # --- BLACK SWAN MULTIPLIER ---
    black_swan_multiplier = 1.0
    # Use .get() to avoid KeyErrors if the sensor is offline
    if live_stats.get('black_swan_active', False):
        severity = live_stats.get('swan_severity', 0)
        # 1.6x multiplier for critical cyber/mobility events
        black_swan_multiplier = 1.0 + (severity * 0.1)
        print(f"!!! BLACK SWAN DETECTED: Digital/Physical Multiplier {black_swan_multiplier:.1f}x Applied !!!")

    # --- FINAL STOCHASTIC ENGINE ---
    # Apply the Cauchy Shock based on current system volatility
    final_raw = raw_base_score * black_swan_multiplier
    stability_index = apply_stochastic_shock(final_raw, live_stats.get('swan_severity', 1.0))

    # --- SITREP OUTPUT ---
    print("-" * 55)
    print(f"STABILITY INDEX: {stability_index}")
    print(f"STATUS: {'CRITICAL' if stability_index > 80 else 'UNSTABLE' if stability_index > 60 else 'STABLE'}")
    
    if stability_index > 80:
        print("-> ALERT: Systemic risk exceeds 80th percentile. Deploying countermeasures.")
    
    # --- EXPORT TO HISTORY ---
    history_file = "stability_history.csv"
    new_entry = pd.DataFrame([{
        "Timestamp": now.strftime("%Y-%m-%d %H:%M"),
        "Scenario": "baseline",
        "Score": stability_index
    }])
    
    new_entry.to_csv(history_file, mode='a', header=not os.path.exists(history_file), index=False)
    
    print("=" * 55)
    print("--- SITREP SUMMARY: MARCH 22, 2026 ---")
    print(f"ULTIMATUM EXPIRES IN <{36 if now.hour < 22 else 34} HOURS.")

if __name__ == "__main__":
    main()
