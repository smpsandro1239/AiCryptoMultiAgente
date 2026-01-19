import json
import os
from typing import List, Dict

class StrategyManager:
    """
    Gere configurações de ensembles de agentes (estratégias) guardadas em ficheiros JSON.
    """
    def __init__(self, strategies_dir: str = "strategies"):
        self.strategies_dir = strategies_dir
        if not os.path.exists(self.strategies_dir):
            os.makedirs(self.strategies_dir)

    def save_strategy(self, name: str, agent_configs: List[Dict]):
        filepath = os.path.join(self.strategies_dir, f"{name}.json")
        with open(filepath, 'w') as f:
            json.dump(agent_configs, f, indent=4)

    def load_strategy(self, name: str) -> List[Dict]:
        filepath = os.path.join(self.strategies_dir, f"{name}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Estratégia '{name}' não encontrada.")

        with open(filepath, 'r') as f:
            return json.load(f)

    def list_strategies(self) -> List[str]:
        return [f.replace(".json", "") for f in os.listdir(self.strategies_dir) if f.endswith(".json")]
