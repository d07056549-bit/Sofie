import argparse
import os
import pandas as pd
from datetime import datetime

# Internal Sofie Modules
from src.data_pipeline.loaders import DataLoader
from src.core.risk_engine import SofieRiskEngine
from src.core.scenario_engine import ScenarioEngine
from src.utils.visualizer import SofieVisualizer
from src.utils.briefing import SofieBriefing
from src.utils.alerts import SofieAlerts

def record_history(score, scenario):
    """Saves the results of every run to a CSV for trend tracking."""
    history_file = "exports/stability_history.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Create the directory if it's missing
    if not os.path.exists("exports"):
        os.makedirs("exports")
        
    new_entry = pd.DataFrame([[timestamp, scenario, score]], 
                            columns=['Timestamp', 'Scenario', 'Score'])
    
    if not os.path.exists(history_file):
        new_entry.to_csv(history_file, index=False)
    else:
        new_entry.to_csv(history_file, mode='a', header=False, index=False)
    print(f"-> History Logged: {timestamp} | {scenario} | Score: {score}")

def main():
    # 1. Handle Command Line Scenarios
    parser = argparse.ArgumentParser(description="Sofie Evolved v2.0 | Intelligence OS")
    parser.add_argument("--scenario", type=str, help="Options: peace, ultimatum_expires, blackout")
    args = parser.parse_args()

    print("\n" + "="*50)
    print("--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: {datetime.now().strftime('%B %d, %Y')}")
    print("="*50 + "\n")
    
    # 2. Load Real-World Baseline Data (March 22, 2026)
    # Note: Ensure your DataLoader points to your actual data files
    data = DataLoader(feed_date="2026-03-22").get_latest_nexus()
    
    # 3. Apply Scenario Overrides (If any)
    current_scenario = "Baseline"
    if args.scenario:
        current_scenario = args.scenario
        data = ScenarioEngine().apply(data, args.scenario)
    
    # 4. Run Global Risk Calculations
    engine = SofieRiskEngine(data)
    stability_score = engine.calculate_global_fragility()
    print(f"\n>>> GLOBAL STABILITY INDEX: {stability_score} <<<\n")

    # 5. Generate Multi-Panel Visual Dashboard
    viz = SofieVisualizer()
    viz.generate_risk_chart(stability_score, data)
    
    # 6. Generate Text SITREP (Situation Report)
    brief = SofieBriefing()
    brief.generate_brief(stability_score, data)
    
    # 7. Identify Top 5 Sovereign Default Risks
    alerts = SofieAlerts()
    alerts.get_top_threats()

    # 8. Record to History for Trend Analysis
    record_history(stability_score, current_scenario)

    print("\n" + "="*50)
    print("--- RUN COMPLETE | ALL EXPORTS SAVED TO /exports ---")
    print("="*50)

if __name__ == "__main__":
    main()
