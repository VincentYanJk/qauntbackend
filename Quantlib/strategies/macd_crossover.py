"""
MACD Crossover strategy implementation
"""
from .base_strategy import BaseStrategy
from Quantlib.indicators.macd import MACD
import backtrader as bt

class MACDCrossover(BaseStrategy):
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
        ('trade_size', 1.0),
    )

    def setup_indicators(self):
        self.macd = MACD(
            self.data.close,
            fast=self.params.fast_period,
            slow=self.params.slow_period,
            signal_period=self.params.signal_period
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if self.crossover > 0:
            self.execute_buy()
        elif self.crossover < 0:
            self.execute_sell()