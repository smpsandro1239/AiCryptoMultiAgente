class PortfolioState:
    def __init__(self, initial_value=10000, name="Default"):
        self.name = name
        self.total_value = initial_value
        self.positions = {}

class MultiPortfolioManager:
    """
    Gere múltiplos portfólios ou sub-contas.
    """
    def __init__(self):
        self.portfolios = {"Default": PortfolioState()}

    def add_portfolio(self, name: str, initial_value: float):
        self.portfolios[name] = PortfolioState(initial_value, name)

    def get_portfolio(self, name: str) -> PortfolioState:
        return self.portfolios.get(name)

    def get_all_value(self) -> float:
        return sum(p.total_value for p in self.portfolios.values())
