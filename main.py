import sys
from src.data_pipeline.loaders import DataLoader
from src.core.risk_engine import SofieRiskEngine

def main():
    print("--- SOFIE EVOLVED v2.0 | SYSTEM INITIALIZED ---")
    
    # 1. Load Data (March 22, 2026 Feed)
    data = DataLoader(feed_date="2026-03-22").get_latest_nexus()
    
    # 2. Run Synthesis
    engine = SofieRiskEngine(data)
    stability_score = engine.calculate_global_fragility()
    
    # 3. Output
    print(f"Current Global Stability Index: {stability_score}")

if __name__ == "__main__":
    main()
