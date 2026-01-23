class PortfolioState:
    def __init__(self, initial_value=10000, name="Default", base_currency="USD"):
        self.name = name
        self.total_value = initial_value
        self.base_currency = base_currency
        self.balances = {base_currency: initial_value} # Suporte multi-moeda
        self.positions = {}

    def update_balance(self, currency: str, amount: float):
        """Atualiza o saldo de uma moeda específica."""
        if currency not in self.balances:
            self.balances[currency] = 0.0
        self.balances[currency] += amount

    def get_balance(self, currency: str) -> float:
        return self.balances.get(currency, 0.0)

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
