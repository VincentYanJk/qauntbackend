"""
Bollinger Bands strategy implementation
"""
from .base_strategy import BaseStrategy
from Quantlib.indicators.bollinger import BollingerBands

class BollingerBand(BaseStrategy):
    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('trade_size', 1.0)
    )

    def setup_indicators(self):
        self.bb = BollingerBands(
            self.data.close, 
            period=self.params.period, 
            devfactor=self.params.devfactor
        )

    def next(self):
        if not self.position and self.data.close < self.bb.lines.bot:
            self.execute_buy()
        elif self.position and self.data.close > self.bb.lines.top:
            self.execute_sell()