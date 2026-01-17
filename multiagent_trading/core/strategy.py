import json
import os

class StrategyManager:
    """
    Manages trading strategies, which are ensembles of agents and their configurations.
    """
    def __init__(self, strategies_dir="strategies"):
        self.strategies_dir = strategies_dir
        if not os.path.exists(strategies_dir):
            os.makedirs(strategies_dir)
        self.strategies = self.load_all_strategies()

    def load_all_strategies(self):
        strategies = {}
        for filename in os.listdir(self.strategies_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.strategies_dir, filename), "r") as f:
                    strategy_name = filename[:-5]
                    strategies[strategy_name] = json.load(f)
        return strategies

    def save_strategy(self, name, agent_configs):
        path = os.path.join(self.strategies_dir, f"{name}.json")
        with open(path, "w") as f:
            json.dump(agent_configs, f, indent=4)
        self.strategies[name] = agent_configs

    def get_strategy(self, name):
        return self.strategies.get(name)

    def list_strategies(self):
        return list(self.strategies.keys())
