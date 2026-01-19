import numpy as np

class PortfolioStressTester:
    """
    Testa o portfólio contra cenários históricos extremos e choques de mercado.
    """
    @staticmethod
    def apply_shock(portfolio_value, shock_pct):
        """Aplica um choque percentual ao valor total do portfólio."""
        return portfolio_value * (1 + shock_pct)

    @staticmethod
    def simulate_scenarios(portfolio_value):
        """Simula cenários pré-definidos de stress."""
        scenarios = {
            "Crash 2008 (Lehman)": -0.20,
            "COVID-19 (Março 2020)": -0.15,
            "Flash Crash": -0.10,
            "Black Monday 1987": -0.22,
            "Cenário Bull Extremo": 0.10
        }

        results = {}
        for name, shock in scenarios.items():
            results[name] = PortfolioStressTester.apply_shock(portfolio_value, shock)

        return results
