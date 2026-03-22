class SofieRiskEngine:
    def __init__(self, data):
        self.data = data

    def calculate_global_fragility(self):
        """
        The 2026 Fragility Formula:
        High Score = High Risk.
        """
        # 1. Energy Shock (How much higher than 'normal' $75 oil?)
        oil_impact = (self.data['oil_price'] - 75) / 75 * 30
        
        # 2. Geopolitical Tension (GPR Index / 10)
        tension_impact = self.data['gpr_index'] / 10
        
        # 3. Financial Contagion (Number of 'B/C' rated countries * 1.5)
        # This is the "Sovereign Risk" weight
        contagion_impact = self.data['sovereign_risk_entities'] * 1.5
        
        # Total Score
        final_score = oil_impact + tension_impact + contagion_impact
        
        # Return as a clean number out of 100 (capped)
        return min(round(final_score, 2), 100.0)
