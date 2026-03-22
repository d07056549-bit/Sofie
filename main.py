import os
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
try:
    import pymc as pm
except ImportError:
    pm = None  # Fallback if PyMC is not yet installed

from src.utils.data_processor import SofieDataEngine

def calculate_nexus_score(live_stats):
    """
    Calculates a stochastic stability score (Layer 2: Math).
    Integrates base metrics with a Cauchy 'Fat-Tail' shock.
    """
    # 1. Base Components (The 'Sensing' values)
    fatalities_comp = live_stats.get('fatalities', 0) / 20
    friction_comp = live_stats.get('friction', 1.0) * 10
    volatility_comp = live_stats.get('volatility', 1.0) * 15
    
    # 2. Black Swan Logic
    is_swan = live_stats.get('black_swan_active', False)
    swan_sev = live_stats.get('swan_severity', 0.0)
    
    # Apply a systemic multiplier if the Black Swan is active
    multiplier = 1.0
    if is_swan:
        # Scale: Severity 9.0 adds roughly 60% to the base risk
        multiplier = 1.0 + (swan_sev * 0.07)
    
    base_score = (fatalities_comp + friction_comp + volatility_comp) * multiplier
    
    # 3. THE CAUCHY SHOCK (Fat-Tail math)
    # Gamma (spread) increases with systemic stress
    gamma = swan_sev if is_swan else 0.5
    # standard_cauchy generates the 'Black Swan' jump
    shock = abs(np.random.standard_cauchy()) * gamma
    
    final_score = base_score + shock
    
    # Clip between 0-150 (The Index allows 'overflow' past 100 in total collapse)
    return round(np.clip(final_score, 0, 150), 2)

def run_bayesian_probability(current_score, swan_active):
    """
    Layer 3: Bayesian Logic.
    Calculates the 'Probability of Systemic Breach' using PyMC.
    """
    if not pm:
        return "N/A" # Skip if library missing
    
    # Background risk level if things are quiet
    if not swan_active and current_score < 45:
        return 5.2 
    
    try:
        with pm.Model() as model:
            # Prior: Probability of risk (Beta distribution)
            risk_p = pm.Beta('risk_p', alpha=2, beta=5)
            # Likelihood: The score as an observation of instability
            obs = pm.Binomial('obs', n=150, p=risk_p, observed=current_score)
            # Maximum A Posteriori (MAP) estimate for real-time speed
            map_estimate = pm.find_MAP(progressbar=False)
            return round(float(map_estimate['risk_p']) * 100, 1)
    except:
        return 0.0

def update_history(scenario, score):
    """Logs the unique run score to the permanent history CSV."""
    history_path = "stability_history.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    new_entry = pd.DataFrame([[timestamp, scenario, score]], columns=["Timestamp", "Scenario", "Score"])
    
    if os.path.exists(history_path):
        new_entry.to_csv(history_path, mode='a', header=False, index=False)
    else:
        new_entry.to_csv(history_path, index=False)

def main():
    parser = argparse.ArgumentParser(description="SOFIE EVOLVED v2.0 - Systemic Monitor")
    parser.add_argument("--scenario", type=str, default="baseline", help="Scenario to run")
    args = parser.parse_args()

    # Initialize Robust Data Engine (Layer 1)
    engine = SofieDataEngine()
    
    print("=======================================================")
    print("--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: {datetime.now().strftime('%B %d, %Y | TIME: %H:%M')} GMT")
    print("=======================================================")

    try:
        # 1. Data Collection
        live_stats = engine.run_all()
        
        # 2. Score Generation
        stability_score = calculate_nexus_score(live_stats)
        
        # 3. Bayesian Inference
        prob_breach = run_bayesian_probability(stability_score, live_stats.get('black_swan_active', False))
        
        # 4. Status Determination
        status = "CRITICAL" if stability_score > 90 else "UNSTABLE" if stability_score > 70 else "STABLE"
        
        # 5. Output and Persistence
        update_history(args.scenario, stability_score)

        print("-------------------------------------------------------")
        print(f"STABILITY INDEX: {stability_score}")
        print(f"PROBABILITY OF SYSTEMIC BREACH: {prob_breach}%")
        print(f"STATUS: {status}")
        
        if live_stats.get('black_swan_active'):
            print(f"!!! ALERT: Black Swan Detected (Severity {live_stats['swan_severity']}) !!!")
            print(">>> Systemic multiplier and Cauchy shock applied.")
            
        print("=======================================================")
        print(f"--- SITREP SUMMARY: {datetime.now().strftime('%B %d, %Y').upper()} ---")
        print("ULTIMATUM EXPIRES IN <34 HOURS.")

    except Exception as e:
        print(f"CRITICAL SYSTEM ERROR: {e}")

if __name__ == "__main__":
    main()
