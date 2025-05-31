from Quantlib.indicators.rsi import RSI
import backtrader as bt

class RSIReversion(bt.Strategy):
    params = (("period", 14), ("oversold", 30), ("overbought", 70), ("trade_size", 1.0))

    def __init__(self):
        self.rsi = RSI(self.data.close, period=self.params.period)

    def next(self):
        if not self.position and self.rsi < self.params.oversold:
            self.buy(size=self.params.trade_size)
        elif self.position and self.rsi > self.params.overbought:
            self.sell(size=self.params.trade_size)