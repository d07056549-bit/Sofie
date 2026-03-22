import os
import argparse
from datetime import datetime

# Import custom intelligence modules
from src.utils.visualizer import SofieVisualizer
from src.utils.mapper import SofieMapper
from src.utils.logistics_mapper import LogisticsMapper
from src.utils.data_processor import SofieDataEngine

def record_history(score, scenario_name, output_path="exports/"):
    """Logs simulation results for the historical trend panel."""
    history_file = os.path.join(output_path, "stability_history.csv")
    file_exists = os.path.isfile(history_file)
    with open(history_file, "a") as f:
        if not file_exists:
            f.write("Timestamp,Scenario,Score\n")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"{timestamp},{scenario_name},{score}\n")

def main():
    # 1. Setup CLI
    parser = argparse.ArgumentParser(description="SOFIE Evolved v2.0 | March 22, 2026 Nexus")
    parser.add_argument('--scenario', type=str, default='baseline', 
                        choices=['baseline', 'peace', 'blackout', 'ultimatum_expires'])
    args = parser.parse_args()

    print("="*55)
    print(f"--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: March 22, 2026 | TIME: {datetime.now().strftime('%H:%M')} GMT")
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

    # 4. Scenario Definitions
    scenarios = {
        'baseline': {
            'oil_price': 112.19, 
            'port_friction': live_stats['friction'] * news_multiplier,
            'sovereign_risk_entities': 96 + (live_stats['fatalities'] // 200)
        },
        'peace': {'oil_price': 72.50, 'port_friction': 1.0, 'sovereign_risk_entities': 45},
        'blackout': {'oil_price': 185.00, 'port_friction': 5.0, 'sovereign_risk_entities': 142},
        'ultimatum_expires': {'oil_price': 145.20, 'port_friction': 3.5, 'sovereign_risk_entities': 110}
    }

    # 5. Stability Index Calculation
    curr = scenarios[args.scenario]
    
    # Define variables clearly before the final calculation
    oil_comp = (min(curr['oil_price'], 200) / 200) * 45
    fric_comp = (min(curr['port_friction'], 5) / 5) * 30
    risk_comp = (min(curr['sovereign_risk_entities'], 195) / 195) * 25
    
    # 5.5 Market Opening Escalation (Sunday Night Logic)
    market_panic = 0
    if datetime.now().hour >= 22:
        print("!! WARNING: Asian Market Opening approaching. Adding +5.0 volatility.")
        market_panic = 5.0
        
    stability_score = round(oil_comp + fric_comp + risk_comp + market_panic, 2)

    print(f">>> GLOBAL STABILITY INDEX: {stability_score} <<<\n")

    # 6. Map Generation
    at_risk_list = data_engine.get_at_risk_countries()
    SofieMapper().generate_risk_map(at_risk_list)
    
    friction_data = data_engine.get_port_friction_map()
    LogisticsMapper().generate_heatmap(friction_data)

    # 7. Dashboard & Logging
    SofieVisualizer().generate_risk_chart(stability_score, curr)
    record_history(stability_score, args.scenario)

    # 8. SitRep Summary
    print("="*55)
    print("--- SITREP SUMMARY: MARCH 22, 2026 ---")
    if stability_score > 75:
        print("STATUS: CRITICAL WATCH. Ultimatum expires in <36 hours.")
    else:
        print("STATUS: STABLE. No immediate kinetic escalation detected.")
    print("="*55)

if __name__ == "__main__":
    main()
