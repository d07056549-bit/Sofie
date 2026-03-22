import argparse
import os
from datetime import datetime
import pandas as pd
from src.utils.data_processor import SofieDataEngine
from src.utils.visualizer import SofieVisualizer

def main():
    parser = argparse.ArgumentParser(description="SOFIE: Strategic Operations & Fragility Intelligence Engine")
    parser.add_argument('--scenario', type=str, default='baseline', help='Target scenario: baseline, peace, blackout')
    args = parser.parse_args()

    # 1. System Initialization
    print("=======================================================")
    print("--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    print(f"DATE: March 22, 2026 | TIME: {datetime.now().strftime('%H:%M')} GMT")
    print("=======================================================")

    engine = SofieDataEngine()
    viz = SofieVisualizer()

    # 2. Live Data Sensing (The run_all handshake)
    live_stats = engine.run_all()

    # 3. Scenario Matrix
    scenarios = {
        'peace': {
            'oil_price': 72.0,
            'port_friction': 1.0,
            'sovereign_risk_entities': 12
        },
        'baseline': {
            'oil_price': 94.50,
            'port_friction': live_stats['friction'],
            'sovereign_risk_entities': 45
        },
        'ultimatum_expires': {
            'oil_price': 145.0,
            'port_friction': 3.5,
            'sovereign_risk_entities': 110
        }
    }

    # 4. Stability Index Calculation Logic
    curr = scenarios.get(args.scenario, scenarios['baseline'])
    
    # Normalized components (0-100 scale)
    oil_comp = (min(curr['oil_price'], 200) / 200) * 45
    fric_comp = (min(curr['port_friction'], 5) / 5) * 30
    risk_comp = (min(curr['sovereign_risk_entities'], 195) / 195) * 25
    
    # 5. Black Swan Logic (Handshake with Data Engine)
    # Using .get() for robustness against KeyErrors
    black_swan_multiplier = 1.0
    if live_stats.get('black_swan_active', False):
        severity = live_stats.get('swan_intensity', 0)
        # Each severity unit adds 20% systemic risk
        black_swan_multiplier = 1.0 + (severity * 0.2)
        print(f"!!! BLACK SWAN DETECTED: Digital Infrastructure compromised. Multiplier: {black_swan_multiplier}x")

    # 6. Time-Based Escalation (The 22:00 GMT Rule)
    market_panic = 0
    if datetime.now().hour >= 22:
        market_panic = 5.0
        # This reflects the Asian Market Open volatility on Sunday night
    
    # Final Composite Score
    stability_score = round((oil_comp + fric_comp + risk_comp + market_panic) * black_swan_multiplier, 2)
    stability_score = min(stability_score, 100.0) if black_swan_multiplier == 1.0 else stability_score

    # 7. Persistence (Stability History)
    history_file = "stability_history.csv"
    new_entry = pd.DataFrame([{
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'Scenario': args.scenario,
        'Score': stability_score
    }])
    new_entry.to_csv(history_file, mode='a', header=not os.path.exists(history_file), index=False)

    # 8. Visual Export
    viz.generate_risk_chart(stability_score, live_stats)
    
    # 9. SITREP Summary
    status = "STABLE"
    if stability_score > 50: status = "ELEVATED"
    if stability_score > 75: status = "CRITICAL WATCH"
    
    print(f"-> Geographic Heatmap Exported: exports/risk_map_march_22.png")
    print(f"-> Logistics Heatmap Exported: exports/logistics_heatmap_march_22.png")
    print(f"-> Multi-Panel Intelligence Dashboard Exported: exports/stability_report_march_22.png")
    print("=======================================================")
    print(f"--- SITREP SUMMARY: MARCH 22, 2026 ---")
    print(f"STATUS: {status}. Stability Index: {stability_score}")
    if status == "CRITICAL WATCH":
        print("ALERT: Ultimatum expires in <36 hours. Prepare for secondary shocks.")
    print("=======================================================")

if __name__ == "__main__":
    main()
