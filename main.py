import os
import sys
import argparse
from datetime import datetime

# Import our custom modules
from src.utils.visualizer import SofieVisualizer
from src.utils.mapper import SofieMapper
from src.utils.data_processor import SofieDataEngine

def record_history(score, scenario_name, output_path="exports/"):
    """Logs the simulation result to a CSV for the trendline component."""
    history_file = os.path.join(output_path, "stability_history.csv")
    file_exists = os.path.isfile(history_file)
    
    with open(history_file, "a") as f:
        if not file_exists:
            f.write("Timestamp,Scenario,Score\n")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"{timestamp},{scenario_name},{score}\n")

def main():
    # 1. Setup CLI Arguments
    parser = argparse.ArgumentParser(description="SOFIE Evolved v2.0 - Global Fragility Monitor")
    parser.add_argument('--scenario', type=str, default='baseline', 
                        choices=['baseline', 'peace', 'blackout', 'ultimatum_expires'],
                        help='Choose the simulation scenario')
    args = parser.parse_args()

    print("="*50)
    print(f"--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: March 22, 2026")
    print("="*50 + "\n")

    # 2. Initialize Data Engines
    # This reads your C:/Data/raw/ folder automatically
    data_engine = SofieDataEngine(root_dir="Data/raw")
    live_csv_stats = data_engine.run_all() 
    
    # 3. Define Simulation Scenarios
    # We combine manual inputs with data-driven multipliers from your CSVs
    scenarios = {
        'baseline': {
            'oil_price': 112.19, 
            'port_friction': live_csv_stats['friction'], # From Maritime CSV
            'sovereign_risk_entities': 96 + (live_csv_stats['fatalities'] // 500) # Risk scaled by ACLED deaths
        },
        'peace': {
            'oil_price': 72.50,
            'port_friction': 1.0,
            'sovereign_risk_entities': 45
        },
        'blackout': {
            'oil_price': 185.00,
            'port_friction': 5.0,
            'sovereign_risk_entities': 142
        },
        'ultimatum_expires': {
            'oil_price': 145.20,
            'port_friction': 3.5,
            'sovereign_risk_entities': 110
        }
    }

    # 4. Calculate Global Stability Index (The SOFIE Formula)
    current = scenarios[args.scenario]
    
    # Simple weighted fragility score (0-100)
    # Oil contributes 40%, Friction 30%, Debt Risk 30%
    oil_component = (min(current['oil_price'], 200) / 200) * 40
    fric_component = (min(current['port_friction'], 5) / 5) * 30
    risk_component = (min(current['sovereign_risk_entities'], 195) / 195) * 30
    
    stability_score = round(oil_component + fric_component + risk_component, 2)

    print(f">>> GLOBAL STABILITY INDEX: {stability_score} <<<\n")

    # 5. Generate Geographic Intelligence Map
    # Pulls country names directly from your ACLED/UCDP fatalitiy data
    at_risk_list = data_engine.get_at_risk_countries()
    mapper = SofieMapper(output_path="exports/")
    mapper.generate_risk_map(at_risk_list)

    # 6. Generate Multi-Panel Dashboard
    viz = SofieVisualizer(output_path="exports/")
    viz.generate_risk_chart(stability_score, current)

    # 7. Record to History for Trend Analysis
    record_history(stability_score, args.scenario)

    # 8. Intelligence Sign-off
    print("="*50)
    print("--- SITREP SUMMARY: MARCH 22, 2026 ---")
    if stability_score > 80:
        print("STATUS: SYSTEMIC COLLAPSE IMMINENT.")
        print("ACTION: Trigger 'Zeta' protocols. Advise immediate asset liquidation.")
    elif stability_score > 65:
        print("STATUS: CRITICAL TENSION.")
        print(f"ACTION: Monitor Hormuz Blockade. Watch for yields in {at_risk_list[:3]}.")
    else:
        print("STATUS: NOMINAL.")
    print("="*50)
    print("--- RUN COMPLETE | ALL EXPORTS SAVED TO /exports ---\n")

if __name__ == "__main__":
    main()
