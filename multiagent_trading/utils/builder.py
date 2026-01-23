import json
import os

class StrategyBuilder:
    """
    Permite a criação programática e visual de ficheiros de configuração de estratégias.
    """
    def __init__(self, strategies_dir: str = "strategies"):
        self.strategies_dir = strategies_dir

    def create_strategy(self, name: str, agent_list: list):
        """
        Gera um ficheiro JSON com a configuração do ensemble de agentes.
        """
        strategy_config = {
            "strategy_name": name,
            "version": "1.0",
            "agents": agent_list
        }

        filepath = os.path.join(self.strategies_dir, f"{name}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(strategy_config, f, indent=4)

        return filepath

    def get_agent_template(self, agent_class_name: str, config: dict = None):
        """Retorna uma estrutura base para um agente."""
        return {
            "class": agent_class_name,
            "name": f"Agent_{agent_class_name}",
            "config": config or {}
        }
