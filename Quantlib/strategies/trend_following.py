"""
Trend Following strategy implementation
"""
from .base_strategy import BaseStrategy
import backtrader as bt

class TrendFollowing(BaseStrategy):
    params = (
        ('sma_period', 50),
        ('trade_size', 1.0),
    )

    def setup_indicators(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, 
            period=self.params.sma_period
        )

    def next(self):
        if not self.position and self.data.close > self.sma:
            self.execute_buy()
        elif self.position and self.data.close < self.sma:
            self.execute_sell()