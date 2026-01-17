class PortfolioState:
    def __init__(self, initial_value=10000, base_currency="USDT"):
        self.total_value = initial_value
        self.base_currency = base_currency
        self.balances = {base_currency: float(initial_value)}
        self.positions = {} # {symbol: quantity}

    def update_balance(self, asset, amount):
        self.balances[asset] = self.balances.get(asset, 0.0) + amount

    def update_position(self, symbol, quantity):
        self.positions[symbol] = self.positions.get(symbol, 0.0) + quantity

    def get_total_value(self, market_prices):
        value = self.balances.get(self.base_currency, 0.0)
        for symbol, qty in self.positions.items():
            price = market_prices.get(symbol, 0.0)
            value += qty * price
        self.total_value = value
        return value
