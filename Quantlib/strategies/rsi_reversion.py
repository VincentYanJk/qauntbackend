"""
RSI Mean Reversion strategy implementation
"""
from .base_strategy import BaseStrategy
from Quantlib.indicators.rsi import RSI

class RSIReversion(BaseStrategy):
    params = (
        ('period', 14),
        ('oversold', 30),
        ('overbought', 70),
        ('trade_size', 1.0)
    )

    def setup_indicators(self):
        self.rsi = RSI(self.data.close, period=self.params.period)

    def next(self):
        if not self.position and self.rsi < self.params.oversold:
            self.execute_buy()
        elif self.position and self.rsi > self.params.overbought:
            self.execute_sell()