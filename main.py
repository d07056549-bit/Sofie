import os
os.environ["PYTENSOR_FLAGS"] = "cxx="

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime

# Layer 3: Bayesian Logic
try:
    import pymc as pm
except ImportError:
    pm = None 

from src.utils.data_processor import SofieDataEngine

EXPORT_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def get_headlines(score):
    """Generates reactive world events based on the Stability Index."""
    low_risk = [
        "Global trade routes report normal throughput.",
        "Central Banks signal 'cautious optimism' on volatility.",
        "Maritime logistics stabilizing in key corridors."
    ]
    med_risk = [
        "Supply chain friction increasing in Northern sectors.",
        "Digital infrastructure reports minor packet loss globally.",
        "Commodity futures show 4% volatility spike."
    ]
    high_risk = [
        "CRITICAL: Hague issues emergency 'Systemic Alert'.",
        "Market Panic: Global indices drop 8% in pre-market.",
        "Black Swan Event: Port of Rotterdam at 10% capacity.",
        "Cyber Breach: Financial clearing houses report intrusion."
    ]
    
    # Filter based on current score
    if score > 85:
        pool = high_risk
    elif score > 50:
        pool = med_risk
    else:
        pool = low_risk
        
    return random.sample(pool, 2) # Pick 2 random headlines from the pool

def update_history(scenario, score):
    history_path = os.path.join(EXPORT_DIR, "stability_history.csv")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = pd.DataFrame([[timestamp, scenario, score]], columns=["Timestamp", "Scenario", "Score"])
    if os.path.exists(history_path):
        new_entry.to_csv(history_path, mode='a', header=False, index=False)
    else:
        new_entry.to_csv(history_path, index=False)

def calculate_nexus_score(live_stats, hours_to_deadline=34):
    fatalities_comp = live_stats.get('fatalities', 0) / 20
    friction_comp = live_stats.get('friction', 1.0) * 10
    volatility_comp = live_stats.get('volatility', 1.0) * 15
    time_stress = 50 / (hours_to_deadline + 1)
    is_swan = live_stats.get('black_swan_active', False)
    swan_sev = live_stats.get('swan_severity', 0.0)
    multiplier = 1.0 + (swan_sev * 0.07) if is_swan else 1.0
    base_score = (fatalities_comp + friction_comp + volatility_comp + time_stress) * multiplier
    shock = abs(np.random.standard_cauchy()) * (swan_sev if is_swan else 0.5)
    return round(np.clip(base_score + shock, 0, 150), 2)

def generate_dashboard(score, prob, status, headlines):
    """Enhanced Dashboard with Dynamic News Feed."""
    plt.style.use('dark_background')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), 
                                       gridspec_kw={'height_ratios': [2, 4, 3]})
    
    # PANEL 1: GAUGE
    color = 'red' if score > 70 else 'orange' if score > 40 else 'green'
    ax1.barh(['INDEX'], [score], color=color, alpha=0.7)
    ax1.set_xlim(0, 150)
    ax1.set_title(f"SOFIE SITREP | {datetime.now().strftime('%H:%M:%S')} GMT", color='cyan', loc='left')
    ax1.text(5, 0, f"BREACH PROBABILITY: {prob}%", color='white', fontweight='bold', va='center')
    ax1.axis('off')

    # PANEL 2: TREND
    try:
        history_path = os.path.join(EXPORT_DIR, "stability_history.csv")
        df_hist = pd.read_csv(history_path)
        data_to_plot = df_hist.iloc[:, 2].tail(15) 
        ax2.plot(range(len(data_to_plot)), data_to_plot, color='cyan', marker='o', linewidth=2)
        ax2.fill_between(range(len(data_to_plot)), data_to_plot, color='cyan', alpha=0.1)
        ax2.set_ylabel("Stability Index")
    except:
        ax2.text(0.5, 0.5, "COLLECTING TREND DATA...", ha='center', color='gray')
    ax2.grid(color='white', alpha=0.1)

    # PANEL 3: LIVE NEWS FEED
    ax3.set_facecolor('#0a0a0a')
    ax3.set_xticks([]); ax3.set_yticks([])
    news_ticker = "\n".join([f">>> {h}" for h in headlines])
    ticker_content = (
        f"STATUS: {status}\n"
        f"---------------------------------------------------\n"
        f"{news_ticker}\n"
        f"---------------------------------------------------\n"
        f">>> ANALYSIS: STOCHASTIC SHOCK DETECTED"
    )
    ax3.text(0.02, 0.5, ticker_content, color='lime', fontfamily='monospace', fontsize=10, va='center')
    ax3.set_title("LIVE INTELLIGENCE FEED", loc='left', fontsize=8, color='lime')

    plt.tight_layout()
    plt.savefig(os.path.join(EXPORT_DIR, "stability_report_march_22.png"))
    plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=str, default="baseline")
    parser.add_argument("--hours", type=int, default=34)
    args = parser.parse_args()
    engine = SofieDataEngine()
    
    try:
        live_stats = engine.run_all()
        score = calculate_nexus_score(live_stats, hours_to_deadline=args.hours)
        
        # Bayesian Logic
        if not pm or score < 40: prob = 5.2
        else:
            with pm.Model() as model:
                risk_p = pm.Beta('risk_p', alpha=2, beta=5)
                obs = pm.Binomial('obs', n=150, p=risk_p, observed=score)
                map_estimate = pm.find_MAP(progressbar=False)
                prob = round(float(map_estimate['risk_p']) * 100, 1)

        status = "CRITICAL" if score > 90 else "UNSTABLE" if score > 70 else "STABLE"
        
        # News and History
        headlines = get_headlines(score)
        update_history(args.scenario, score)
        generate_dashboard(score, prob, status, headlines)

        print(f"=======================================================")
        print(f"STABILITY INDEX: {score} | STATUS: {status}")
        print(f"BREACH PROBABILITY: {prob}%")
        for h in headlines: print(f"NEWS: {h}")
        print(f"=======================================================")

    except Exception as e:
        print(f"SYSTEM ERROR: {e}")

if __name__ == "__main__":
    main()
