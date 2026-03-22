import math

class SofieRiskEngine:
    def __init__(self, data):
        self.data = data

    def calculate_global_fragility(self):
        # Calculate weights
        oil_shock = (self.data['oil_price'] - 75) / 75 * 30
        gpr_weight = (self.data['gpr_index'] / 500) * 30
        
        entities = self.data['sovereign_risk_entities']
        financial_weight = math.log10(entities + 1) * 20 

        # Add the Friction Bonus
        friction_val = self.data.get('port_friction', 1.0) # Uses 1.0 if missing
        friction_bonus = (friction_val - 1.0) * 10

        total_score = oil_shock + gpr_weight + financial_weight + friction_bonus
        return round(min(total_score, 100.0), 2)
