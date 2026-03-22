import sys
from src.data_pipeline.loaders import DataLoader
from src.core.risk_engine import SofieRiskEngine
from src.utils.visualizer import SofieVisualizer
from src.utils.briefing import SofieBriefing

def main(scenario_oil=None):
    print("--- SOFIE EVOLVED v2.0 | SCENARIO ANALYSIS ---")
    
    # 1. Load Real Data
    data = DataLoader(feed_date="2026-03-22").get_latest_nexus()
    
    # 2. APPLY SCENARIO (If you provided one)
    if scenario_oil:
        print(f"!! STRESS TEST: Overriding Oil Price to ${scenario_oil}")
        data['oil_price'] = float(scenario_oil)
    
    # 3. Run Synthesis
    engine = SofieRiskEngine(data)
    stability_score = engine.calculate_global_fragility()
    
    print(f"Scenario Global Stability Index: {stability_score}")

    # 4. Export Visuals & Briefing
    viz = SofieVisualizer()
    viz.generate_risk_chart(stability_score)
    
    brief = SofieBriefing()
    brief.generate_brief(stability_score, data)

if __name__ == "__main__":
    # If you type a number after the command, it uses it for Oil Price
    # Example: python -m main 150
    oil_input = sys.argv[1] if len(sys.argv) > 1 else None
    main(oil_input)
