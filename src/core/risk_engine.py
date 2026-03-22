class SofieRiskEngine:
    def __init__(self, data):
        self.data = data

    def calculate_global_fragility(self):
        """Math to determine if the world is entering a Black Swan event."""
        # S^3 Formula: (Price Shock * Risk Index) + Shipping Friction
        oil_shock = (self.data['oil_price'] - 75) / 75
        friction = self.data['shipping_delay'] * 2
        
        # Stability Score (0 = Perfect, 100 = Total Collapse)
        score = (oil_shock * 40) + (self.data['gpr_index'] / 10) + (friction * 10)
        return round(score, 2)
