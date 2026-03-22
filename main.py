from src.data_pipeline.loaders import DataLoader
from src.core.risk_engine import SofieRiskEngine
from src.utils.visualizer import SofieVisualizer
from src.utils.briefing import SofieBriefing
from src.utils.alerts import SofieAlerts # <-- NEW

def main():
    print("--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    
    # 1. Load & Process
    data = DataLoader(feed_date="2026-03-22").get_latest_nexus()
    engine = SofieRiskEngine(data)
    stability_score = engine.calculate_global_fragility()
    
    # 2. Results
    print(f"Current Global Stability Index: {stability_score}")

    # 3. Visuals & Briefings
    SofieVisualizer().generate_risk_chart(stability_score)
    SofieBriefing().generate_brief(stability_score, data)
    
    # 4. Critical Alerts (NEW)
    SofieAlerts().get_top_threats()

if __name__ == "__main__":
    main()
