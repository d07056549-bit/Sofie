import os
import argparse
from datetime import datetime

# Import custom intelligence modules
from src.utils.visualizer import SofieVisualizer
from src.utils.mapper import SofieMapper
from src.utils.logistics_mapper import LogisticsMapper
from src.utils.data_processor import SofieDataEngine

def record_history(score, scenario_name, output_path=r"C:\Users\Empok\Documents\GitHub\Sofie\Data\exports"):
    """Logs simulation results for the historical trend panel."""
    import os
    from datetime import datetime
    
    # 1. Ensure the folder exists
    os.makedirs(output_path, exist_ok=True)
    
    # 2. Set the correct file path
    history_file = os.path.join(output_path, "stability_history.csv")
    file_exists = os.path.isfile(history_file)
    
    # 3. Open the file in 'append' mode ('a')
    with open(history_file, "a") as f:
        # If it's a brand new file, add the headers first
        if not file_exists:
            f.write("Timestamp,Scenario,Score\n")
        
        # Write the actual data row
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"{timestamp},{scenario_name},{score}\n")
    
    print(f"📊 HISTORICAL LOG UPDATED: {history_file}")

def main():
    # 1. Setup CLI (Defining 'args' first to prevent NameError)
    parser = argparse.ArgumentParser(description="SOFIE Evolved v2.0 | March 23 Nexus")
    parser.add_argument('--scenario', type=str, default='baseline', 
                        choices=['baseline', 'peace', 'blackout', 'ultimatum_expires'])
    args = parser.parse_args()

    # DYNAMIC TIME FOR MARCH 23
    now = datetime.now()
    live_date = now.strftime("%B %d, %Y")
    live_time = now.strftime("%H:%M")

    print("="*55)
    print(f"--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: {live_date} | TIME: {live_time} GMT")
    print("="*55 + "\n")

    # 2. Data Ingestion (CSVs + News)
    data_engine = SofieDataEngine(root_dir="Data/raw")
    live_stats = data_engine.run_all()
    
    # 3. Crisis Intelligence Multiplier
    news_multiplier = 1.0
    if os.path.exists("news_feed.txt"):
        with open("news_feed.txt", "r") as f:
            news = f.read().lower()
            if any(word in news for word in ["blockade", "strike", "ultimatum"]):
                news_multiplier = 1.4

    # FIX: Using live_stats to create a baseline
    base_stability = round(live_stats.get('friction', 1.0) * 35.0, 2)
    
    # Check the CLI --scenario flag
    if args.scenario in ["blackout", "ultimatum_expires"]:
        stability_score = round(base_stability * 1.5 * news_multiplier, 2)
        status_msg = f"CRITICAL: {args.scenario.upper()} in effect." # Added this
        print(f"🚨 SCENARIO: {args.scenario.upper()} MODE ACTIVATED - Risk adjusted.")
    else:
        stability_score = round(base_stability * news_multiplier, 2)
        status_msg = "STABLE. Monitoring regional friction nodes."

    # Make sure we don't exceed 100%
    stability_score = min(stability_score, 100.0)

    # 4. Scenario Definitions
    scenarios = {
        'baseline': {
            'oil_price': 112.19, # Current Brent Spot
            'port_friction': live_stats['friction'] * news_multiplier,
            'sovereign_risk_entities': int(96 * live_stats['friction'])
        },
        'peace': {'oil_price': 72.50, 'port_friction': 1.0, 'sovereign_risk_entities': 45},
        'blackout': {'oil_price': 185.00, 'port_friction': 5.0, 'sovereign_risk_entities': 142},
        'ultimatum_expires': {'oil_price': 145.20, 'port_friction': 3.5, 'sovereign_risk_entities': 110}
    }

    # 5. Apply the selected Scenario
    current_scenario = scenarios.get(args.scenario, scenarios['baseline'])
    
    # Now update your stability score using the scenario values
    stability_score = min(current_scenario['port_friction'] * 10, 100.0) 
    # -----------------------------------------

    # 6. Get the News Feed (for the sidebar)
    live_alerts = data_engine.get_live_port_alerts()
    
    # 7. Stability Index Calculation
    curr = scenarios[args.scenario]
    oil_comp = (min(curr['oil_price'], 200) / 200) * 45
    fric_comp = (min(curr['port_friction'], 5) / 5) * 30
    risk_comp = (min(curr['sovereign_risk_entities'], 195) / 195) * 25
    stability_score = round(oil_comp + fric_comp + risk_comp, 2)

    print(f">>> GLOBAL STABILITY INDEX: {stability_score} <<<\n")

    # 8. Map Generation Setup
    file_suffix = now.strftime("%H%M") 
    at_risk_list = data_engine.get_at_risk_countries()
    friction_data = data_engine.get_port_friction_map()

    # Note: We skip individual maps because Unified Dashboard (Section 7) handles them better.
    # SofieMapper().generate_risk_map(at_risk_list, suffix=file_suffix)
    # LogisticsMapper().generate_heatmap(friction_data, suffix=file_suffix)

   # 9. Unified Dashboard Generation
    # 1. Fetch the Live Feed using the existing engine
    live_alerts = data_engine.get_live_port_alerts() 
    
    # 2. Initialize the Visualizer
    visualizer = SofieVisualizer()

    # 3. Generate the actual file
    visualizer.generate_unified_intel(
        score=stability_score, 
        at_risk=at_risk_list, 
        friction=friction_data, # This is your Port CSV data
        alerts=live_alerts,     # This is your Online News feed
        suffix=file_suffix
    )
    
    record_history(stability_score, args.scenario)

    # 8. SitRep Summary
    print("="*55)
    # CHANGE 'current_date' TO 'live_date' HERE:
    print(f"--- SITREP SUMMARY: {live_date.upper()} ---") 
    
    if stability_score > 75:
        print("STATUS: CRITICAL WATCH. Ultimatum window CLOSING.")
    else:
        print("STATUS: STABLE. Monitoring regional friction nodes.")
    print("="*55)
    print("--- RUN COMPLETE ---\n")

if __name__ == "__main__":
    main()
