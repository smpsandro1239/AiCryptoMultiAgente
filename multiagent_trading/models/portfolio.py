class PortfolioState:
    def __init__(self, initial_value=10000):
        self.total_value = initial_value
        self.positions = {}
