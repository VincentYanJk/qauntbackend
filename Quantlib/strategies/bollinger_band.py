from Quantlib.indicators.bollinger import BollingerBands
import backtrader as bt

class BollingerBand(bt.Strategy):
    params = (("period", 20), ("devfactor", 2.0), ("trade_size", 1.0))

    def __init__(self):
        self.bb = BollingerBands(self.data.close, period=self.params.period, devfactor=self.params.devfactor)

    def next(self):
        if not self.position and self.data.close < self.bb.lines.bot:
            self.buy(size=self.params.trade_size)
        elif self.position and self.data.close > self.bb.lines.top:
            self.sell(size=self.params.trade_size)