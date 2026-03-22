import math

class SofieRiskEngine:
    def __init__(self, data):
        self.data = data

    def calculate_global_fragility(self):
        # 1. Energy Weight (30 pts max)
        oil_shock = (self.data['oil_price'] - 75) / 75 * 30
        
        # 2. Geopolitical Weight (30 pts max)
        gpr_weight = (self.data['gpr_index'] / 500) * 30
        
        # 3. Financial Weight (40 pts max)
        entities = self.data['sovereign_risk_entities']
        financial_weight = math.log10(entities + 1) * 20 

        # 4. The Friction Multiplier (Port Performance)
        # If ports are 1.5x slower, the total risk is amplified by 15%
        friction_bonus = (self.data['port_friction'] - 1.0) * 10

        total_score = oil_shock + gpr_weight + financial_weight + friction_bonus
        
        return round(min(total_score, 100.0), 2)
