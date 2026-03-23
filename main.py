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
    # (Removed news_feed.txt dependency)
    news_multiplier = 1.0 
    
    # We still calculate the base stability from the CSV data
    base_stability = round(live_stats.get('friction', 1.0) * 35.0, 2)
    
    # Apply scenario logic
    if args.scenario in ["blackout", "ultimatum_expires"]:
        stability_score = round(base_stability * 1.5, 2)
        status_msg = f"CRITICAL: {args.scenario.upper()} in effect."
        print(f"🚨 SCENARIO: {args.scenario.upper()} MODE ACTIVATED.")
    else:
        stability_score = base_stability
        status_msg = "STABLE. Monitoring regional friction nodes."

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
    
    # 7. MULTI-DOMAIN STABILITY PREDICTION
    try:
        # Load ACLED
        acled_data = pd.read_csv("Data/processed/acled_risk_indices.csv")
        acled_score = acled_data[acled_data['YEAR'] == 2026]['conflict_index'].mean()

        # Load UCDP
        ucdp_data = pd.read_csv("Data/processed/ucdp_risk_indices.csv")
        ucdp_score = ucdp_data[ucdp_data['year'] == 2026]['ucdp_risk_index'].mean()

        # Consensus Conflict Score (Average of both)
        global_conflict_avg = (acled_score + ucdp_score) / 2
        
        print(f"🌍 GEOPOLITICAL Intel: Consensus Risk (ACLED+UCDP) at {global_conflict_avg:.2f}%")
    except Exception as e:
        print(f"⚠️ Geopolitical Load Warning: {e}")
        global_conflict_avg = 0.5 # Fallback

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

    print(f"DEBUG: Found {len(live_alerts)} live alerts.")
    if len(live_alerts) > 0:
        print(f"DEBUG: First alert title: {live_alerts[0]['title']}")
    
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
