import os

class SofieBriefing:
    def __init__(self, output_path="exports/"):
        self.output_path = output_path

    def generate_brief(self, score, data):
        """Writes a professional Situation Report (SITREP)."""
        brief = f"""
--- SOFIE INTELLIGENCE BRIEF | MARCH 22, 2026 ---
GLOBAL FRAGILITY INDEX: {score}/100

SITUATION SUMMARY:
The world has entered a 'Flashpoint Zone' as of this Sunday morning. 
The 48-hour ultimatum regarding the Strait of Hormuz is the primary 
driver of systemic instability.

KEY DATA POINTS:
- FINANCIAL: {data['sovereign_risk_entities']} nations are at high risk of debt default.
- ENERGY: Oil prices are averaging ${data['oil_price']}, a 49% increase from baseline.
- LOGISTICS: Port friction is {data['port_friction']:.2f}x above normal levels.

VERDICT:
The 77.71 score suggests that while the system is fracturing, a total 
global collapse is currently being held back by emergency IEA reserve 
releases (400mb). However, if the 48-hour deadline expires without 
de-escalation, we project a jump to 85.0+.
"""
        file_path = os.path.join(self.output_path, "daily_briefing_march_22.txt")
        with open(file_path, "w") as f:
            f.write(brief)
        print(f"-> Briefing Exported: {file_path}")
