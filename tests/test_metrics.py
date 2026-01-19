import unittest
import numpy as np
from multiagent_trading.analytics.metrics import calculate_sharpe_ratio, calculate_max_drawdown

class TestMetrics(unittest.TestCase):
    def test_sharpe_ratio(self):
        returns = [0.01, 0.02, -0.01, 0.03, 0.01]
        sharpe = calculate_sharpe_ratio(returns)
        self.assertGreater(sharpe, 0)

    def test_max_drawdown(self):
        values = [100, 110, 105, 115, 90, 95]
        mdd = calculate_max_drawdown(values)
        self.assertLess(mdd, 0)
        self.assertAlmostEqual(mdd, (90-115)/115)

if __name__ == "__main__":
    unittest.main()
