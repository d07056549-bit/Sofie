import os
os.environ["PYTENSOR_FLAGS"] = "cxx="
import argparse
import pandas as pd
import numpy as np
from datetime import datetime

# Layer 3: Bayesian Logic (Probability)
try:
    import pymc as pm
except ImportError:
    pm = None 

# Layer 1: Sensing (Robust Data Engine)
from src.utils.data_processor import SofieDataEngine

def calculate_nexus_score(live_stats):
    """
    Layer 2: Math. 
    Calculates a stochastic stability score using Cauchy 'Fat-Tail' shocks.
    """
    # 1. Base Components
    fatalities_comp = live_stats.get('fatalities', 0) / 20
    friction_comp = live_stats.get('friction', 1.0) * 10
    volatility_comp = live_stats.get('volatility', 1.0) * 15
    
    # 2. Black Swan Logic & Multiplier
    is_swan = live_stats.get('black_swan_active', False)
    swan_sev = live_stats.get('swan_severity', 0.0)
    
    # The 1.6x dynamic multiplier (scaled by severity)
    multiplier = 1.0 + (swan_sev * 0.07) if is_swan else 1.0
    base_score = (fatalities_comp + friction_comp + volatility_comp) * multiplier
    
    # 3. Stochastic Cauchy Shock
    # Gamma (spread) increases with systemic stress
    gamma = swan_sev if is_swan else 0.5
    shock = abs(np.random.standard_cauchy()) * gamma
    
    return round(np.clip(base_score + shock, 0, 150), 2)

def run_bayesian_probability(current_score, swan_active):
    """
    Layer 3: Logic.
    Calculates the 'Probability of Systemic Breach' using Bayesian Inference.
    """
    if not pm or current_score < 40:
        return 5.2 # Baseline background risk
    
    try:
        with pm.Model() as model:
            # Prior: We expect risk to be low, but the score can shift our belief
            risk_p = pm.Beta('risk_p', alpha=2, beta=5)
            # Likelihood
            obs = pm.Binomial('obs', n=150, p=risk_p, observed=current_score)
            # Maximum A Posteriori (MAP) estimate
            map_estimate = pm.find_MAP(progressbar=False)
            return round(float(map_estimate['risk_p']) * 100, 1)
    except:
        return 5.2

def get_causal_impact(live_stats):
    """
    Layer 4: Connection.
    Traces the 'Path of Contagion' (Simulated Graph Logic).
    """
    if not live_stats.get('black_swan_active'):
        return "Stable - No active contagion chains detected."
    
    # Simulated Graph Relationships
    causal_chains = {
        "Cyber": "Digital Hubs -> Financial Markets -> Power Grid",
        "Maritime": "Strait of Malacca -> Global Supply Chain -> Consumer CPI",
    }
    
    chain = causal_chains.get("Cyber") if live_stats['swan_severity'] > 0 else "Local friction"
    return f"ANALYSIS: [Trigger] -> {chain}"

def update_history(scenario, score):
    """Logs the run to the central history CSV."""
    history_path = "stability_history.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = pd.DataFrame([[timestamp, scenario, score]], columns=["Timestamp", "Scenario", "Score"])
    
    if os.path.exists(history_path):
        new_entry.to_csv(history_path, mode='a', header=False, index=False)
    else:
        new_entry.to_csv(history_path, index=False)

def main():
    parser = argparse.ArgumentParser(description="SOFIE EVOLVED v2.0")
    parser.add_argument("--scenario", type=str, default="baseline")
    args = parser.parse_args()

    engine = SofieDataEngine()
    
    print("=======================================================")
    print("--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: {datetime.now().strftime('%B %d, %Y | TIME: %H:%M')} GMT")
    print("=======================================================")

    try:
        # Step 1: Data Sensing
        live_stats = engine.run_all()
        
        # Step 2: Stochastic Math
        stability_score = calculate_nexus_score(live_stats)
        
        # Step 3: Bayesian Logic
        prob_breach = run_bayesian_probability(stability_score, live_stats.get('black_swan_active', False))
        
        # Step 4: Causal Connectivity
        causal_analysis = get_causal_impact(live_stats)
        
        # Determine Status
        status = "CRITICAL" if stability_score > 90 else "UNSTABLE" if stability_score > 70 else "STABLE"
        
        # Persist results
        update_history(args.scenario, stability_score)

        # Output Display
        print("-------------------------------------------------------")
        print(f"STABILITY INDEX: {stability_score}")
        print(f"PROBABILITY OF SYSTEMIC BREACH: {prob_breach}%")
        print(f"STATUS: {status}")
        print(f"CAUSAL {causal_analysis}")
        
        if live_stats.get('black_swan_active'):
            print(f"!!! BLACK SWAN ALERT: Severity {live_stats['swan_severity']} Detected !!!")
            
        print("=======================================================")
        print(f"--- SITREP SUMMARY: {datetime.now().strftime('%B %d, %Y').upper()} ---")
        print("ULTIMATUM EXPIRES IN <34 HOURS.")

    except Exception as e:
        print(f"CRITICAL SYSTEM ERROR: {e}")

if __name__ == "__main__":
    main()
