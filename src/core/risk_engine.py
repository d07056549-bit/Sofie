import math

class SofieRiskEngine:
    def __init__(self, data):
        self.data = data

    def calculate_global_fragility(self):
        """
        Refined 2026 Stress Formula:
        Balances Oil Shocks, Geopolitical Tension, and Financial Contagion.
        """
        # 1. Energy Pressure (Weighted at 30% of the total)
        # Oil at $112 is a 49% increase over the $75 baseline.
        oil_base = 75.0
        oil_shock = (self.data['oil_price'] - oil_base) / oil_base
        energy_weight = oil_shock * 30 

        # 2. Geopolitical Tension (Weighted at 30% of the total)
        # 385 GPR is high, but we normalize it against a "Crisis" level of 500.
        gpr_normalized = (self.data['gpr_index'] / 500) * 30

        # 3. Financial Contagion (The 96 Countries)
        # Instead of 1.5x each, we use a 'Logarithmic' scale. 
        # The more countries at risk, the higher the score, but it slows down 
        # so it doesn't break the 100 limit immediately.
        entities = self.data['sovereign_risk_entities']
        # Log logic: 96 entities will result in a weight of ~40 points.
        financial_weight = math.log10(entities + 1) * 20 

        # 4. Summing the Pillars
        raw_score = energy_weight + gpr_normalized + financial_weight
        
        # FINAL SCORE (Capped at 100, but harder to reach)
        return round(min(raw_score, 100.0), 2)
