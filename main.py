import pandas as pd # Ensure you have pandas
from datetime import datetime
import argparse
from src.data_pipeline.loaders import DataLoader
from src.core.risk_engine import SofieRiskEngine
from src.core.scenario_engine import ScenarioEngine # <-- NEW
from src.utils.visualizer import SofieVisualizer
from src.utils.briefing import SofieBriefing
from src.utils.alerts import SofieAlerts

def main():
    parser = argparse.ArgumentParser(description="Sofie Evolved v2.0")
    parser.add_argument("--scenario", type=str, help="Scenario: peace, ultimatum_expires, blackout")
    args = parser.parse_args()

    print("--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")

    def record_history(score, scenario):
    history_file = "exports/stability_history.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    new_data = pd.DataFrame([[timestamp, scenario, score]], 
                            columns=['Timestamp', 'Scenario', 'Score'])
    
    if not os.path.exists(history_file):
        new_data.to_csv(history_file, index=False)
    else:
        new_data.to_csv(history_file, mode='a', header=False, index=False)
    print(f"-> History Updated: {timestamp} | Score: {score}")
    
    # 1. Load Baseline
    data = DataLoader(feed_date="2026-03-22").get_latest_nexus()
    
    # 2. Apply Scenario if requested
    if args.scenario:
        data = ScenarioEngine().apply(data, args.scenario)
    
    # 3. Calculate
    engine = SofieRiskEngine(data)
    stability_score = engine.calculate_global_fragility()
    print(f"Global Stability Index: {stability_score}")

# 4. Export & Record
    viz = SofieVisualizer()
    viz.generate_risk_chart(stability_score, data)
    
    # Record this specific run to history
    record_history(stability_score, args.scenario if args.scenario else "Baseline")
    
    # Generate the text report
    brief = SofieBriefing()
    brief.generate_brief(stability_score, data)
    
    # Print the country alerts to the console
    alerts = SofieAlerts()
    alerts.get_top_threats()

if __name__ == "__main__":
    main()
