import unittest
import numpy as np
from multiagent_trading.indicators.ema import calculate_ema
from multiagent_trading.indicators.rsi import calculate_rsi

class TestIndicators(unittest.TestCase):
    def test_ema(self):
        prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        ema = calculate_ema(prices, period=5)
        self.assertIsNotNone(ema)
        self.assertEqual(len(ema), len(prices))

    def test_rsi(self):
        prices = [10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10]
        rsi = calculate_rsi(prices, period=5)
        self.assertIsNotNone(rsi)
        self.assertEqual(len(rsi), len(prices))

if __name__ == "__main__":
    unittest.main()
