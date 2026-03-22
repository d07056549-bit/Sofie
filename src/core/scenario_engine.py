class ScenarioEngine:
    def __init__(self):
        self.scenarios = {
            "peace": {
                "oil_price": 68.0, "gpr_index": 45.0, "port_friction": 1.0,
                "desc": "Strait of Hormuz reopened. Diplomacy successful."
            },
            "ultimatum_expires": {
                "oil_price": 145.0, "gpr_index": 550.0, "port_friction": 2.5,
                "desc": "48-hour deadline passed. Kinetic strikes initiated."
            },
            "blackout": {
                "oil_price": 190.0, "gpr_index": 800.0, "port_friction": 5.0,
                "desc": "Total regional conflict. Global energy severed."
            }
        }

    def apply(self, base_data, scenario_name):
        s = self.scenarios.get(scenario_name.lower())
        if not s:
            return base_data
        print(f"!! APPLYING SCENARIO: {scenario_name.upper()}")
        print(f"!! CONTEXT: {s['desc']}")
        updated = base_data.copy()
        updated.update({"oil_price": s["oil_price"], "gpr_index": s["gpr_index"], "port_friction": s["port_friction"]})
        return updated
