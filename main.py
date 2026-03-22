from src.data_pipeline.loaders import DataLoader
from src.core.risk_engine import SofieRiskEngine
from src.utils.visualizer import SofieVisualizer
from src.utils.briefing import SofieBriefing 
from src.utils.alerts import SofieAlerts

def main():
    print("--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    
    # 1. Load Data
    data = DataLoader(feed_date="2026-03-22").get_latest_nexus()
    
    # 2. Run Engine
    engine = SofieRiskEngine(data)
    stability_score = engine.calculate_global_fragility()
    print(f"Current Global Stability Index: {stability_score}")

    # 3. Visuals & Reports
    viz = SofieVisualizer()
    viz.generate_risk_chart(stability_score)
    
    brief = SofieBriefing()
    brief.generate_brief(stability_score, data)
    
    # 4. Critical Alerts
    alerts = SofieAlerts()
    alerts.get_top_threats()

if __name__ == "__main__":
    main()
