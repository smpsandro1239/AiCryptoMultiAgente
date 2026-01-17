import unittest
import numpy as np
from multiagent_trading.indicators.ema import ema
from multiagent_trading.indicators.rsi import rsi
from multiagent_trading.indicators.macd import macd
from multiagent_trading.indicators.bollinger_bands import bollinger_bands

class TestIndicators(unittest.TestCase):
    def test_ema(self):
        data = [10, 10, 10, 10, 10]
        result = ema(data, 3)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[-1], 10.0)

    def test_rsi(self):
        data = [10, 12, 14, 13, 15, 17, 18, 20, 19, 21, 23, 22, 24, 26, 25]
        result = rsi(data, 14)
        self.assertEqual(len(result), 15)
        self.assertFalse(np.isnan(result[-1]))

    def test_macd(self):
        data = np.linspace(100, 200, 50).tolist()
        macd_line, signal_line, hist = macd(data)
        self.assertEqual(len(macd_line), 50)
        self.assertFalse(np.isnan(macd_line[-1]))

    def test_bollinger_bands(self):
        data = [100] * 30
        upper, middle, lower = bollinger_bands(data, period=20)
        self.assertEqual(len(upper), 30)
        self.assertEqual(middle[-1], 100.0)
        self.assertEqual(upper[-1], 100.0)

if __name__ == "__main__":
    unittest.main()
