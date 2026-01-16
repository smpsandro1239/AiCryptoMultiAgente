import unittest
import numpy as np
from multiagent_trading.indicators.ema import ema
from multiagent_trading.indicators.rsi import rsi

class TestIndicators(unittest.TestCase):
    def test_ema(self):
        data = [10, 10, 10, 10, 10]
        result = ema(data, 3)
        self.assertEqual(len(result), 5)
        self.assertTrue(np.isnan(result[0]))
        self.assertEqual(result[-1], 10.0)

    def test_rsi(self):
        data = [10, 12, 14, 13, 15, 17, 18, 20, 19, 21, 23, 22, 24, 26, 25]
        result = rsi(data, 14)
        self.assertEqual(len(result), 15)
        self.assertFalse(np.isnan(result[-1]))

if __name__ == "__main__":
    unittest.main()
