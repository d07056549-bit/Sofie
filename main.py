import os
# --- LINE 1 & 2: SILENCE WARNINGS & PATH SETUP ---
os.environ["PYTENSOR_FLAGS"] = "cxx="

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Layer 3: Bayesian Logic (Probability)
try:
    import pymc as pm
except ImportError:
    pm = None 

# Layer 1: Sensing (Robust Data Engine)
from src.utils.data_processor import SofieDataEngine

# Define the global export path
EXPORT_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def update_history(scenario, score):
    """Logs the unique run score specifically to the exports folder."""
    history_path = os.path.join(EXPORT_DIR, "stability_history.csv")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = pd.DataFrame([[timestamp, scenario, score]], columns=["Timestamp", "Scenario", "Score"])
    
    if os.path.exists(history_path):
        new_entry.to_csv(history_path, mode='a', header=False, index=False)
    else:
        new_entry.to_csv(history_path, index=False)

def calculate_nexus_score(live_stats, hours_to_deadline=34):
    """Layer 2: Math - Stochastic Stability with Temporal Stress."""
    fatalities_comp = live_stats.get('fatalities', 0) / 20
    friction_comp = live_stats.get('friction', 1.0) * 10
    volatility_comp = live_stats.get('volatility', 1.0) * 15
    
    # Temporal Stress factor
    time_stress = 50 / (hours_to_deadline + 1)
    
    is_swan = live_stats.get('black_swan_active', False)
    swan_sev = live_stats.get('swan_severity', 0.0)
    multiplier = 1.0 + (swan_sev * 0.07) if is_swan else 1.0
    
    base_score = (fatalities_comp + friction_comp + volatility_comp + time_stress) * multiplier
    shock = abs(np.random.standard_cauchy()) * (swan_sev if is_swan else 0.5)
    
    return round(np.clip(base_score + shock, 0, 150), 2)

def run_bayesian_probability(current_score, swan_active):
    """Layer 3: Bayesian Logic - Calculates Breach Probability."""
    if not pm or current_score < 40:
        return 5.2 
    try:
        with pm.Model() as model:
            risk_p = pm.Beta('risk_p', alpha=2, beta=5)
            obs = pm.Binomial('obs', n=150, p=risk_p, observed=current_score)
            map_estimate = pm.find_MAP(progressbar=False)
            return round(float(map_estimate['risk_p']) * 100, 1)
    except:
        return 5.2

def generate_dashboard(score, prob, status):
    """Creates the Visual Intelligence Report (PNG) in the exports folder."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    color = 'red' if score > 70 else 'orange' if score > 40 else 'green'
    ax.barh(['Stability Index'], [score], color=color, alpha=0.6)
    ax.set_xlim(0, 150)
    
    plt.title(f"SOFIE SITREP: {status} | {datetime.now().strftime('%H:%M')} GMT", fontsize=14, color='cyan')
    plt.xlabel("Index Value (0-150)")
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    
    plt.text(5, 0.2, f"Probability of Breach: {prob}%", fontsize=12, color='white', fontweight='bold')
    plt.text(5, -0.2, f"Systemic Status: {status}", fontsize=12, color=color, fontweight='bold')

    plt.tight_layout()
    # Save specifically to the exports directory
    report_path = os.path.join(EXPORT_DIR, "stability_report_march_22.png")
    plt.savefig(report_path)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="SOFIE EVOLVED v2.0")
    parser.add_argument("--scenario", type=str, default="baseline")
    parser.add_argument("--hours", type=int, default=34)
    args = parser.parse_args()

    engine = SofieDataEngine()
    
    print("=======================================================")
    print("--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: {datetime.now().strftime('%B %d, %Y | TIME: %H:%M')} GMT")
    print(f"TARGET DIRECTORY: {EXPORT_DIR}")
    print("=======================================================")

    try:
        live_stats = engine.run_all()
        stability_score = calculate_nexus_score(live_stats, hours_to_deadline=args.hours)
        prob_breach = run_bayesian_probability(stability_score, live_stats.get('black_swan_active', False))
        status = "CRITICAL" if stability_score > 90 else "UNSTABLE" if stability_score > 70 else "STABLE"
        
        # All exports handled by the functions using EXPORT_DIR
        update_history(args.scenario, stability_score)
        generate_dashboard(stability_score, prob_breach, status)

        print("-------------------------------------------------------")
        print(f"STABILITY INDEX: {stability_score}")
        print(f"PROBABILITY OF SYSTEMIC BREACH: {prob_breach}%")
        print(f"STATUS: {status}")
        print(f"✅ ALL EXPORTS SAVED TO: /exports/")
        
        if live_stats.get('black_swan_active'):
            print(f"!!! BLACK SWAN ALERT: Severity {round(live_stats['swan_severity'], 2)} Detected !!!")
        print("=======================================================")

    except Exception as e:
        print(f"CRITICAL SYSTEM ERROR: {e}")

if __name__ == "__main__":
    main()
