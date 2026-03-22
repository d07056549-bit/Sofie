class ScenarioEngine:
    def __init__(self):
        self.scenarios = {
            "peace": {
                "oil_price": 68.0,
                "gpr_index": 45.0,
                "port_friction": 1.0,
                "desc": "Strait of Hormuz reopened. Sanctions eased."
            },
            "ultimatum_expires": {
                "oil_price": 145.0,
                "gpr_index": 550.0,
                "port_friction": 2.5,
                "desc": "48-hour deadline passed. Kinetic strikes on Iranian infrastructure begun."
            },
            "blackout": {
                "oil_price": 190.0,
                "gpr_index": 800.0,
                "port_friction": 5.0,
                "desc": "Total regional conflict. Global energy supply chain severed."
            }
        }

    def apply(self, base_data, scenario_name):
        if scenario_name not in self.scenarios:
            print(f"!! Unknown scenario '{scenario_name}'. Using live data.")
            return base_data
        
        s = self.scenarios[scenario_name]
        print(f"-> Applying Scenario: {scenario_name.upper()}")
        print(f"-> Context: {s['desc']}")
        
        # Override baseline data with scenario values
        updated_data = base_data.copy()
        updated_data.update({
            "oil_price": s["oil_price"],
            "gpr_index": s["gpr_index"],
            "port_friction": s["port_friction"]
        })
        return updated_data
